import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

interface HeroSectionProps {
  onOpenDashboard: () => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({ onOpenDashboard }) => {
  const videoLeftRef = useRef<HTMLVideoElement | null>(null);
  const videoRightRef = useRef<HTMLVideoElement | null>(null);
  const activeSideRef = useRef<'left' | 'right'>('right');

  // Video interaction & scrubbing physics for desktop / tablet / touch
  useEffect(() => {
    let animationFrameId: number;
    let isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

    const handleMouseMove = (e: MouseEvent) => {
      if (isTouch) return;

      const width = window.innerWidth;
      const deadZone = Math.max(30, width * 0.05);
      const center = width / 2;
      const mouseX = e.clientX;

      const leftVideo = videoLeftRef.current;
      const rightVideo = videoRightRef.current;

      if (!leftVideo || !rightVideo) return;

      // Check dead zone: within +/- deadZone around center
      if (Math.abs(mouseX - center) <= deadZone) {
        if (!leftVideo.seeking) leftVideo.currentTime = 0;
        if (!rightVideo.seeking) rightVideo.currentTime = 0;
        return;
      }

      if (mouseX < center - deadZone) {
        // Cursor left of deadzone -> active side RIGHT video
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
        // Cursor right of deadzone -> active side LEFT video
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
      {/* 1G. Video Container (Hero Layer) */}
      <div
        id="main-canvas"
        className="pointer-events-none fixed inset-0 w-full h-full z-0 overflow-hidden bg-black transition-opacity duration-700 opacity-100"
        style={{
          // Mobile responsive height adjustment
          top: window.innerWidth < 640 ? '220px' : '0',
          height: window.innerWidth < 640 ? 'calc(100vh - 220px)' : '100vh',
        }}
      >
        {/* Living background zoom & fade animation */}
        <div className="relative w-full h-full animate-[fadeIn_1s_ease-out] scale-100 transition-transform duration-[25000ms] ease-out hover:scale-105">
          {/* Subtle Dark Gradient Overlay (40–60% opacity) */}
          <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/40 to-black/80 z-10 pointer-events-none" />

          {/* Left Video */}
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

          {/* Right Video */}
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

      {/* 1B. Logo (Top Left) */}
      <motion.div
        className="fixed pointer-events-none z-20 top-4 left-4 lg:top-8 lg:left-8 mix-blend-exclusion"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.25, 0.1, 0.25, 1], delay: 0 }}
      >
        <svg
          viewBox="0 0 355 110"
          className="w-[124px] sm:w-[266px] lg:w-[355px] h-auto fill-white"
        >
          {/* PRMPT Wordmark Logo */}
          <text
            x="0"
            y="75"
            fontSize="78"
            fontWeight="700"
            fontFamily="Inter Tight, sans-serif"
            letterSpacing="-0.06em"
          >
            prmpt
          </text>
          {/* Circled R mark */}
          <circle cx="285" cy="30" r="14" stroke="white" strokeWidth="3" fill="none" />
          <text
            x="285"
            y="35"
            fontSize="15"
            fontWeight="600"
            textAnchor="middle"
            fill="white"
          >
            R
          </text>
        </svg>
      </motion.div>

      {/* 1C. Caption (Below Logo, Left Side) */}
      <motion.div
        className="fixed pointer-events-none z-20 left-4 lg:left-8 text-white mix-blend-exclusion max-w-[692px] w-[calc(100vw-32px)] sm:w-[calc(50vw-48px)] lg:w-[692px]"
        style={{
          top: window.innerWidth >= 1024 ? '244px' : window.innerWidth >= 640 ? '180px' : '118px',
          fontFamily: 'Inter Tight, sans-serif',
          fontWeight: 500,
          fontSize: '12px',
          lineHeight: '140%',
          letterSpacing: '-0.04em',
        }}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.25, 0.1, 0.25, 1], delay: 0.3 }}
      >
        When switching between videos near the center, do not reset currentTime to 0 abruptly. Add a small dead zone: if cursor is within +/-50px of center, keep both videos at currentTime = 0 and show whichever was last active.
      </motion.div>

      {/* 1D. Header Navigation (Top Right) */}
      <motion.div
        className="fixed z-20 top-4 right-4 lg:top-8 lg:right-8 w-auto lg:w-[330px] h-[30px] flex items-center justify-between mix-blend-exclusion pointer-events-auto"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.25, 0.1, 0.25, 1], delay: 0.15 }}
      >
        <span className="hidden lg:inline text-white uppercase text-[15px] font-medium tracking-tight hover:opacity-75 transition-opacity cursor-pointer">
          ABOUT
        </span>

        <div className="flex items-center gap-5 lg:gap-[50px]">
          <button
            onClick={onOpenDashboard}
            className="text-white text-[13px] lg:text-[15px] font-medium tracking-tight uppercase hover:underline flex items-center gap-1.5"
            title="Open IngredientSight AI Dashboard"
          >
            [ DASHBOARD ]
          </button>

          <div className="cursor-pointer group" onClick={onOpenDashboard}>
            <svg
              viewBox="0 0 40 40"
              className="w-6 h-6 lg:w-[30px] lg:h-[30px] stroke-white"
              strokeWidth="2.5"
            >
              <path d="M0 14H40" />
              <path d="M0 26H40" />
            </svg>
          </div>

          <span className="text-white text-[13px] lg:text-[15px] font-medium tracking-tight cursor-pointer">
            [ CART ]
          </span>
        </div>
      </motion.div>

      {/* 1E. Product Info (Bottom Right) */}
      <motion.div
        id="outro-info"
        className="fixed z-20 right-0 left-0 lg:left-auto lg:right-[32px] bottom-[48px] lg:bottom-[80px] w-full lg:w-[330px] flex flex-col items-center mix-blend-exclusion pointer-events-none"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.45 }}
        data-outro-offset={window.innerWidth >= 1024 ? 166 : 132}
      >
        <div className="flex flex-col items-start lg:items-start w-[252px] lg:w-full mb-3 lg:mb-8">
          <div className="relative w-5 h-5 lg:w-[30px] lg:h-[30px] mb-2 flex items-center justify-center">
            <svg viewBox="0 0 40 40" className="w-full h-full">
              <circle
                cx="20"
                cy="20"
                r="18.75"
                stroke="white"
                strokeWidth={window.innerWidth >= 1024 ? '2.5' : '2'}
                fill="none"
              />
            </svg>
            <span
              id="circle-symbol"
              className="absolute text-white font-medium text-[10px] lg:text-[15px] tracking-tighter uppercase"
            >
              8
            </span>
          </div>

          <div className="text-white text-[20px] lg:text-[30px] leading-none tracking-[-0.04em] uppercase text-center lg:text-left font-medium">
            ARCHIVE COLLECTION
            <br />
            "PROMPT"
          </div>
        </div>

        <div className="text-white text-[60px] lg:text-[80px] leading-none tracking-[-0.04em] font-medium text-center">
          $97,33
        </div>
      </motion.div>

      {/* 1F. "View" Button (Bottom Right, Initially Scaled 0) */}
      <div
        id="outro-buy"
        onClick={onOpenDashboard}
        className="fixed z-20 right-4 lg:right-[32px] bottom-[60px] lg:bottom-[32px] w-[calc(100vw-32px)] lg:w-[330px] h-[100px] lg:h-[174px] bg-white rounded-[1335px] flex items-center justify-center cursor-pointer transition-transform duration-300 pointer-events-auto shadow-2xl hover:scale-105"
        style={{
          transformOrigin: 'right bottom',
          transform: 'scale(0)',
          mixBlendMode: 'exclusion',
        }}
      >
        <span
          className="text-white font-medium text-[72px] lg:text-[110px] tracking-[-0.04em] uppercase select-none"
          style={{ mixBlendMode: 'exclusion' }}
        >
          view
        </span>
      </div>

      {/* 1I. White Overlay (Scroll Controlled) */}
      <div
        id="outro-overlay"
        className="fixed inset-0 pointer-events-none z-12 bg-white opacity-0 transition-opacity"
      />

      {/* 1J. Footer */}
      <div
        id="outro-footer"
        className="fixed bottom-6 lg:bottom-[32px] left-4 lg:left-[16px] z-20 pointer-events-none mix-blend-exclusion opacity-0 transition-opacity flex justify-between lg:justify-start lg:gap-[80px] text-white text-[11px] lg:text-[13px] tracking-[-0.02em] uppercase font-medium"
      >
        <span>PRMPT (R) 2026</span>
        <span>PRIVACY POLICY</span>
      </div>
    </>
  );
};
