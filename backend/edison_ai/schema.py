from typing import Annotated, List, Optional
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing import TypedDict

# Constants for different actions
SUMMARIZE_TRANSCRIPT = "summarize_transcript"
ANALYZE_STUDENT_LEVEL = "analyze_student_level"
CREATE_QUIZ = "create_quiz"
ROUTER = "router"
EXTRACT_STUDENT_RESPONSE = "extract_student_response"
TRANSCRIBE_YOUTUBE = "transcribe_youtube"

class QuestionResponse(BaseModel):
    question: str = Field(default="", description="The question posed to the student")
    response: str = Field(default="", description="The student's response to the question")
    analysis: str = Field(default="", description="Analysis of the student's response")

class StudentAssessment(BaseModel):
    knowledge_recall: QuestionResponse = Field(default_factory=QuestionResponse, description="Tests basic recall of facts from the lecture")
    comprehension: QuestionResponse = Field(default_factory=QuestionResponse, description="Tests understanding of concepts from the lecture")
    application: QuestionResponse = Field(default_factory=QuestionResponse, description="Tests ability to apply concepts to new situations")
    analysis: QuestionResponse = Field(default_factory=QuestionResponse, description="Tests ability to break down and examine relationships between concepts")
    synthesis: QuestionResponse = Field(default_factory=QuestionResponse, description="Tests ability to combine ideas to form new concepts")
    evaluation: QuestionResponse = Field(default_factory=QuestionResponse, description="Tests ability to make judgments about the value of ideas or materials")
    metacognitive: QuestionResponse = Field(default_factory=QuestionResponse, description="Questions about the student's own learning process and understanding")

class StudentLevelAssessment(BaseModel):
    assessment: StudentAssessment
    overall_level: str = Field(description="Overall assessment of the student's level based on their responses")
    strengths: List[str] = Field(description="Areas where the student showed strong understanding")
    areas_for_improvement: List[str] = Field(description="Areas where the student might benefit from additional study")

class BaseResponse(BaseModel):
    reason: str

class ShouldCreateQuiz(BaseResponse):
    bool_value: bool = Field(description="Whether to create a quiz based on the transcript and student's level. If the student level is not determined, this will always be false.")

class ShouldAnalyzeStudentLevel(BaseResponse):
    """
    Use this to analyze the student's level based on the responses from the student.
    """
    bool_value: bool = Field(description="Whether to analyze the student's level based on the responses from the student. If the student has provided responses to the questions you asked to analyze their level, This will be false.")
    
class ShouldExtractStudentResponse(BaseResponse):
    """
    Use this to extract the student's assessment response to the questions you asked to analyze their level.
    If the student has provided a response to the question for analyzing their level, you can use this to extract it.
    """
    bool_value: bool = Field(description="If the student has provided a response to the question for analyzing their level, this will be true.")
    
class ResponseAssessment(BaseModel):
    """
    Use this to classify the User's response, which is either an answer to one of your questions or a request to create a quiz or analyze the student's level.
    """
    should_create_quiz: ShouldCreateQuiz
    should_analyze_student_level: ShouldAnalyzeStudentLevel
    should_extract_student_response: ShouldExtractStudentResponse

class YouTubeURLParser(BaseModel):
    """
    Parse the YouTube URL from the user's input
    """
    url: str = Field(description="The YouTube URL to parse")

class Log(TypedDict):
    """
    Represents a log of an action performed by the agent.
    """
    message: str
    done: bool
    
class AgentState(BaseModel):
    messages: Annotated[List[AnyMessage], add_messages] = Field(default_factory=list)
    route: Optional[str] = Field(default=None)
    assessment: Optional[StudentLevelAssessment] = Field(default=None)
    lesson_explanation: Optional[str] = Field(default=None)
    logs: List[Log] = Field(default_factory=list)
    transcript: Optional[str] = Field(default=None)
    quiz: Optional[str] = Field(default=None)

class QuizAnswer(BaseModel):
    text: str = Field(description="The answer text")
    is_correct: bool = Field(description="Whether this is the correct answer")
    explanation: Optional[str] = Field(default=None, description="Explanation for why this answer is correct or incorrect")

class QuizQuestion(BaseModel):
    question: str = Field(description="The question text")
    answers: List[QuizAnswer] = Field(description="List of possible answers")
    difficulty: str = Field(description="Difficulty level of the question (easy, moderate, or challenging)")
    topic: str = Field(description="The main topic this question covers")
    skill_tested: str = Field(description="The type of skill being tested (recall, comprehension, application, etc.)")

class Quiz(BaseModel):
    title: str = Field(description="Title of the quiz")
    description: str = Field(description="Brief description of the quiz content")
    instructions: str = Field(description="Instructions for taking the quiz")
    questions: List[QuizQuestion] = Field(description="List of quiz questions")
    difficulty_level: str = Field(description="Overall difficulty level of the quiz")
    target_skills: List[str] = Field(description="List of skills being tested in this quiz")