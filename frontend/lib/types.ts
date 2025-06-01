export type ModerationType = 'text' | 'image';


export interface ModerationResponnse {
  is_toxic: boolean;
  confidence: number;
  summary: string;
}

export interface ModeratedContent {
  type: ModerationType;
  isSafe: boolean;
  confidence: number;
  content: string;
  summary: string;
}