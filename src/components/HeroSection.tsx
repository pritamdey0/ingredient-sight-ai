import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { TextEffectSpeed } from './core/text-effect';

interface HeroSectionProps {
  onOpenDashboard: () => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({ onOpenDashboard }) => {
  const videoLeftRef = useRef<HTMLVideoElement | null>(null);
  const videoRightRef = useRef<HTMLVideoElement | null>(null);
  const activeSideRef = useRef<'left' | 'right'>('right');
  const [heroOpacity, setHeroOpacity] = useState(1);

  // Scroll listener to fade out hero content (logo, caption, CTA) between 0 and 100vh
  useEffect(() => {
    const handleScroll = () => {
      const scrollY = window.scrollY;
      const vh = window.innerHeight || 800;
      // Opacity goes from 1 at scrollY=0 to 0 at scrollY = vh * 0.65
      const newOpacity = Math.max(0, Math.min(1, 1 - scrollY / (vh * 0.65)));
      setHeroOpacity(newOpacity);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Video scrubbing physics
  useEffect(() => {
    let animationFrameId: number = 0;
    const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

    const handleMouseMove = (e: MouseEvent) => {
      if (isTouch) return;

      const width = window.innerWidth;
      const deadZone = Math.max(30, width * 0.05);
      const center = width / 2;
      const mouseX = e.clientX;

      const leftVideo = videoLeftRef.current;
      const rightVideo = videoRightRef.current;

      if (!leftVideo || !rightVideo) return;

      if (Math.abs(mouseX - center) <= deadZone) {
        if (!leftVideo.seeking) leftVideo.currentTime = 0;
        if (!rightVideo.seeking) rightVideo.currentTime = 0;
        return;
      }

      if (mouseX < center - deadZone) {
        if (activeSideRef.current !== 'right') {
          activeSideRef.current = 'right';
          rightVideo.style.display = 'block';
          leftVideo.style.display = 'none';
        }

        const availableRange = center - deadZone;
        const distFromCenter = center - deadZone - mouseX;
        const progress = Math.min(1, Math.max(0, distFromCenter / availableRange));

        if (rightVideo.duration && !rightVideo.seeking) {
          rightVideo.currentTime = progress * rightVideo.duration;
        }
      } else {
        if (activeSideRef.current !== 'left') {
          activeSideRef.current = 'left';
          leftVideo.style.display = 'block';
          rightVideo.style.display = 'none';
        }

        const availableRange = width - (center + deadZone);
        const distFromCenter = mouseX - (center + deadZone);
        const progress = Math.min(1, Math.max(0, distFromCenter / availableRange));

        if (leftVideo.duration && !leftVideo.seeking) {
          leftVideo.currentTime = progress * leftVideo.duration;
        }
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <>
      {/* Background Video Layer */}
      <div
        id="main-canvas"
        className="pointer-events-none fixed inset-0 w-full h-full z-0 overflow-hidden bg-black transition-opacity duration-700 opacity-100"
      >
        <div className="relative w-full h-full scale-100 transition-transform duration-[25000ms] ease-out hover:scale-105">
          <div className="absolute inset-0 bg-gradient-to-b from-black/70 via-black/50 to-black/90 z-10 pointer-events-none" />

          <video
            ref={videoLeftRef}
            src="/assets/hero_video.mp4"
            muted
            playsInline
            preload="auto"
            loop
            autoPlay
            className="absolute inset-0 w-full h-full object-cover hidden"
          />

          <video
            ref={videoRightRef}
            src="/assets/hero_video.mp4"
            muted
            playsInline
            preload="auto"
            loop
            autoPlay
            className="absolute inset-0 w-full h-full object-cover block"
          />
        </div>
      </div>

      

      {/* Hero Content Overlay (Fades out between 0 and 100vh scroll) */}
      <div
        className="fixed inset-0 z-20 pointer-events-none flex flex-col justify-between p-6 sm:p-10 lg:p-12 transition-opacity duration-300"
        style={{
          opacity: heroOpacity,
          pointerEvents: heroOpacity < 0.1 ? 'none' : 'auto',
        }}
      >
        {/* Top Left Logo & Title - Sized precisely per request */}
        {/* Mobile: 160px | Tablet: 220px | Desktop: 300px */}
        <div className="mt-2 sm:mt-4">
          <motion.div
            className="w-[160px] sm:w-[220px] lg:w-[300px] cursor-pointer"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
           
          >
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-white tracking-tight leading-none font-sans drop-shadow-lg">
              <TextEffectSpeed text="IngredientSight AI.." />
            </h1>
            <p className="text-[11px] sm:text-xs font-mono text-zinc-400 tracking-wider uppercase mt-1">
              Cosmetic Molecular Intelligence
            </p>
          </motion.div>

          {/* Subtitle / Caption */}
          <motion.p
            className="text-xs sm:text-sm text-zinc-300 max-w-md mt-4 leading-relaxed font-light drop-shadow"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            Real-time INCI safety analysis, toxicological profiling, and evidence synthesis powered by autonomous AI agents.
          </motion.p>
        </div>

      </div>
    </>
  );
};