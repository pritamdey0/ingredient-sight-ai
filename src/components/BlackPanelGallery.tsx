import React, { useEffect, useRef, useState, useMemo } from 'react';

// 10 gallery images as specified in prompt
const GALLERY_IMAGES = [
  { id: 1, title: 'AI Cosmetic Ingredient Matrix', url: '/assets/ChatGPT Image Aug 4, 2026, 08_54_58 PM.png' },
  { id: 2, title: 'Compound Structural Analysis', url: '/assets/ab45d017-dc89-48c7-9b89-eaae7de45fc1.png' },
  { id: 3, title: 'Dermal Bio-Safety Assay', url: '/assets/01a8a669-0493-4265-8682-28edfb21f061.png' },
  { id: 4, title: 'Toxicity Evaluation Graph', url: '/assets/3c0b76e5-a2d4-4d46-ac78-689f3177eab0.png' },
  { id: 5, title: 'LangGraph Multi-Agent Synthesis', url: '/assets/f13e1096-7ba7-4eae-a30f-e1d5ffd6c605.png' },
  { id: 6, title: 'Archive Molecular Specimen A', url: '/assets/ChatGPT Image Aug 4, 2026, 08_54_58 PM.png' },
  { id: 7, title: 'Archive Molecular Specimen B', url: '/assets/ab45d017-dc89-48c7-9b89-eaae7de45fc1.png' },
  { id: 8, title: 'Archive Molecular Specimen C', url: '/assets/01a8a669-0493-4265-8682-28edfb21f061.png' },
  { id: 9, title: 'Archive Molecular Specimen D', url: '/assets/3c0b76e5-a2d4-4d46-ac78-689f3177eab0.png' },
  { id: 10, title: 'Archive Molecular Specimen E', url: '/assets/f13e1096-7ba7-4eae-a30f-e1d5ffd6c605.png' },
];

/**
 * Grid Layout Algorithm buildLayout(count, cols)
 */
function buildLayout(count: number, cols: number): number[][] {
  const rows: number[][] = [];
  let imgIndex = 0;
  let r = 0;

  while (imgIndex < count) {
    const rowCells = new Array(cols).fill(-1);
    const a = (r * 2 + (r % 2)) % cols;
    rowCells[a] = imgIndex;
    imgIndex++;

    if (r % 3 === 0 && imgIndex < count) {
      let b = (a + 2) % cols;
      if (b === a) b = (a + 1) % cols;
      rowCells[b] = imgIndex;
      imgIndex++;
    }

    rows.push(rowCells);
    r++;
  }

  return rows;
}

interface BlackPanelGalleryProps {
  onOpenDashboard: () => void;
}

