"use client";

import { useCoAgent, useCoAgentStateRender, useCopilotChat } from "@copilotkit/react-core";
import { CopilotPopup } from "@copilotkit/react-ui";
import { TextMessage, MessageRole } from "@copilotkit/runtime-client-gql";
import { CopilotChat } from "@copilotkit/react-ui";
import { Progress } from "./components/ui/Progress";
import { AgentState } from "./lib/types";

export function Main() {
  const {
    state: agentState,
  } = useCoAgent<AgentState>({
    name: "edison_ai",
    initialState: { 
      messages: [{ content: "" }],
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
      
      {/* Right sidebar for chat */}
      <div className="w-120 border-l border-gray-200">
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
