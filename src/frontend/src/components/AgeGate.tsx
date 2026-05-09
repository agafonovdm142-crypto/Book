import { useState } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, Check } from 'lucide-react';

export function AgeGate() {
  const [verified, setVerified] = useState(false);
  const [error, setError] = useState('');

  const handleVerify = async (method: 'self' | 'id') => {
    if (method === 'self') {
      setVerified(true);
      localStorage.setItem('ageVerified', 'true');
    }
  };

  if (verified || localStorage.getItem('ageVerified') === 'true') {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="fixed inset-0 z-[200] bg-[#1E1A18] flex items-center justify-center p-6"
    >
      <div className="max-w-md w-full text-center">
        {/* Logo */}
        <h1 className="text-4xl font-bold text-white font-serif mb-2 tracking-wider">
          ЖИВАЯ КНИГА
        </h1>
        <div className="w-16 h-[2px] bg-gradient-to-r from-[#7B2D4C] to-[#C8956C] mx-auto mb-8" />

        {/* Age verification card */}
        <div className="bg-white/5 backdrop-blur-sm rounded-3xl p-8 border border-white/10">
          <div className="w-14 h-14 rounded-full bg-[#7B2D4C]/20 flex items-center justify-center mx-auto mb-4">
            <AlertTriangle className="w-7 h-7 text-[#C8956C]" />
          </div>

          <h2 className="text-xl font-semibold text-white mb-2">
            Вам есть 18 лет?
          </h2>
          <p className="text-sm text-[#8A8580] mb-6">
            Этот сайт содержит эротический контент, предназначенный только для взрослой аудитории. Вход разрешён только лицам старше 18 лет.
          </p>

          <div className="space-y-3">
            <button
              onClick={() => handleVerify('self')}
              className="w-full py-4 bg-gradient-to-r from-[#7B2D4C] to-[#6B2642] text-white rounded-2xl font-semibold hover:shadow-lg hover:shadow-[#7B2D4C]/20 transition-all flex items-center justify-center gap-2"
            >
              <Check className="w-5 h-5" />
              Да, мне есть 18 лет
            </button>

            <button
              onClick={() => window.location.href = 'https://www.google.com'}
              className="w-full py-3 bg-white/5 text-[#8A8580] rounded-2xl text-sm hover:bg-white/10 transition-colors"
            >
              Нет, мне нет 18 лет — покинуть сайт
            </button>
          </div>

          {error && (
            <p className="text-red-400 text-xs mt-3">{error}</p>
          )}
        </div>

        {/* Disclaimer */}
        <p className="text-xs text-[#4A4542] mt-6">
          Нажимая "Да", вы подтверждаете, что вам исполнилось 18 лет и вы соглашаетесь с{' '}
          <a href="/terms" className="text-[#C8956C] hover:underline">условиями использования</a>
        </p>
      </div>
    </motion.div>
  );
}
