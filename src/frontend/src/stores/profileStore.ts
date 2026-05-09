import { create } from 'zustand';

interface Profile {
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
}

interface ProfileState {
  profile: Profile | null;
  isLoading: boolean;

  loadProfile: () => Promise<void>;
  updateProfile: (effects: Record<string, number>) => void;
  setHeroName: (name: string) => void;
  setCity: (city: string) => void;
}

const defaultProfile: Profile = {
  heroName: 'Алиса',
  city: 'Москва',
  romanticism: 5,
  adventure: 5,
  dominance: 5,
  sensuality: 5,
  mystery: 5,
  confidence: 5,
  boldness: 5,
  intimacy: 5,
  seduction: 5,
};

export const useProfileStore = create<ProfileState>((set, get) => ({
  profile: null,
  isLoading: false,

  loadProfile: async () => {
    try {
      const response = await fetch('/api/v1/profile', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });
      if (response.ok) {
        const profile: Profile = await response.json();
        set({ profile });
      } else {
        set({ profile: defaultProfile });
      }
    } catch {
      set({ profile: defaultProfile });
    }
  },

  updateProfile: (effects: Record<string, number>) => {
    const { profile } = get();
    if (!profile) return;
    const updated = { ...profile };
    for (const [key, value] of Object.entries(effects)) {
      if (key in updated) {
        (updated as any)[key] = Math.min(10, Math.max(1, (updated as any)[key] + value));
      }
    }
    set({ profile: updated });
  },

  setHeroName: (name: string) => {
    set({ profile: { ...(get().profile || defaultProfile), heroName: name } });
  },

  setCity: (city: string) => {
    set({ profile: { ...(get().profile || defaultProfile), city } });
  },
}));
