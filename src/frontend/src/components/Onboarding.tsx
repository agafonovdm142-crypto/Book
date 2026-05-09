import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Heart, MapPin, Sparkles, ArrowRight } from 'lucide-react';
import { useProfileStore } from '../stores/profileStore';

const moods = [
  { id: 'romantic', label: 'Романтика', desc: 'Хочу нежности и чувственности', icon: Heart, effects: { romanticism: 3 } },
  { id: 'adventure', label: 'Приключения', desc: 'Хочу азарта и нового', icon: Sparkles, effects: { adventure: 3 } },
  { id: 'dominance', label: 'Контроль', desc: 'Хочу управлять ситуацией', icon: Sparkles, effects: { dominance: 3 } },
  { id: 'mystery', label: 'Загадка', desc: 'Хочу быть непредсказуемой', icon: Sparkles, effects: { mystery: 3 } },
];

export function Onboarding() {
  const [step, setStep] = useState(0);
  const [name, setName] = useState('');
  const [city, setCity] = useState('');
  const [selectedMood, setSelectedMood] = useState('');
  const { setHeroName, setCity: setProfileCity, updateProfile } = useProfileStore();

  const handleComplete = () => {
    if (name) setHeroName(name);
    if (city) setProfileCity(city);
    const mood = moods.find(m => m.id === selectedMood);
    if (mood) updateProfile(mood.effects);
    localStorage.setItem('onboardingComplete', 'true');
    window.location.reload();
  };

  if (localStorage.getItem('onboardingComplete') === 'true') return null;

  return (
    <div className="fixed inset-0 z-[150] bg-gradient-to-b from-[#FAF6F1] to-[#F5E6D8] flex items-center justify-center p-6">
      <div className="max-w-md w-full">
        <AnimatePresence mode="wait">
          {step === 0 && (
            <motion.div
              key="step0"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="text-center"
            >
              <h1 className="text-4xl font-bold text-[#1E1A18] font-serif mb-2">
                ЖИВАЯ КНИГА
              </h1>
              <p className="text-[#8A8580] mb-8">Твоя история. Твой выбор.</p>

              <div className="bg-white/80 rounded-3xl p-6 shadow-sm">
                <label className="block text-left text-sm font-semibold text-[#1E1A18] mb-2">
                  Как тебя зовут?
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Алиса"
                  className="w-full px-4 py-3 rounded-2xl border border-[#E8E4E0] focus:border-[#7B2D4C] focus:outline-none text-[#1E1A18] bg-white"
                />
              </div>

              <button
                onClick={() => name && setStep(1)}
                disabled={!name}
                className="mt-6 w-full py-4 bg-gradient-to-r from-[#7B2D4C] to-[#6B2642] text-white rounded-2xl font-semibold disabled:opacity-40 flex items-center justify-center gap-2"
              >
                Далее <ArrowRight className="w-5 h-5" />
              </button>
            </motion.div>
          )}

          {step === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <div className="bg-white/80 rounded-3xl p-6 shadow-sm">
                <div className="flex items-center gap-2 mb-4">
                  <MapPin className="w-5 h-5 text-[#7B2D4C]" />
                  <label className="text-sm font-semibold text-[#1E1A18]">
                    В каком городе ты просыпаешься?
                  </label>
                </div>
                <input
                  type="text"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  placeholder="Москва"
                  className="w-full px-4 py-3 rounded-2xl border border-[#E8E4E0] focus:border-[#7B2D4C] focus:outline-none text-[#1E1A18] bg-white"
                />
              </div>

              <button
                onClick={() => city && setStep(2)}
                disabled={!city}
                className="mt-6 w-full py-4 bg-gradient-to-r from-[#7B2D4C] to-[#6B2642] text-white rounded-2xl font-semibold disabled:opacity-40 flex items-center justify-center gap-2"
              >
                Далее <ArrowRight className="w-5 h-5" />
              </button>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <h2 className="text-xl font-semibold text-[#1E1A18] mb-2">
                Какой у тебя настрой?
              </h2>
              <p className="text-sm text-[#8A8580] mb-6">
                Это повлияет на первую историю
              </p>

              <div className="space-y-3">
                {moods.map((mood) => (
                  <button
                    key={mood.id}
                    onClick={() => setSelectedMood(mood.id)}
                    className={`w-full p-4 rounded-2xl border-[1.5px] text-left transition-all ${
                      selectedMood === mood.id
                        ? 'border-[#7B2D4C] bg-[#7B2D4C]/5'
                        : 'border-[#E8E4E0] bg-white hover:border-[#7B2D4C]/30'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <mood.icon className="w-5 h-5 text-[#7B2D4C]" />
                      <div>
                        <p className="font-semibold text-[#1E1A18] text-sm">{mood.label}</p>
                        <p className="text-xs text-[#8A8580]">{mood.desc}</p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>

              <button
                onClick={handleComplete}
                disabled={!selectedMood}
                className="mt-6 w-full py-4 bg-gradient-to-r from-[#7B2D4C] to-[#6B2642] text-white rounded-2xl font-semibold disabled:opacity-40"
              >
                Начать историю
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Progress dots */}
        <div className="flex justify-center gap-2 mt-6">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className={`w-2 h-2 rounded-full transition-colors ${
                i === step ? 'bg-[#7B2D4C]' : 'bg-[#E8E4E0]'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
