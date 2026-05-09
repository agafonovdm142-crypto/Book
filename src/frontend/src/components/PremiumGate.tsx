import { motion } from 'framer-motion';
import { X, Crown, Sparkles, Zap, Eye } from 'lucide-react';

interface PremiumGateProps {
  onClose: () => void;
}

const features = [
  { icon: Zap, text: 'Все выборы без ограничений' },
  { icon: Sparkles, text: 'AI-персонализация текста' },
  { icon: Eye, text: 'Эксклюзивные интимные сцены' },
  { icon: Crown, text: 'Ранний доступ к новым главам' },
];

export function PremiumGate({ onClose }: PremiumGateProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[100] flex items-end sm:items-center justify-center"
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-[#1E1A18]/80 backdrop-blur-sm" onClick={onClose} />

      {/* Modal */}
      <motion.div
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: 100, opacity: 0 }}
        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
        className="relative w-full sm:w-[420px] bg-[#FAF6F1] rounded-t-3xl sm:rounded-3xl p-6 shadow-2xl"
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 rounded-full bg-[#E8E4E0] flex items-center justify-center hover:bg-[#D5D0CC] transition-colors"
        >
          <X className="w-4 h-4 text-[#4A4542]" />
        </button>

        {/* Header */}
        <div className="text-center mb-6">
          <div className="w-14 h-14 rounded-full bg-gradient-to-br from-[#7B2D4C] to-[#C8956C] flex items-center justify-center mx-auto mb-3">
            <Crown className="w-7 h-7 text-white" />
          </div>
          <h3 className="text-xl font-bold text-[#1E1A18] font-serif">Premium</h3>
          <p className="text-sm text-[#8A8580] mt-1">
            Этот выбор доступен только для подписчиков
          </p>
        </div>

        {/* Features */}
        <div className="space-y-3 mb-6">
          {features.map(({ icon: Icon, text }) => (
            <div key={text} className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-[#7B2D4C]/10 flex items-center justify-center">
                <Icon className="w-4 h-4 text-[#7B2D4C]" />
              </div>
              <span className="text-sm text-[#1E1A18]">{text}</span>
            </div>
          ))}
        </div>

        {/* CTA */}
        <button className="w-full py-4 bg-gradient-to-r from-[#7B2D4C] to-[#6B2642] text-white rounded-2xl font-semibold text-sm hover:shadow-lg hover:shadow-[#7B2D4C]/20 transition-all active:scale-[0.98]">
          Оформить Premium — $14.99/мес
        </button>

        <button
          onClick={onClose}
          className="w-full py-3 text-[#8A8580] text-sm hover:text-[#4A4542] transition-colors mt-2"
        >
          Продолжить с бесплатным выбором
        </button>

        {/* Trial */}
        <p className="text-center text-xs text-[#8A8580] mt-4">
          Или <span className="text-[#7B2D4C] font-semibold cursor-pointer">попробуй 3 дня бесплатно</span>
        </p>
      </motion.div>
    </motion.div>
  );
}
