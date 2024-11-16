import ReactMarkdown from 'react-markdown';
import { AgentState } from "../../lib/types";

interface QuizProps {
  quiz: string;
}

export function Quiz({ quiz }: QuizProps) {
  return (
    <div className="w-1/2 flex-grow p-4 space-y-4">
      <div className="text-sm text-gray-700">
        <div className="h-[calc(100vh-2rem)] overflow-y-auto">
          <p className="text-lg font-bold">Quiz</p>
          <ReactMarkdown>{quiz}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
} 