export interface QuestionResponse {
  question: string;
  response: string;
  analysis: string;
}

export interface StudentAssessment {
  knowledge_recall: QuestionResponse;
  comprehension: QuestionResponse;
  application: QuestionResponse;
  analysis: QuestionResponse;
  synthesis: QuestionResponse;
  evaluation: QuestionResponse;
  metacognitive: QuestionResponse;
}

export interface StudentLevelAssessment {
  assessment: StudentAssessment;
  overall_level: string;
  strengths: string[];
  areas_for_improvement: string[];
}

export interface QuizAnswer {
  text: string;
  is_correct: boolean;
  explanation?: string;
}

export interface QuizQuestion {
  question: string;
  answers: QuizAnswer[];
  difficulty: string;
  topic: string;
  skill_tested: string;
}

export interface Quiz {
  title: string;
  description: string;
  instructions: string;
  questions: QuizQuestion[];
  difficulty_level: string;
  target_skills: string[];
}

export interface Log {
  message: string;
  done: boolean;
}

export interface AgentState {
  messages: any[];
  route?: string;
  assessment?: StudentLevelAssessment;
  lesson_explanation?: string;
  logs?: Log[];
  transcript?: string;
  quiz?: Quiz;
}
