import React from 'react';
import { motion } from 'framer-motion';

interface TextEffectProps {
  children: string;
  preset?: 'fade-in-blur' | 'fade-in' | 'slide-up';
  speedReveal?: number;
  speedSegment?: number;
  className?: string;
}

export const TextEffect: React.FC<TextEffectProps> = ({
  children,
  preset = 'fade-in-blur',
  speedReveal = 1.1,
  speedSegment = 0.3,
  className = '',
}) => {
  const words = children.split(' ');

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: speedSegment / Math.max(1, words.length),
        duration: speedReveal,
      },
    },
  };

  const itemVariants = {
    hidden: {
      opacity: 0,
      filter: preset === 'fade-in-blur' ? 'blur(12px)' : 'none',
      y: preset === 'slide-up' ? 20 : 0,
    },
    visible: {
      opacity: 1,
      filter: 'blur(0px)',
      y: 0,
      transition: {
        duration: speedSegment,
        ease: [0.25, 0.1, 0.25, 1] as const,
      },
    },
  };

  return (
    <motion.span
      className={`inline-flex flex-wrap gap-x-2.5 ${className}`}
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {words.map((word, idx) => (
        <motion.span key={idx} variants={itemVariants} className="inline-block">
          {word}
        </motion.span>
      ))}
    </motion.span>
  );
};

export function TextEffectSpeed({ text = 'IngredientSight AI..' }: { text?: string }) {
  return (
    <TextEffect preset="fade-in-blur" speedReveal={1.1} speedSegment={0.3}>
      {text}
    </TextEffect>
  );
}
