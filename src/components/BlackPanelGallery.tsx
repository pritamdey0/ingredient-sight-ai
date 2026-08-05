import React, { useEffect, useRef } from 'react';

const SLIDES = [
  {
    id: 1,
    headline: 'AI OCR Engine',
    subtitle: 'Optical Label Extraction & Recognition',
    description: 'Extracts ingredient labels from any cosmetic product packaging or image instantly using high-density optical recognition and deep neural analysis.',
    highlights: ['Multi-angle text recognition', 'Instant INCI dictionary matching', 'Auto-correct cosmetic trade names'],
    url: '/assets/ChatGPT Image Aug 4, 2026, 08_54_58 PM.png',
  },
  {
    id: 2,
    headline: 'Research Agent',
    subtitle: 'Autonomous Scientific Evidence Synthesizer',
    description: 'Searches and synthesizes scientific literature across PubMed, FDA safety monographs, CIR safety panels, and SCCS regulatory frameworks in real time.',
    highlights: ['PubMed & CIR database integration', 'Toxicological risk mapping', 'Real-time citation synthesis'],
    url: '/assets/f13e1096-7ba7-4eae-a30f-e1d5ffd6c605.png',
  },
  {
    id: 3,
    headline: 'Safety Analysis',
    subtitle: 'Multi-Tier Toxicological Risk Scoring',
    description: 'Computes toxicological hazard indices, EWG score approximations, endocrine disruption alerts, and contact allergen probability for every formulation.',
    highlights: ['EWG hazard score mapping', 'Dermal sensitization scoring', 'Cumulative chemical interaction audit'],
    url: '/assets/3c0b76e5-a2d4-4d46-ac78-689f3177eab0.png',
  },
  {
    id: 4,
    headline: 'Compound Structural Analysis',
    subtitle: 'INCI Molecular & Chemical Profiler',
    description: 'Generates detailed molecular structure diagrams, CAS registry lookup, chemical functional groups, and bio-accumulation parameters.',
    highlights: ['Molecular structure rendering', 'CAS registry cross-reference', 'Bio-accumulation metrics'],
    url: '/assets/ab45d017-dc89-48c7-9b89-eaae7de45fc1.png',
  },
  {
    id: 5,
    headline: 'Dermal Bio-Safety Assay',
    subtitle: 'Dermatological Irritation & Barrier Model',
    description: 'Evaluates epidermal absorption depth, irritation potential, comedogenicity index, and skin barrier disturbance metrics.',
    highlights: ['Epidermal penetration modeling', 'Comedogenicity rating', 'Barrier integrity assessment'],
    url: '/assets/01a8a669-0493-4265-8682-28edfb21f061.png',
  },
];

interface BlackPanelGalleryProps {
  onOpenDashboard: () => void;
}

