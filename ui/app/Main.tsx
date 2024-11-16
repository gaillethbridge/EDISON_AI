"use client";

import { useCoAgent, useCoAgentStateRender, useCopilotChat } from "@copilotkit/react-core";
import { CopilotPopup } from "@copilotkit/react-ui";
import { TextMessage, MessageRole } from "@copilotkit/runtime-client-gql";
import { CopilotChat } from "@copilotkit/react-ui";
import { Progress } from "./components/ui/Progress";
import { AgentState } from "./lib/types";
import { TextDisplay } from "./components/ui/TextDisplay";
import { Quiz } from "./components/ui/Quiz";
const sampleQuiz: Quiz = {
  title: "Introduction to Machine Learning Concepts",
  description: "A comprehensive quiz covering basic machine learning concepts, algorithms, and applications",
  instructions: "Select the best answer for each question. Each question has one correct answer. Take your time to read each question and explanation carefully.",
  difficulty_level: "moderate",
  target_skills: ["recall", "comprehension", "application", "analysis"],
  questions: [
    {
      question: "What is the primary difference between supervised and unsupervised learning?",
      answers: [
        {
          text: "Supervised learning uses labeled data for training, while unsupervised learning works with unlabeled data",
          is_correct: true,
          explanation: "This is correct. Supervised learning algorithms learn from labeled examples to make predictions, while unsupervised learning finds patterns in unlabeled data."
        },
        {
          text: "Supervised learning is faster than unsupervised learning",
          is_correct: false,
          explanation: "This is incorrect. The speed of learning depends on the specific algorithm and dataset, not whether it's supervised or unsupervised."
        },
        {
          text: "Supervised learning requires no human intervention",
          is_correct: false,
          explanation: "This is incorrect. Supervised learning actually requires human intervention to label the training data."
        },
        {
          text: "Unsupervised learning always produces better results",
          is_correct: false,
          explanation: "This is incorrect. The effectiveness depends on the specific problem and use case, not the type of learning."
        }
      ],
      difficulty: "moderate",
      topic: "Machine Learning Fundamentals",
      skill_tested: "comprehension"
    },
    {
      question: "Which of the following is an example of a regression problem?",
      answers: [
        {
          text: "Predicting house prices based on square footage and location",
          is_correct: true,
          explanation: "This is correct. Predicting a continuous numerical value (price) based on features is a classic regression problem."
        },
        {
          text: "Classifying emails as spam or not spam",
          is_correct: false,
          explanation: "This is incorrect. This is an example of binary classification, not regression."
        },
        {
          text: "Grouping customers by purchasing behavior",
          is_correct: false,
          explanation: "This is incorrect. This is an example of clustering, which is unsupervised learning."
        },
        {
          text: "Identifying objects in images",
          is_correct: false,
          explanation: "This is incorrect. This is an example of image classification, not regression."
        }
      ],
      difficulty: "easy",
      topic: "Types of Machine Learning Problems",
      skill_tested: "application"
    },
    {
      question: "What potential issue might arise if your training data is not representative of the real-world data?",
      answers: [
        {
          text: "Model bias and poor generalization to new data",
          is_correct: true,
          explanation: "This is correct. When training data doesn't represent the real world, the model may learn biased patterns and perform poorly on actual data."
        },
        {
          text: "Faster training times",
          is_correct: false,
          explanation: "This is incorrect. Training data representativeness doesn't directly affect training speed."
        },
        {
          text: "Improved model accuracy",
          is_correct: false,
          explanation: "This is incorrect. Non-representative data typically leads to worse, not better, accuracy."
        },
        {
          text: "Lower computational requirements",
          is_correct: false,
          explanation: "This is incorrect. Data representativeness is unrelated to computational requirements."
        }
      ],
      difficulty: "challenging",
      topic: "Model Training and Evaluation",
      skill_tested: "analysis"
    }
  ]
};

export function Main() {
  const {
    state: agentState,
  } = useCoAgent<AgentState>({
    name: "edison_ai",
    initialState: {
      messages: [{ content: "" }],
      quiz: sampleQuiz
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
