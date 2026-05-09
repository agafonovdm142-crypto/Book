export interface Choice {
  id: string;
  text: string;
  effects?: Record<string, number>;
  condition?: {
    stat?: { name: string; min?: number; max?: number };
    flag?: string;
  };
}

export interface Scene {
  sceneId: string;
  type: 'interactive' | 'narrative' | 'cliffhanger';
  location?: string;
  time?: string;
  text: string;
  textVariant?: 'default' | 'romantic' | 'dominant' | 'mysterious';
  illustrationUrl?: string;
  illustrationPrompt?: string;
  choices: Choice[];
  isPremium?: boolean;
  music?: string;
}

export interface Profile {
  heroName: string;
  city: string;
  romanticism: number;
  adventure: number;
  dominance: number;
  sensuality: number;
  mystery: number;
  confidence: number;
  boldness: number;
  intimacy: number;
  seduction: number;
  submission?: number;
  passion?: number;
}

export interface StoryProgress {
  currentSceneId: string;
  flags: string[];
  chapter: number;
  completedChapters: number[];
}

export interface User {
  id: string;
  email: string;
  name?: string;
  subscription: 'free' | 'premium' | 'vip';
  ageVerified: boolean;
}

export interface SubscriptionTier {
  id: string;
  name: string;
  price: number;
  period: 'month' | 'year';
  features: string[];
}