export const BlackPanelGallery: React.FC<BlackPanelGalleryProps> = ({ onOpenDashboard }) => {
  const panelRef = useRef<HTMLDivElement | null>(null);
  const wrapperRef = useRef<HTMLDivElement | null>(null);

  // RAF Scroll Driver & 3D Diagonal Slide Physics
  useEffect(() => {
    let animationFrameId: number;

    const handleScroll = () => {
      const scrollY = window.scrollY;
      const vh = window.innerHeight || 800;
      const panel = panelRef.current;
      const wrapper = wrapperRef.current;
      const spacer = document.getElementById('scroll-spacer');
      const outroBuy = document.getElementById('outro-buy');
      const outroOverlay = document.getElementById('outro-overlay');

      if (!panel || !wrapper) return;

      const totalSlides = SLIDES.length;
      const slideScrollChunk = vh * 1.2;
      const maxScroll = slideScrollChunk * (totalSlides + 0.5);

      // Adjust total page scroll height dynamically
      if (spacer) {
        const totalHeight = vh + maxScroll + vh * 0.8;
        if (spacer.style.height !== `${totalHeight}px`) {
          spacer.style.height = `${totalHeight}px`;
        }
      }

      // Phase 1: scrollY 0 to vh -> Panel slides up from translateY(100vh) to 0
      if (scrollY <= vh) {
        const panelTranslate = Math.max(0, vh - scrollY);
        panel.style.transform = `translateY(${panelTranslate}px)`;
        wrapper.style.transform = `translateY(0px)`;
        if (outroOverlay) outroOverlay.style.opacity = '0';
        if (outroBuy) outroBuy.style.transform = 'scale(0)';
      } 
      // Phase 2: scrollY > vh -> Panel fixed at top
      else if (scrollY > vh && scrollY <= vh + maxScroll) {
        panel.style.transform = `translateY(0px)`;
        const wrapperTranslate = -(scrollY - vh);
        wrapper.style.transform = `translateY(${wrapperTranslate}px)`;
        if (outroOverlay) outroOverlay.style.opacity = '0';
        if (outroBuy) outroBuy.style.transform = 'scale(0)';
      } 
      // Phase 3: Outro
      else {
        panel.style.transform = `translateY(0px)`;
        wrapper.style.transform = `translateY(${-maxScroll}px)`;
        const outroProgress = Math.min(1, Math.max(0, (scrollY - vh - maxScroll) / (vh * 0.5)));
        if (outroOverlay) outroOverlay.style.opacity = `${outroProgress}`;
        if (outroBuy) outroBuy.style.transform = `scale(${outroProgress})`;
      }

      // Calculate 3D Diagonal Transformation for each slide element
      const slideElements = Array.from(document.querySelectorAll<HTMLElement>('.slide-3d'));

      slideElements.forEach((slideEl) => {
        const rect = slideEl.getBoundingClientRect();
        const centerY = rect.top + rect.height / 2;
        const targetCenterY = vh / 2;
        const dist = centerY - targetCenterY;

        // Distance normalized relative to viewport
        const normDist = dist / (vh * 0.7);
        const clampedDist = Math.max(-1.5, Math.min(1.5, normDist));

        // 3D Diagonal Matrix Transform Math
        const rotateX = clampedDist * -14; // degree
        const rotateY = clampedDist * 18;  // degree
        const rotateZ = clampedDist * -4;   // diagonal skew
        const translateZ = -Math.abs(clampedDist) * 220; // 3D depth shift
        const translateX = clampedDist * 60; // diagonal lateral shift
        const scale = Math.max(0.82, 1 - Math.abs(clampedDist) * 0.18);
        const opacity = Math.max(0.15, Math.min(1, 1 - Math.abs(clampedDist) * 0.75));

        slideEl.style.transform = `perspective(1200px) translate3d(${translateX}px, 0px, ${translateZ}px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) rotateZ(${rotateZ}deg) scale(${scale})`;
        slideEl.style.opacity = `${opacity}`;
      });

      animationFrameId = requestAnimationFrame(handleScroll);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();

    return () => {
      window.removeEventListener('scroll', handleScroll);
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <>
      <div
        ref={panelRef}
        className="fixed inset-0 bg-black z-10 overflow-hidden pointer-events-none transition-transform duration-75"
        style={{ transform: 'translateY(100vh)' }}
      >
        {/* Fixed Ambient Background Gradient Grid */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(16,185,129,0.15),rgba(255,255,255,0))] pointer-events-none" />

        {/* Main Scrolling Slides Container */}
        <div
          ref={wrapperRef}
          className="w-full px-4 sm:px-8 lg:px-16 pointer-events-auto pb-48"
          style={{ paddingTop: 'min(180px, 15vh)' }}
        >
          <div className="max-w-7xl mx-auto">
            {/* Gallery Intro Heading */}
            <div className="mb-20 text-center">
              <span className="text-xs uppercase tracking-widest text-emerald-400 font-mono block mb-3">
                INGREDIENTSIGHT AI // 3D SYSTEM MATRIX
              </span>
              <h2 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white">
                AUTONOMOUS SAFETY PIPELINE
              </h2>
              <p className="text-sm sm:text-base text-zinc-400 max-w-xl mx-auto mt-4 font-light">
                Scroll to explore each neural module in 3D diagonal transition view.
              </p>
            </div>

            {/* Individual 3D Diagonal Slides */}
            <div className="flex flex-col gap-28 lg:gap-40">
              {SLIDES.map((slide, idx) => {
                const isEven = idx % 2 === 1;

                return (
                  <div
                    key={slide.id}
                    className="slide-3d transition-transform duration-100 ease-out flex flex-col lg:flex-row items-center gap-10 lg:gap-16 bg-zinc-950/80 backdrop-blur-2xl border border-white/15 rounded-3xl p-6 sm:p-10 lg:p-12 shadow-[0_25px_60px_-15px_rgba(0,0,0,0.9)] cursor-pointer group hover:border-emerald-500/40"
                    style={{
                      transformStyle: 'preserve-3d',
                      willChange: 'transform, opacity',
                    }}
                    onClick={onOpenDashboard}
                  >
                    {/* 3D Image Frame Container */}
                    <div
                      className={`w-full lg:w-1/2 h-[280px] sm:h-[360px] lg:h-[420px] rounded-2xl overflow-hidden bg-black/90 border border-white/10 relative p-4 flex items-center justify-center shadow-2xl group-hover:border-emerald-500/30 transition-all duration-500 ${
                        isEven ? 'lg:order-2' : 'lg:order-1'
                      }`}
                    >
                      {/* Ambient Glow Backdrop behind image */}
                      <div className="absolute inset-0 bg-gradient-to-tr from-emerald-500/10 via-transparent to-purple-500/10 opacity-50 group-hover:opacity-100 transition-opacity" />
                      
                      <img
                        src={slide.url}
                        alt={slide.headline}
                        className="w-full h-full object-contain relative z-10 transition-transform duration-700 group-hover:scale-105 drop-shadow-2xl"
                        loading="lazy"
                      />
                    </div>

                    {/* Side-by-Side Content Side */}
                    <div
                      className={`w-full lg:w-1/2 flex flex-col justify-center ${
                        isEven ? 'lg:order-1 lg:text-right lg:items-end' : 'lg:order-2 lg:text-left lg:items-start'
                      }`}
                    >
                      <h3 className="text-2xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight leading-none">
                        {slide.headline}
                      </h3>
                      <p className="text-xs sm:text-sm font-mono text-emerald-400 mt-2 uppercase tracking-wider">
                        {slide.subtitle}
                      </p>

                      <p className="text-sm sm:text-base text-zinc-300 font-light leading-relaxed mt-5">
                        {slide.description}
                      </p>

                      {/* Highlight Bullet Points */}
                      <ul className={`mt-6 space-y-2 text-xs sm:text-sm text-zinc-400 font-mono ${isEven ? 'lg:items-end' : 'lg:items-start'}`}>
                        {slide.highlights.map((h, i) => (
                          <li key={i} className="flex items-center gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block" />
                            <span>{h}</span>
                          </li>
                        ))}
                      </ul>

                      {/* Interactive Dashboard Trigger CTA */}
                      <div className="mt-8">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onOpenDashboard();
                          }}
                          className="inline-flex items-center gap-3 text-xs sm:text-sm font-mono font-semibold text-black bg-white hover:bg-zinc-200 px-6 py-3 rounded-full uppercase tracking-wider transition-all duration-300 shadow-xl hover:scale-105"
                        >
                          <span>Explore in Dashboard</span>
                          <span>&rarr;</span>
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Final Call To Action Box */}
            <div className="mt-28 text-center bg-gradient-to-b from-zinc-900/90 to-zinc-950/95 border border-white/15 p-10 sm:p-16 rounded-3xl backdrop-blur-2xl shadow-2xl">
              <h3 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
                Ready to Analyze Your Products?
              </h3>
              <p className="text-zinc-400 text-sm sm:text-base mt-4 max-w-xl mx-auto font-light">
                Launch the IngredientSight AI Dashboard to test cosmetic labels with real-time toxicological reporting.
              </p>
              <button
                onClick={onOpenDashboard}
                className="mt-8 inline-flex items-center gap-3 bg-white text-black hover:bg-zinc-100 px-9 py-4.5 rounded-full font-bold text-sm sm:text-base tracking-tight uppercase transition-all duration-300 shadow-2xl hover:scale-105"
              >
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping" />
                <span>LAUNCH DASHBOARD NOW &rarr;</span>
              </button>
            </div>

            {/* Conclusion */}
            <div className="mt-20 mb-10 text-center max-w-2xl mx-auto">
              <p className="text-zinc-500 text-xs sm:text-sm font-light leading-relaxed">
                IngredientSight AI is built to give consumers and researchers a transparent, evidence-backed window into the chemistry of everyday cosmetic products. Every ingredient analyzed. Every risk surfaced. Every decision informed.
              </p>
              <div className="mt-6 w-12 h-px bg-zinc-700 mx-auto" />
            </div>

            {/* Footer */}
            <footer className="pb-16 text-center">
              <p className="text-zinc-600 text-[11px] font-mono uppercase tracking-widest">
                &copy; {new Date().getFullYear()} IngredientSight AI &mdash; All rights reserved.
              </p>
            </footer>
          </div>
        </div>
      </div>

      {/* Outro CTA Floating Button */}
      <div
        id="outro-buy"
        onClick={onOpenDashboard}
        className="fixed z-30 right-6 bottom-6 px-8 py-4 bg-white text-black rounded-full flex items-center justify-center cursor-pointer transition-transform duration-300 shadow-2xl hover:scale-110 font-bold uppercase tracking-wider text-sm sm:text-base"
        style={{
          transform: 'scale(0)',
        }}
      >
        <span>LAUNCH DASHBOARD &rarr;</span>
      </div>

      {/* Outro Overlay */}
      <div
        id="outro-overlay"
        className="fixed inset-0 pointer-events-none z-12 bg-black/60 opacity-0 transition-opacity"
      />
    </>
  );
};
