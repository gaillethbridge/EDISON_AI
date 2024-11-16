"use client";

import { useCoAgent, useCoAgentStateRender, useCopilotChat } from "@copilotkit/react-core";
import { CopilotPopup } from "@copilotkit/react-ui";
import { TextMessage, MessageRole } from "@copilotkit/runtime-client-gql";
import { CopilotChat } from "@copilotkit/react-ui";
import { Progress } from "./components/ui/Progress";
import { AgentState } from "./lib/types";
import { TextDisplay } from "./components/ui/TextDisplay";
import { Quiz } from "./components/ui/Quiz";


export function Main() {
  const {
    state: agentState,
  } = useCoAgent<AgentState>({
    name: "edison_ai",
    initialState: {
      messages: [{ content: "" }],
      quiz: `Quiz Questions:
What is the primary purpose of LangChain?

A) To replace GPT-4 with a new language model.
B) To enhance AI capabilities by integrating LLMs with external data and resources.
C) To provide a new programming language for AI development.
D) To create a standalone AI application without external data.
How does LangChain handle data for AI applications?

A) It stores data in a traditional database for easy access.
B) It divides data into smaller chunks and stores them as embeddings in a vector database.
C) It uses cloud storage to keep all data centralized.
D) It relies on the LLM's internal memory to manage data.
Which of the following is NOT a core component of LangChain?

A) LLM Wrappers
B) Prompt Templates
C) Neural Networks
D) Agents
What is the role of 'Chains' in LangChain?

A) To connect multiple LLMs together for enhanced performance.
B) To combine multiple components to solve tasks and build applications.
C) To encrypt data before storing it in a vector database.
D) To provide a user interface for AI applications.
In what way can LangChain be applied in the field of education?

A) By replacing teachers with AI models.
B) By enabling LLMs to reference entire syllabi to aid learning.
C) By creating educational games for students.
D) By developing new educational theories.
What is the significance of 'Agents' in LangChain?

A) They are used to store data securely.
B) They enable LLMs to interact with external APIs.
C) They provide a graphical interface for users.
D) They are responsible for training the LLMs.
Which programming languages are available for LangChain?

A) Java and C++
B) Python and TypeScript
C) Ruby and Swift
D) PHP and JavaScript
What is a practical example of using LangChain mentioned in the transcript?

A) Developing a new operating system.
B) Setting up LangChain to interact with LLMs and vector stores.
C) Creating a social media platform.
D) Designing a new AI language model.
Answers:
B
B
C
B
B
B
B
B`,
    },
  });

  useCoAgentStateRender({
    name: "edison_ai",
    render: ({ state, nodeName, status }) => {
      if (!state.logs || state.logs.length === 0) {
        return null;
      }
      return <Progress logs={state.logs} />;
    },
  });

  return (
    <div className="flex h-full w-full">
      {/* Main content area */}
      <div className="flex-grow flex flex-col">
        <div className="flex">
          <TextDisplay state={agentState} />
          {agentState.quiz && <Quiz quiz={agentState.quiz} />}
        </div>
      </div>

      {/* Right sidebar for chat */}
      <div className="w-96 border-l border-gray-200">
        <CopilotChat
          className="h-full"
          instructions={"You are assisting the user as best as you can. Answer in the best way possible given the data you have."}
          labels={{
            title: "Edison AI",
            initial: "Hi! 👋 Can you share the YouTube video you want to learn from?",
          }}
        />
      </div>
    </div>
  );
}
