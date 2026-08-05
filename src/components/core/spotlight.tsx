// Spotlight – cursor-following radial glow (Motion Primitives style)
import React, { useCallback, useRef } from 'react';
import { motion, useMotionValue, useSpring } from 'framer-motion';

interface SpotlightProps {
  className?: string;
  size?: number;
}

export const Spotlight: React.FC<SpotlightProps> = ({
  className = 'from-blue-600 via-blue-400 to-blue-200 blur-xl',
  size = 200,
}) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mouseX = useMotionValue(-size * 2);
  const mouseY = useMotionValue(-size * 2);

  const springX = useSpring(mouseX, { stiffness: 200, damping: 28 });
  const springY = useSpring(mouseY, { stiffness: 200, damping: 28 });

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      const rect = containerRef.current?.getBoundingClientRect();
      if (!rect) return;
      mouseX.set(e.clientX - rect.left - size / 2);
      mouseY.set(e.clientY - rect.top - size / 2);
    },
    [mouseX, mouseY, size]
  );

  const handleMouseLeave = useCallback(() => {
    mouseX.set(-size * 2);
    mouseY.set(-size * 2);
  }, [mouseX, mouseY, size]);

  return (
    <div
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className="absolute inset-0 overflow-hidden pointer-events-none"
    >
      <motion.div
        className={`absolute rounded-full bg-radial-[ellipse_at_center] ${className} opacity-60`}
        style={{
          width: size,
          height: size,
          x: springX,
          y: springY,
        }}
      />
    </div>
  );
};
