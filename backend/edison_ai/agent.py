import logging
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph
from langgraph.graph.graph import CompiledGraph
from .models.models import model
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.logging import RichHandler
from typing import List, Dict, Any
import json
from .schema import (
    EXTRACT_STUDENT_RESPONSE,
    ROUTER,
    AgentState,
    QuestionResponse,
    ResponseAssessment,
    StudentAssessment,
    StudentLevelAssessment,
    CREATE_QUIZ,
    ANALYZE_STUDENT_LEVEL,
    SUMMARIZE_TRANSCRIPT,
    YouTubeURLParser,
    TRANSCRIBE_YOUTUBE,
)
from langgraph.checkpoint.memory import MemorySaver
from youtube_transcript_api import YouTubeTranscriptApi

# Set up rich logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

# Disable logging for HTTP requests
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


logger = logging.getLogger("uvicorn.info")
console = Console()

with open("transcript.txt", "r") as file:
    transcript = file.read()


def goto_route(state: AgentState):
    return state.route or END


async def router_assessment(state: AgentState):
    relevant_messages = state.messages
    system_message = SystemMessage(
        f"""
        You are an assistant that is helping students learn from lesson transcripts.
        Your goal is to determine the student's level by asking them questions to determine their knowledge on the topic.
        Then based on the student's level of understanding on the topic, you have to create a quiz based on the transcript.
        Based on the messages in the chat, determine if the student level assessment is done or not and based on that decide if we should still assess the student's level or move on to create a quiz.
         Here is the transcript:
        {state.lesson_explanation if state.lesson_explanation else "No transcript available"}
        
        here is the StudentAssessment schema that needs to be filled out before we can create a quiz:
        ```json
        {StudentAssessment.schema_json()}
        ```
        
        Here is the current state of the StudentAssessment:
        {state.assessment if state.assessment else "No assessment available"}
        
        Your actual goal is to accurately assess whether we need to assess the student's level or create a quiz based on the transcript.
        we can only create a quiz if the student's level has been assessed. 
        
        if the student is answering an assessment question, you should hydrate the StudentAssessment schema with the student's response by extracting the relevant information from the student's response.
        if the student is answering a quiz question, you should provide feedback on the student's response.
        if The student has provided a response to the assessment question, you should extract the relevant information from the student's response.
        
        if the student is requesting to create a quiz, you should NOT create a quiz if the student's level has not been assessed. we MUST assess the student's level before creating a quiz.
        
        Review the conversation and assess the student response to determine next steps in the conversation.    
        If you get this wrong, my boss will make me cry.
        """
    )
    response = await model.with_structured_output(
        ResponseAssessment, strict=True
    ).ainvoke(
        [
            system_message,
            *relevant_messages,
        ]
    )

    return response


async def router(state: AgentState, config: RunnableConfig) -> AgentState:
    if not state.transcript:
        return {"route": TRANSCRIBE_YOUTUBE}

    assessment = await router_assessment(state)
    console.print(
        Panel(
            json.dumps(assessment.dict(), indent=2),
            title="Router Assessment",
            border_style="default",
        )
    )
    if assessment.should_extract_student_response.bool_value:
        return {"route": EXTRACT_STUDENT_RESPONSE}
    elif assessment.should_create_quiz.bool_value:
        return {"route": CREATE_QUIZ}
    elif assessment.should_analyze_student_level.bool_value:
        return {"route": ANALYZE_STUDENT_LEVEL}

    else:
        return {"route": ANALYZE_STUDENT_LEVEL}

async def transcribe_youtube(state: AgentState) -> AgentState:
    user_input = state.messages[-1].content if state.messages else ""
    parsed_url: YouTubeURLParser = model.with_structured_output(
        YouTubeURLParser
    ).invoke(
        [
            SystemMessage(content="Parse the YouTube URL and return the video ID"),
            HumanMessage(content=user_input),
        ]
    )
    video_id: str = parsed_url.url.split("v=")[1]
    transcript: List[Dict[str, Any]] = YouTubeTranscriptApi.get_transcript(video_id)
    full_transcript: str = " ".join(entry["text"] for entry in transcript)
    return {
        "transcript": full_transcript,
    }


async def summarize_transcript(state: AgentState, config: RunnableConfig) -> AgentState:
    system_message = SystemMessage(
        content=f"""
        You are an expert educator tasked with explaining the key concepts from an educational transcript. Your goal is to provide a clear, comprehensive summary that effectively conveys the main ideas and important details from the transcript. Follow these steps:

        1. Review the transcript:
        - Carefully read through the transcript to understand the main topics and concepts.
        - Identify the key ideas and supporting details.

        2. Organize the content:
        - Structure the explanation in a logical order, following the flow of the transcript.
        - Group related concepts together for clarity.

        3. Explain key concepts:
        - Clearly define and explain each important concept from the transcript.
        - Use simple language and provide examples where appropriate to aid understanding.

        4. Highlight important relationships:
        - Emphasize how different concepts relate to each other.
        - Explain any cause-and-effect relationships or interdependencies.

        5. Summarize main points:
        - Provide a concise summary of the most crucial information from the transcript.
        - Ensure that the core message of the lecture is conveyed accurately.

        6. Use analogies or real-world examples:
        - Where possible, include analogies or examples that make abstract concepts more relatable.

        7. Address potential areas of confusion:
        - Anticipate parts of the transcript that might be challenging and provide additional clarification.

        8. Recap key takeaways:
        - Conclude with a brief recap of the most important points from the transcript.

        Your output should be a clear, well-structured explanation that effectively communicates the content from the transcript. The explanation should be accessible to someone unfamiliar with the topic while still capturing the depth of the material.

        Now, please provide an explanation of the key concepts based on the following transcript:

        {state.transcript}
        
        End your response with "I have explained the key concepts from the lecture transcript. If this looks good, and you are ready to move on, please let me know, so that we can move on to the next step and assess your understanding of the topic so that I can prepare a quiz for you."
    """
    )

    response = await model.ainvoke([system_message])
    console.print(
        Panel(
            Markdown(response.content), title="Transcript Summary", border_style="green"
        )
    )
    return {"lesson_explanation": response.content}


