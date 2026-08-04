import React, { useState } from 'react';
import { CustomCursor } from './components/CustomCursor';
import { HeroSection } from './components/HeroSection';
import { BlackPanelGallery } from './components/BlackPanelGallery';
import { Dashboard } from './components/Dashboard';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<'landing' | 'dashboard'>('landing');

  return (
    <div className="relative min-h-screen bg-black text-white selection:bg-white selection:text-black">
      {/* Custom mix-blend-mode cursor */}
      <CustomCursor />

      {currentView === 'landing' ? (
        <div id="scroll-spacer" className="relative user-select-none bg-white min-h-[500vh]">
          {/* Hero Section */}
          <HeroSection onOpenDashboard={() => setCurrentView('dashboard')} />

          {/* Black Panel Gallery Section */}
          <BlackPanelGallery onOpenDashboard={() => setCurrentView('dashboard')} />
        </div>
      ) : (
        <Dashboard onBackToLanding={() => setCurrentView('landing')} />
      )}
    </div>
  );
};

export default App;