export const BlackPanelGallery: React.FC<BlackPanelGalleryProps> = ({ onOpenDashboard }) => {
  const panelRef = useRef<HTMLDivElement | null>(null);
  const wrapperRef = useRef<HTMLDivElement | null>(null);
  const [cols, setCols] = useState(4);

  // Responsive column detection
  useEffect(() => {
    const updateCols = () => {
      const w = window.innerWidth;
      if (w < 640) setCols(2);
      else if (w < 1024) setCols(3);
      else setCols(4);
    };
    updateCols();
    window.addEventListener('resize', updateCols);
    return () => window.removeEventListener('resize', updateCols);
  }, []);

  const layoutRows = useMemo(() => buildLayout(GALLERY_IMAGES.length, cols), [cols]);

  // Main RAF Scroll Driver & Card Scaling Algorithm
  useEffect(() => {
    let animationFrameId: number;
    let lastSymbolTime = 0;
    const symbols = ['8', '$', '^^', '%', '/'];

    const handleScroll = () => {
      const scrollY = window.scrollY;
      const vh = window.innerHeight;
      const panel = panelRef.current;
      const wrapper = wrapperRef.current;
      const spacer = document.getElementById('scroll-spacer');
      const outroInfo = document.getElementById('outro-info');
      const outroBuy = document.getElementById('outro-buy');
      const outroOverlay = document.getElementById('outro-overlay');
      const outroFooter = document.getElementById('outro-footer');
      const circleSymbol = document.getElementById('circle-symbol');

      if (!panel || !wrapper) return;

      const wrapScrollHeight = wrapper.offsetHeight + vh * 0.4;
      const maxScroll = Math.max(0, wrapScrollHeight - vh);

      // Dynamically calculate spacer height
      if (spacer) {
        const totalHeight = vh + maxScroll + 2 * vh;
        if (spacer.style.height !== `${totalHeight}px`) {
          spacer.style.height = `${totalHeight}px`;
        }
      }

      // Randomize circle symbol (throttled 80ms)
      const now = performance.now();
      if (circleSymbol && now - lastSymbolTime > 80) {
        const randomSym = symbols[Math.floor(Math.random() * symbols.length)];
        circleSymbol.innerText = randomSym;
        lastSymbolTime = now;
      }

      // Phase 1: scrollY 0 to vh -> Panel slides up from translateY(100vh) to 0
      if (scrollY <= vh) {
        const panelTranslate = Math.max(0, vh - scrollY);
        panel.style.transform = `translateY(${panelTranslate}px)`;
        wrapper.style.transform = `translateY(0px)`;

        if (outroBuy) outroBuy.style.transform = 'scale(0)';
        if (outroOverlay) outroOverlay.style.opacity = '0';
        if (outroFooter) outroFooter.style.opacity = '0';
        if (outroInfo) outroInfo.style.transform = `translateY(0px)`;
      } 
      // Phase 2: scrollY > vh -> Panel fixed at top, inner wrapper translates up
      else if (scrollY > vh && scrollY <= vh + maxScroll) {
        panel.style.transform = `translateY(0px)`;
        const wrapperTranslate = -(scrollY - vh);
        wrapper.style.transform = `translateY(${wrapperTranslate}px)`;

        if (outroBuy) outroBuy.style.transform = 'scale(0)';
        if (outroOverlay) outroOverlay.style.opacity = '0';
        if (outroFooter) outroFooter.style.opacity = '0';
        if (outroInfo) outroInfo.style.transform = `translateY(0px)`;
      } 
      // Outro Phase: scrollY > vh + maxScroll -> Overlay fades in, view CTA button scales up
      else {
        panel.style.transform = `translateY(0px)`;
        wrapper.style.transform = `translateY(${-maxScroll}px)`;

        const outroProgress = Math.min(1, Math.max(0, (scrollY - vh - maxScroll) / (vh - 100)));

        if (outroOverlay) outroOverlay.style.opacity = `${outroProgress}`;
        if (outroFooter) outroFooter.style.opacity = `${outroProgress}`;
        if (outroBuy) outroBuy.style.transform = `scale(${outroProgress})`;

        if (outroInfo) {
          const offset = parseFloat(outroInfo.getAttribute('data-outro-offset') || '166');
          outroInfo.style.transform = `translateY(${-outroProgress * offset}px)`;
        }
      }

      // Per-card scaling calculation in RAF based on card vertical position
      const cards = Array.from(document.querySelectorAll<HTMLElement>('.bp-card'));
      cards.forEach((card) => {
        const rect = card.getBoundingClientRect();
        const top = rect.top;
        const bottom = rect.bottom;

        if (bottom <= 0 || top >= vh) {
          card.style.transform = 'scale(0)';
        } else {
          const enter = Math.min(1, (vh - top) / (vh * 0.6));
          const exit = Math.min(1, bottom / (vh * 0.4));
          const finalScale = Math.max(0, Math.min(enter, exit));
          card.style.transform = `scale(${finalScale})`;
        }
      });

      animationFrameId = requestAnimationFrame(handleScroll);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();

    return () => {
      window.removeEventListener('scroll', handleScroll);
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
    };
  }, [cols, layoutRows]);

  return (
    <div
      ref={panelRef}
      className="fixed inset-0 bg-black z-10 overflow-hidden pointer-events-none transition-transform duration-75"
      style={{ transform: 'translateY(100vh)' }}
    >
      {/* Inner Wrapper */}
      <div
        ref={wrapperRef}
        className="w-full px-4 sm:px-8 lg:px-12 pointer-events-auto"
        style={{ paddingTop: 'min(400px, 40vh)' }}
      >
        <div className="max-w-7xl mx-auto">
          {/* Header title inside black panel */}
          <div className="mb-16 text-center">
            <span className="text-xs uppercase tracking-widest text-zinc-500 font-mono block mb-2">
              PRMPT // INGREDIENTSIGHT ARCHIVE
            </span>
            <h2 className="text-3xl lg:text-5xl font-medium tracking-tight text-white">
              ANALYZED SPECIMEN MATRIX
            </h2>
          </div>

          {/* Grid Layout */}
          <div
            className="grid gap-4 sm:gap-6 lg:gap-8 mb-32"
            style={{
              gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))`,
            }}
          >
            {layoutRows.map((row, rIdx) =>
              row.map((cellImgIdx, cIdx) => {
                if (cellImgIdx === -1) {
                  return (
                    <div
                      key={`empty-${rIdx}-${cIdx}`}
                      className="aspect-[2/3] pointer-events-none"
                    />
                  );
                }

                const item = GALLERY_IMAGES[cellImgIdx];
                const isLeftHalf = cIdx < cols / 2;
                const transformOrigin = isLeftHalf ? 'right bottom' : 'left bottom';

                return (
                  <div
                    key={`card-${item.id}-${cellImgIdx}`}
                    className="bp-card aspect-[2/3] relative rounded-xl overflow-hidden group bg-zinc-900 border border-zinc-800/80 shadow-2xl cursor-pointer transition-all duration-300 hover:border-zinc-500"
                    style={{
                      transformOrigin,
                      transform: 'scale(0)',
                    }}
                    onClick={onOpenDashboard}
                  >
                    <img
                      src={item.url}
                      alt={item.title}
                      className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                      loading="lazy"
                    />
                    {/* Subtle Overlay with Title & ID */}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent opacity-80 group-hover:opacity-95 transition-opacity p-4 flex flex-col justify-end">
                      <span className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider mb-1">
                        SPECIMEN 00{item.id}
                      </span>
                      <span className="text-xs sm:text-sm font-medium text-white tracking-tight leading-tight">
                        {item.title}
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