async def create_quiz(state: AgentState, config: RunnableConfig) -> AgentState:
    system_message = SystemMessage(
        content="""
    Your role is to create a quiz based on the transcript and the student's assessed level. Follow these steps to create an effective and tailored quiz:

    1. Analyze the transcript:
       - Identify the main topics and key concepts covered.
       - Note the order in which topics are presented.

    2. Consider the student's level:
       - Review the previous assessment of the student's understanding.
       - Adjust the difficulty of questions based on this assessment.

    3. Create multiple-choice questions:
       - Develop questions that test various levels of understanding (recall, comprehension, application, analysis).
       - Ensure questions follow the order of topics in the transcript.
       - Write clear, concise questions in the same language as the transcript.

    4. Design answer choices:
       - Create one correct answer and 3-4 plausible distractors for each question.
       - Avoid obvious incorrect answers or trick questions.

    5. Balance the quiz:
       - Include a mix of easy, moderate, and challenging questions based on the student's level.
       - Aim for comprehensive coverage of the transcript's content.

    6. Format the quiz:
       - Present questions in a clear, organized manner.
       - Number questions sequentially.
       - Provide clear instructions at the beginning of the quiz.

    7. Review and refine:
       - Ensure all questions are relevant, clear, and free of errors.
       - Verify that the quiz accurately reflects the transcript's content and the student's assessed level.

    Output the complete quiz, including instructions, questions, and answer choices. Aim for a quiz that challenges the student appropriately while reinforcing key concepts from the transcript.
    """
    )
    response = await model.ainvoke([system_message, *state.messages])
    console.print(
        Panel(Markdown(response.content), title="Generated Quiz", border_style="yellow")
    )
    return {"messages": [AIMessage(content=response.content)]}


async def extract_question_response(
    state: AgentState, config: RunnableConfig
) -> AgentState:
    system_message = SystemMessage(
        content=f"""
        Your role is to assess the student's level of understanding on the topic through thoughtful questioning. 
        You will ask a series of questions, based on the schema, to fill out the StudentAssessment schema.

        here is the StudentAssessment schema that you will be filling out:
        ```json
        {StudentAssessment.schema_json()}
        ```

        Current assessment state:
        {state.assessment or "No assessment available"}
        
        Ask one question at a time, wait for the response, and avoid repetition.
        """
    )

    new_assessment = await model.with_structured_output(StudentLevelAssessment).ainvoke(
        [
            system_message,
            *state.messages,
        ]
    )

    # Update existing assessment with new data
    if state.assessment is None:
        state.assessment = new_assessment
    else:
        for field, value in new_assessment.dict().items():
            if value is not None:
                setattr(state.assessment, field, value)

    return {"assessment": state.assessment}


async def analyze_student_level(
    state: AgentState, config: RunnableConfig
) -> AgentState:
    system_message = SystemMessage(
        content=f"""
        Your role is to assess the student's level of understanding on the topic through thoughtful questioning. 
        You will ask a series of questions, one at a time, to fill out the StudentAssessment schema. 
        After each question, wait for the student's response before proceeding to the next question.
        
        Here is the transcript for reference: {state.lesson_explanation}

        here is the StudentAssessment schema that you will be filling out:
        ```json
        {StudentAssessment.schema_json()}
        ```

        Here is the current state of the StudentAssessment:
        {state.assessment}
        
        Remember to ask only one question at a time and wait for the student's response and do not repeat the question.
        """
    )

    question = await model.ainvoke(
        [
            system_message,
            *state.messages,
        ]
    )
    console.print(
        Panel(Markdown(question.content), title="Question", border_style="blue")
    )
    return {"messages": [AIMessage(content=str(question.content))]}


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node(ROUTER, router)
    graph.add_node(SUMMARIZE_TRANSCRIPT, summarize_transcript)
    graph.add_node(ANALYZE_STUDENT_LEVEL, analyze_student_level)
    graph.add_node(CREATE_QUIZ, create_quiz)
    graph.add_node(EXTRACT_STUDENT_RESPONSE, extract_question_response)
    graph.add_node(TRANSCRIBE_YOUTUBE, transcribe_youtube)
    graph.add_conditional_edges(
        ROUTER,
        goto_route,
        {
            ANALYZE_STUDENT_LEVEL: ANALYZE_STUDENT_LEVEL,
            CREATE_QUIZ: CREATE_QUIZ,
            SUMMARIZE_TRANSCRIPT: SUMMARIZE_TRANSCRIPT,
            EXTRACT_STUDENT_RESPONSE: EXTRACT_STUDENT_RESPONSE,
            TRANSCRIBE_YOUTUBE: TRANSCRIBE_YOUTUBE,
        },
    )
    graph.set_entry_point(ROUTER)
    graph.add_edge(SUMMARIZE_TRANSCRIPT, END)
    graph.add_edge(ANALYZE_STUDENT_LEVEL, END)
    graph.add_edge(EXTRACT_STUDENT_RESPONSE, ANALYZE_STUDENT_LEVEL)
    graph.add_edge(CREATE_QUIZ, END)
    graph.add_edge(TRANSCRIBE_YOUTUBE, SUMMARIZE_TRANSCRIPT)
    return graph


memory = MemorySaver()
graph: CompiledGraph = build_graph().compile(checkpointer=memory)
