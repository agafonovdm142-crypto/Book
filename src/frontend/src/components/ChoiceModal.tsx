import { motion } from 'framer-motion';
import { Lock, Flame, Heart, Eye, Sparkles } from 'lucide-react';
import { useProfileStore } from '../stores/profileStore';

interface Choice {
  id: string;
  text: string;
  effects?: Record<string, number>;
  isPremium?: boolean;
}

interface ChoiceModalProps {
  choice: Choice;
  index: number;
  isSelected: boolean;
  onSelect: () => void;
}

const effectIcons: Record<string, typeof Flame> = {
  sensuality: Flame,
  romanticism: Heart,
  mystery: Eye,
  dominance: Sparkles,
  boldness: Flame,
  intimacy: Heart,
};

export function ChoiceModal({ choice, index, isSelected, onSelect }: ChoiceModalProps) {
  const { profile } = useProfileStore();

  const getEffectPreview = () => {
    if (!choice.effects) return null;
    return Object.entries(choice.effects).map(([key, value]) => {
      const Icon = effectIcons[key] || Sparkles;
      return (
        <span key={key} className="inline-flex items-center gap-1 text-xs text-[#8A8580]">
          <Icon className="w-3 h-3" />
          {value > 0 ? '+' : ''}{value}
        </span>
      );
    });
  };

  return (
    <motion.button
      onClick={onSelect}
      disabled={isSelected}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={`w-full text-left p-4 rounded-2xl border-[1.5px] transition-all duration-300 relative ${
        isSelected
          ? 'bg-[#7B2D4C] border-[#7B2D4C] text-white'
          : 'bg-white/80 border-[#7B2D4C]/30 hover:border-[#7B2D4C] hover:bg-[#7B2D4C]/5'
      }`}
    >
      <div className="flex items-start gap-3">
        {/* Choice letter */}
        <span className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
          isSelected ? 'bg-white text-[#7B2D4C]' : 'bg-[#7B2D4C]/10 text-[#7B2D4C]'
        }`}>
          {String.fromCharCode(65 + index)}
        </span>

        <div className="flex-1 min-w-0">
          <p className={`text-sm leading-relaxed ${isSelected ? 'text-white' : 'text-[#1E1A18]'}`}>
            {choice.text}
          </p>

          {/* Effect preview */}
          {choice.effects && (
            <div className="flex gap-3 mt-2 flex-wrap">
              {getEffectPreview()}
            </div>
          )}
        </div>

        {/* Premium lock */}
        {choice.isPremium && (
          <Lock className={`flex-shrink-0 w-4 h-4 ${isSelected ? 'text-white/70' : 'text-[#C8956C]'}`} />
        )}
      </div>
    </motion.button>
  );
}
