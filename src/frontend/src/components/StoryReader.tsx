import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Lock, Sparkles } from 'lucide-react';
import { useStoryStore } from '../stores/storyStore';
import { useProfileStore } from '../stores/profileStore';
import { ChoiceModal } from './ChoiceModal';
import { PremiumGate } from './PremiumGate';

export function StoryReader() {
  const { currentScene, isLoading, loadScene, makeChoice } = useStoryStore();
  const { profile } = useProfileStore();
  const [selectedChoice, setSelectedChoice] = useState<string | null>(null);
  const [showPremium, setShowPremium] = useState(false);
  const [showChoices, setShowChoices] = useState(false);
  const textRef = useRef<HTMLDivElement>(null);
  const [textRevealed, setTextRevealed] = useState(false);

  useEffect(() => {
    loadScene('scene_01_morning_wake');
  }, []);

  useEffect(() => {
    if (currentScene) {
      setTextRevealed(false);
      setShowChoices(false);
      setTimeout(() => setTextRevealed(true), 300);
      setTimeout(() => setShowChoices(true), currentScene.text.length * 8 + 500);
    }
  }, [currentScene?.sceneId]);

  const handleChoice = async (choiceId: string, isPremium?: boolean) => {
    if (isPremium && profile?.subscription === 'free') {
      setShowPremium(true);
      return;
    }
    setSelectedChoice(choiceId);
    await makeChoice(choiceId);
    setSelectedChoice(null);
  };

  const scrollToChoices = () => {
    textRef.current?.scrollTo({ top: textRef.current.scrollHeight, behavior: 'smooth' });
  };

  if (isLoading && !currentScene) {
    return (
      <div className="h-screen w-full bg-[#FAF6F1] flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-[#7B2D4C] border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="mt-4 text-[#8A8580] text-sm">Загружаем историю...</p>
        </div>
      </div>
    );
  }

  if (!currentScene) return null;

  return (
    <div className="h-screen w-full bg-gradient-to-b from-[#FAF6F1] to-[#F5E6D8] flex flex-col overflow-hidden">
      {/* Progress Bar */}
      <div className="h-[3px] w-full bg-[#E8E4E0] fixed top-0 z-50">
        <motion.div
          className="h-full bg-gradient-to-r from-[#7B2D4C] to-[#C8956C]"
          initial={{ width: '0%' }}
          animate={{ width: `${(useStoryStore.getState().history.length / 22) * 100}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>

      {/* Illustration */}
      <div className="relative h-[45vh] w-full flex-shrink-0">
        {currentScene.illustrationUrl ? (
          <motion.img
            key={currentScene.illustrationUrl}
            src={currentScene.illustrationUrl}
            alt={currentScene.location || 'Scene'}
            className="w-full h-full object-cover"
            initial={{ opacity: 0, scale: 1.05 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-[#7B2D4C]/20 to-[#C8956C]/20 flex items-center justify-center">
            <Sparkles className="w-12 h-12 text-[#7B2D4C]/30" />
          </div>
        )}
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-[#FAF6F1]" />

        {/* Scene label */}
        <div className="absolute top-4 left-4 flex items-center gap-2">
          {currentScene.location && (
            <span className="text-xs font-semibold uppercase tracking-widest text-[#8A8580] bg-white/80 backdrop-blur-sm px-3 py-1 rounded-full">
              {currentScene.location}
            </span>
          )}
          {currentScene.time && (
            <span className="text-xs font-semibold text-[#C8956C] bg-white/80 backdrop-blur-sm px-3 py-1 rounded-full">
              {currentScene.time}
            </span>
          )}
        </div>
      </div>

      {/* Text Area */}
      <div
        ref={textRef}
        className="flex-1 overflow-y-auto px-6 py-4 scrollbar-hide"
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={currentScene.sceneId}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: textRevealed ? 1 : 0, y: textRevealed ? 0 : 20 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="max-w-lg mx-auto"
          >
            {/* Story text with paragraph animation */}
            {currentScene.text.split('\n\n').map((paragraph, idx) => (
              <motion.p
                key={idx}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: idx * 0.15 }}
                className={`mb-4 leading-relaxed ${
                  paragraph.startsWith('«') || paragraph.startsWith('"')
                    ? 'font-serif italic text-[#7B2D4C] text-lg'
                    : 'text-[#1E1A18] text-base'
                }`}
              >
                {paragraph}
              </motion.p>
            ))}
          </motion.div>
        </AnimatePresence>

        {/* Choices */}
        <AnimatePresence>
          {showChoices && currentScene.choices.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="max-w-lg mx-auto mt-6 pb-8 space-y-3"
            >
              {currentScene.choices.map((choice, idx) => (
                <ChoiceModal
                  key={choice.id}
                  choice={choice}
                  index={idx}
                  isSelected={selectedChoice === choice.id}
                  onSelect={() => handleChoice(choice.id, choice.isPremium)}
                />
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Scroll hint */}
      {!showChoices && (
        <motion.button
          onClick={scrollToChoices}
          className="absolute bottom-4 left-1/2 -translate-x-1/2 text-[#8A8580] animate-bounce"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2 }}
        >
          <ChevronDown className="w-6 h-6" />
        </motion.button>
      )}

      {/* Premium Gate Modal */}
      {showPremium && (
        <PremiumGate onClose={() => setShowPremium(false)} />
      )}
    </div>
  );
}
