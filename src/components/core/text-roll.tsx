// TextRoll – letter-by-letter roll-in animation (Motion Primitives style)
import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface TextRollProps {
  children: string;
  className?: string;
  duration?: number;
  staggerDelay?: number;
}

export const TextRoll: React.FC<TextRollProps> = ({
  children,
  className = '',
  duration = 0.5,
  staggerDelay = 0.04,
}) => {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setVisible(true), 80);
    return () => clearTimeout(timer);
  }, []);

  const letters = children.split('');

  return (
    <span className={`inline-flex overflow-hidden ${className}`} aria-label={children}>
      {letters.map((char, i) => (
        <motion.span
          key={i}
          initial={{ opacity: 0, y: 40, rotateX: -60 }}
          animate={visible ? { opacity: 1, y: 0, rotateX: 0 } : {}}
          transition={{
            duration,
            delay: i * staggerDelay,
            ease: [0.22, 1, 0.36, 1],
          }}
          style={{ display: char === ' ' ? 'inline' : 'inline-block', transformOrigin: 'bottom' }}
        >
          {char === ' ' ? '\u00A0' : char}
        </motion.span>
      ))}
    </span>
  );
};
