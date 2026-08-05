// Dock – macOS-style magnifying dock (Motion Primitives style)
import React, { createContext, useContext, useRef, useState } from 'react';
import { motion, useMotionValue, useSpring, useTransform, MotionValue } from 'framer-motion';

// ── Context ────────────────────────────────────────────────────────────────

const DOCK_DISTANCE = 110;
const MAX_MAGNIFY = 58;
const BASE_SIZE = 40;

interface DockContextValue {
  mouseX: MotionValue<number>;
}

const DockContext = createContext<DockContextValue | null>(null);

const useDock = () => {
  const ctx = useContext(DockContext);
  if (!ctx) throw new Error('Dock children must be inside <Dock>');
  return ctx;
};

// ── Dock Container ─────────────────────────────────────────────────────────

interface DockProps {
  children: React.ReactNode;
  className?: string;
}

export const Dock: React.FC<DockProps> = ({ children, className = '' }) => {
  const mouseX = useMotionValue<number>(Infinity);

  return (
    <DockContext.Provider value={{ mouseX }}>
      <motion.div
        onMouseMove={(e) => mouseX.set(e.pageX)}
        onMouseLeave={() => mouseX.set(Infinity)}
        className={`flex items-end gap-2 rounded-2xl border border-white/10 bg-white/10 backdrop-blur-xl px-4 py-2 shadow-2xl ${className}`}
      >
        {children}
      </motion.div>
    </DockContext.Provider>
  );
};

// ── Dock Item ──────────────────────────────────────────────────────────────

interface DockItemProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  href?: string;
}

export const DockItem: React.FC<DockItemProps> = ({ children, className = '', onClick, href }) => {
  const { mouseX } = useDock();
  const ref = useRef<HTMLDivElement>(null);

  const distance = useMotionValue(Infinity);

  // Update distance whenever mouseX changes – we need to know the element's centre
  React.useEffect(() => {
    const unsubscribe = mouseX.onChange((v) => {
      const el = ref.current;
      if (!el) return;
      const { left, width } = el.getBoundingClientRect();
      distance.set(Math.abs(v - (left + width / 2)));
    });
    return () => unsubscribe();
  }, [mouseX]);


  const widthTransform = useTransform(
    distance,
    [0, DOCK_DISTANCE],
    [BASE_SIZE + MAX_MAGNIFY, BASE_SIZE]
  );
  const width = useSpring(widthTransform, { stiffness: 300, damping: 26 });

  const [hovered, setHovered] = useState(false);

  const content = (
    <motion.div
      ref={ref}
      style={{ width, height: width }}
      onHoverStart={() => setHovered(true)}
      onHoverEnd={() => setHovered(false)}
      onClick={onClick}
      className={`relative flex cursor-pointer items-center justify-center rounded-full ${className}`}
    >
      {/* Label */}
      {hovered && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          className="absolute -top-9 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-md bg-black/80 backdrop-blur-sm px-2.5 py-1 text-[11px] font-medium text-white shadow-lg border border-white/10"
        >
          {React.Children.toArray(children).find(
            (child) => React.isValidElement(child) && child.type === DockLabel
          )}
        </motion.div>
      )}
      {/* Icon */}
      {React.Children.toArray(children).find(
        (child) => React.isValidElement(child) && child.type === DockIcon
      )}
    </motion.div>
  );

  if (href) {
    return (
      <a href={href} target="_blank" rel="noreferrer" className="block">
        {content}
      </a>
    );
  }

  return content;
};

// ── Dock Label (data only — rendered by DockItem) ─────────────────────────

interface DockLabelProps {
  children: React.ReactNode;
}

export const DockLabel: React.FC<DockLabelProps> = ({ children }) => {
  return <span>{children}</span>;
};

// ── Dock Icon ──────────────────────────────────────────────────────────────

interface DockIconProps {
  children: React.ReactNode;
}

export const DockIcon: React.FC<DockIconProps> = ({ children }) => {
  return <span className="flex h-full w-full items-center justify-center">{children}</span>;
};
