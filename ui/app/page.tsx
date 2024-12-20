"use client";

import { CopilotKit } from "@copilotkit/react-core";
import { Main } from "./Main";
import "@copilotkit/react-ui/styles.css";
import ReactMarkdown from 'react-markdown';

export default function Home() {
  return (
    <main className="flex flex-col items-center justify-between">
      <CopilotKit runtimeUrl="/api/copilotkit" agent="edison_ai" showDevConsole={false}>
        <Main />
      </CopilotKit>
    </main>
  );
}
