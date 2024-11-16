import { Quiz as QuizType } from "../../lib/types";
import { useState } from 'react';

interface QuizProps {
  quiz: QuizType;
}

export function Quiz({ quiz }: QuizProps) {
  const [selectedAnswers, setSelectedAnswers] = useState<{ [key: number]: number }>({});
  const [showExplanations, setShowExplanations] = useState<{ [key: number]: boolean }>({});

  const handleAnswerSelect = (questionIndex: number, answerIndex: number) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [questionIndex]: answerIndex
    }));
    setShowExplanations(prev => ({
      ...prev,
      [questionIndex]: true
    }));
  };

  return (
    <div className="w-1/2 flex-grow p-4 space-y-6">
      <div className="text-sm text-gray-700">
        <div className="h-[calc(100vh-2rem)] overflow-y-auto space-y-6">
          {/* Quiz Header */}
          <div className="space-y-2">
            <h1 className="text-2xl font-bold">{quiz.title}</h1>
            <p className="text-gray-600">{quiz.description}</p>
            <p className="text-sm text-gray-500 italic">{quiz.instructions}</p>
            <div className="flex gap-2 text-xs text-gray-500">
              <span>Difficulty: {quiz.difficulty_level}</span>
              <span>•</span>
              <span>Skills: {quiz.target_skills.join(', ')}</span>
            </div>
          </div>

          {/* Questions */}
          <div className="space-y-8">
            {quiz.questions.map((question, qIndex) => (
              <div key={qIndex} className="space-y-4 p-4 bg-white rounded-lg shadow">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Question {qIndex + 1}</span>
                    <div className="flex gap-2 text-xs text-gray-500">
                      <span>{question.difficulty}</span>
                      <span>•</span>
                      <span>{question.topic}</span>
                    </div>
                  </div>
                  <p className="font-medium">{question.question}</p>
                </div>

                {/* Answers */}
                <div className="space-y-2">
                  {question.answers.map((answer, aIndex) => (
                    <div key={aIndex}>
                      <button
                        className={`w-full text-left p-3 rounded-md transition-colors ${
                          selectedAnswers[qIndex] === aIndex
                            ? answer.is_correct
                              ? 'bg-green-100 border-green-500'
                              : 'bg-red-100 border-red-500'
                            : 'bg-gray-50 hover:bg-gray-100'
                        } border`}
                        onClick={() => handleAnswerSelect(qIndex, aIndex)}
                      >
                        {answer.text}
                      </button>
                      
                      {/* Explanation */}
                      {showExplanations[qIndex] && selectedAnswers[qIndex] === aIndex && (
                        <div className={`mt-2 p-3 rounded-md text-sm ${
                          answer.is_correct ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                        }`}>
                          {answer.explanation}
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {/* Question Metadata */}
                <div className="text-xs text-gray-500">
                  Skill tested: {question.skill_tested}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
} 