import { create } from 'zustand';

interface Choice {
  id: string;
  text: string;
  effects?: Record<string, number>;
}

interface Scene {
  sceneId: string;
  location?: string;
  time?: string;
  text: string;
  illustrationUrl?: string;
  choices: Choice[];
  isPremium?: boolean;
}

interface StoryState {
  currentScene: Scene | null;
  history: string[];
  flags: string[];
  isLoading: boolean;
  streak: number;
  lastReadAt: string | null;

  loadScene: (sceneId: string) => Promise<void>;
  makeChoice: (choiceId: string) => Promise<void>;
  addFlag: (flag: string) => void;
}

export const useStoryStore = create<StoryState>((set, get) => ({
  currentScene: null,
  history: [],
  flags: [],
  isLoading: false,
  streak: 0,
  lastReadAt: null,

  loadScene: async (sceneId: string) => {
    set({ isLoading: true });
    try {
      const response = await fetch(`/api/v1/story/scene/${sceneId}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });
      const scene: Scene = await response.json();
      set({
        currentScene: scene,
        history: [...get().history, sceneId],
        isLoading: false,
      });
    } catch (error) {
      console.error('Failed to load scene:', error);
      set({ isLoading: false });
    }
  },

  makeChoice: async (choiceId: string) => {
    set({ isLoading: true });
    try {
      const response = await fetch('/api/v1/story/choice', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ choiceId }),
      });
      const result: Scene = await response.json();
      set({
        currentScene: result,
        history: [...get().history, result.sceneId],
        isLoading: false,
      });
    } catch (error) {
      console.error('Failed to make choice:', error);
      set({ isLoading: false });
    }
  },

  addFlag: (flag: string) => {
    set({ flags: [...get().flags, flag] });
  },
}));
