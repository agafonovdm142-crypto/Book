import { create } from 'zustand';
import scenes from '../data/scenes';

interface Choice {
  id: string;
  text: string;
  effects?: Record<string, number>;
  isPremium?: boolean;
  nextSceneId: string;
}

interface Scene {
  sceneId: string;
  location?: string;
  time?: string;
  text: string;
  illustrationUrl?: string;
  choices: Choice[];
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
    // Simulate API delay for realism
    await new Promise(r => setTimeout(r, 300));
    const scene = scenes[sceneId];
    if (scene) {
      set({
        currentScene: scene,
        history: [...get().history, sceneId],
        isLoading: false,
      });
    } else {
      console.error('Scene not found:', sceneId);
      set({ isLoading: false });
    }
  },

  makeChoice: async (choiceId: string) => {
    set({ isLoading: true });
    await new Promise(r => setTimeout(r, 200));
    const current = get().currentScene;
    if (!current) return;
    const choice = current.choices.find(c => c.id === choiceId);
    if (choice && scenes[choice.nextSceneId]) {
      const nextScene = scenes[choice.nextSceneId];
      set({
        currentScene: nextScene,
        history: [...get().history, nextScene.sceneId],
        isLoading: false,
      });
    }
    set({ isLoading: false });
  },

  addFlag: (flag: string) => {
    set({ flags: [...get().flags, flag] });
  },
}));
.error('Failed to make choice:', error);
      set({ isLoading: false });
    }
  },

  addFlag: (flag: string) => {
    set({ flags: [...get().flags, flag] });
  },
}));
