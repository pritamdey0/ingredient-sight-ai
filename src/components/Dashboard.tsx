import React, { useState } from 'react';
import { 
  ShieldCheck, 
  AlertTriangle, 
  FileText, 
  UploadCloud, 
  ArrowLeft, 
  Sparkles, 
  CheckCircle2, 
  Activity, 
  Search, 
  Cpu, 
  Download,
  Info,
  Beaker,
  ChevronRight
} from 'lucide-react';

interface DashboardProps {
  onBackToLanding: () => void;
}

// Sample pre-analyzed datasets for quick demonstration & offline mode
const DEMO_PRODUCTS = [
  {
    id: 'sample-1',
    name: 'Hydrating Botanical Cleansing Gel',
    brand: 'AURA Archive',
    category: 'Cosmetic / Cleanser',
    image: '/assets/ChatGPT Image Aug 4, 2026, 08_54_58 PM.png',
    ocr_text: 'INGREDIENTS: Aqua/Water/Eau, Glycerin, Sodium Cocoyl Glycinate, Niacinamide, Hyaluronic Acid, Phenoxyethanol, Ethylhexylglycerin, Salicylic Acid, Fragrance (Parfum).',
    ingredients: ['Water', 'Glycerin', 'Sodium Cocoyl Glycinate', 'Niacinamide', 'Hyaluronic Acid', 'Phenoxyethanol', 'Ethylhexylglycerin', 'Salicylic Acid', 'Fragrance'],
    safety_analysis: {
      overall_score: 92,
      risk_level: 'Low Risk',
      summary: 'Formula demonstrates exceptional dermatological safety profile. High concentration of skin-identical hydrating agents and anti-inflammatory Niacinamide.',
      warnings: [
        'Contains Fragrance (Parfum) which may cause mild sensitivity in compromised skin barriers.',
        'Contains Salicylic Acid (BHA 0.5%); exercise caution if combining with strong retinoids.'
      ],
      recommendations: [
        'Safe for daily morning and evening cleansing.',
        'Perform a 24-hour patch test if diagnosed with rosacea or severe eczema.'
      ],
      breakdown: [
        { name: 'Water (Aqua)', ewg: 1, role: 'Solvent', safety: 'Safe' },
        { name: 'Glycerin', ewg: 1, role: 'Humectant', safety: 'Safe' },
        { name: 'Niacinamide (Vitamin B3)', ewg: 1, role: 'Barrier Support', safety: 'Safe' },
        { name: 'Hyaluronic Acid', ewg: 1, role: 'Deep Hydration', safety: 'Safe' },
        { name: 'Salicylic Acid', ewg: 3, role: 'Exfoliant / Exfoliating BHA', safety: 'Caution' },
        { name: 'Phenoxyethanol', ewg: 2, role: 'Preservative (<1%)', safety: 'Safe' },
        { name: 'Fragrance (Parfum)', ewg: 4, role: 'Sensitizer', safety: 'Caution' },
      ]
    }
  },
  {
    id: 'sample-2',
    name: 'Cellular Renew Peptide Serum',
    brand: 'PRMPT Specimen 02',
    category: 'Serum / Anti-Aging',
    image: '/assets/ab45d017-dc89-48c7-9b89-eaae7de45fc1.png',
    ocr_text: 'INGREDIENTS: Aqua, Butylene Glycol, Palmitoyl Pentapeptide-4, Copper Tripeptide-1, Allantoin, Panthenol, Methylparaben, Propylparaben, Sodium Hydroxide.',
    ingredients: ['Aqua', 'Butylene Glycol', 'Palmitoyl Pentapeptide-4', 'Copper Tripeptide-1', 'Allantoin', 'Panthenol', 'Methylparaben', 'Propylparaben'],
    safety_analysis: {
      overall_score: 74,
      risk_level: 'Moderate Caution',
      summary: 'High efficacy peptide formulation with soothing Panthenol. Contains alkyl parabens as preservatives which warrant consumer review for endocrine disruption concerns.',
      warnings: [
        'Contains Methylparaben & Propylparaben (EWG Risk Score 4-6).',
        'Sodium Hydroxide used for pH adjustment; potential mild mucosal irritant if un-buffered.'
      ],
      recommendations: [
        'Avoid applying immediately post-chemical peel or microneedling.',
        'Store in a cool, dark location to maintain peptide stability.'
      ],
      breakdown: [
        { name: 'Aqua', ewg: 1, role: 'Solvent', safety: 'Safe' },
        { name: 'Palmitoyl Pentapeptide-4', ewg: 1, role: 'Collagen Stimulator', safety: 'Safe' },
        { name: 'Copper Tripeptide-1', ewg: 1, role: 'Tissue Repair', safety: 'Safe' },
        { name: 'Panthenol (Pro-Vitamin B5)', ewg: 1, role: 'Soothing', safety: 'Safe' },
        { name: 'Propylparaben', ewg: 6, role: 'Preservative (Paraben)', safety: 'Hazard' },
        { name: 'Methylparaben', ewg: 4, role: 'Preservative (Paraben)', safety: 'Caution' },
      ]
    }
  }
];

export const Dashboard: React.FC<DashboardProps> = ({ onBackToLanding }) => {
  const [selectedProduct, setSelectedProduct] = useState(DEMO_PRODUCTS[0]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentStep, setCurrentStep] = useState<number>(5);
  const [customFile, setCustomFile] = useState<File | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'breakdown' | 'agent-graph' | 'raw-report'>('overview');

  const agents = [
    { id: 1, name: 'OCR Agent', icon: Search, desc: 'Optical Character Recognition & Label Text Extraction' },
    { id: 2, name: 'Ingredient Agent', icon: Beaker, desc: 'INCI Normalization & Botanical Chemical Mapping' },
    { id: 3, name: 'Research Agent', icon: Cpu, desc: 'ECHA / CIR / PubMed Toxicology Scientific Lookup' },
    { id: 4, name: 'Safety Agent', icon: ShieldCheck, desc: 'EWG Scoring & Dermatological Risk Assessment' },
    { id: 5, name: 'Report Agent', icon: FileText, desc: 'Explainable Markdown & Consumer Report Generator' },
  ];

  // Simulating live 5-agent LangGraph analysis execution
  const handleAnalyzeUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setCustomFile(file);
      startAnalysisPipeline(file.name);
    }
  };

  const startAnalysisPipeline = (fileName: string) => {
    setIsAnalyzing(true);
    setCurrentStep(1);

    const stepInterval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev >= 5) {
          clearInterval(stepInterval);
          setIsAnalyzing(false);
          // Set uploaded result
          setSelectedProduct({
            id: 'custom-upload',
            name: `Analyzed Specimen: ${fileName}`,
            brand: 'Uploaded Label Image',
            category: 'Custom Product Scan',
            image: URL.createObjectURL(customFile || new Blob()),
            ocr_text: 'INGREDIENTS: Aqua, Caprylic/Capric Triglyceride, Squalane, Ceramide NP, Tocopherol, Retinol (0.3%), BHT, Benzyl Alcohol, Parfum.',
            ingredients: ['Aqua', 'Caprylic/Capric Triglyceride', 'Squalane', 'Ceramide NP', 'Tocopherol', 'Retinol', 'BHT', 'Parfum'],
            safety_analysis: {
              overall_score: 81,
              risk_level: 'Safe with Active Retinoid Caution',
              summary: 'Barrier-repairing lipid matrix featuring Ceramide NP and Pure Squalane. Contains potent Retinol (0.3%) which promotes cellular turnover.',
              warnings: [
                'Retinol requires gradual acclimatization and strict daytime SPF protection.',
                'Contains BHT preservative; low risk at cosmetic threshold concentrations.'
              ],
              recommendations: [
                'Introduce 2 nights per week initially.',
                'Always follow up with broad-spectrum SPF 50+ during daytime.'
              ],
              breakdown: [
                { name: 'Squalane', ewg: 1, role: 'Skin Identical Lipid', safety: 'Safe' },
                { name: 'Ceramide NP', ewg: 1, role: 'Barrier Repair', safety: 'Safe' },
                { name: 'Retinol (0.3%)', ewg: 3, role: 'Cellular Turnover Active', safety: 'Caution' },
                { name: 'Tocopherol (Vitamin E)', ewg: 1, role: 'Antioxidant', safety: 'Safe' },
                { name: 'BHT', ewg: 4, role: 'Antioxidant Preservative', safety: 'Caution' },
              ]
            }
          });
          return 5;
        }
        return prev + 1;
      });
    }, 900);
  };

  const downloadReport = (format: 'md' | 'json') => {
    const text = format === 'json' 
      ? JSON.stringify(selectedProduct, null, 2)
      : `# INGREDIENTSIGHT AI REPORT: ${selectedProduct.name}\n\n**Brand:** ${selectedProduct.brand}\n**Safety Score:** ${selectedProduct.safety_analysis.overall_score}/100\n\n## Summary\n${selectedProduct.safety_analysis.summary}\n\n## Normalized Ingredients\n${selectedProduct.ingredients.join(', ')}`;
    
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedProduct.name.toLowerCase().replace(/\s+/g, '_')}_report.${format}`;
    a.click();
  };

  return (
    <div className="min-h-screen bg-black text-white font-['Inter_Tight',sans-serif] pb-24 selection:bg-white selection:text-black">
      {/* Top Header Navigation */}
      <header className="sticky top-0 z-40 bg-black/80 backdrop-blur-md border-b border-zinc-800 px-6 lg:px-12 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={onBackToLanding}
            className="flex items-center gap-2 text-xs font-mono text-zinc-400 hover:text-white transition-colors bg-zinc-900 px-3 py-1.5 rounded-md border border-zinc-800"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>RETURN TO ARCHIVE</span>
          </button>
          <div className="h-4 w-[1px] bg-zinc-800 hidden sm:block" />
          <h1 className="text-lg font-medium tracking-tight text-white flex items-center gap-2">
            <span>INGREDIENTSIGHT AI</span>
            <span className="text-[10px] font-mono bg-zinc-800 text-zinc-300 px-2 py-0.5 rounded uppercase">
              v1.0.4 LangGraph
            </span>
          </h1>
        </div>

        {/* Quick Action CTAs */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => downloadReport('md')}
            className="flex items-center gap-1.5 text-xs font-medium bg-zinc-900 hover:bg-zinc-800 text-zinc-200 border border-zinc-800 px-3.5 py-2 rounded-lg transition-all"
          >
            <Download className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">EXPORT REPORT (.MD)</span>
          </button>

          <label className="flex items-center gap-1.5 text-xs font-medium bg-white hover:bg-zinc-200 text-black px-4 py-2 rounded-lg cursor-pointer transition-all shadow-md">
            <UploadCloud className="w-4 h-4" />
            <span>ANALYZE LABEL</span>
            <input type="file" accept="image/*" onChange={handleAnalyzeUpload} className="hidden" />
          </label>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-6 lg:px-12 pt-8">
        
        {/* LangGraph 5-Agent Execution Progress Bar */}
        <section className="mb-10 bg-zinc-950 border border-zinc-800 rounded-2xl p-6 relative overflow-hidden">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-zinc-400 animate-pulse" />
              <span className="text-xs font-mono text-zinc-400 uppercase tracking-wider">
                LangGraph StateGraph Execution Pipeline
              </span>
            </div>
            {isAnalyzing && (
              <span className="text-xs font-mono text-emerald-400 animate-pulse flex items-center gap-2">
                <Activity className="w-3.5 h-3.5" />
                PROCESSING NODE {currentStep}/5...
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
            {agents.map((agent) => {
              const Icon = agent.icon;
              const isActive = currentStep === agent.id;
              const isCompleted = currentStep > agent.id;

              return (
                <div
                  key={agent.id}
                  className={`p-3.5 rounded-xl border transition-all relative ${
                    isActive
                      ? 'bg-zinc-900 border-white text-white shadow-lg'
                      : isCompleted
                      ? 'bg-zinc-900/50 border-zinc-800 text-zinc-300'
                      : 'bg-zinc-950 border-zinc-900 text-zinc-600'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-mono uppercase tracking-widest text-zinc-400">
                      STEP 0{agent.id}
                    </span>
                    {isCompleted ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    ) : (
                      <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-zinc-500'}`} />
                    )}
                  </div>
                  <h4 className="text-xs font-semibold tracking-tight mb-1">{agent.name}</h4>
                  <p className="text-[10px] text-zinc-500 line-clamp-2 leading-snug">{agent.desc}</p>

                  {/* Active node highlight bar */}
                  {isActive && (
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-white rounded-b-xl animate-pulse" />
                  )}
                </div>
              );
            })}
          </div>
        </section>

        {/* Demo Selector / Upload Banner */}
        <section className="mb-8 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-zinc-900/40 p-4 rounded-xl border border-zinc-800">
          <div className="flex items-center gap-3">
            <span className="text-xs font-mono text-zinc-400 uppercase">SELECT SPECIMEN:</span>
            <div className="flex flex-wrap gap-2">
              {DEMO_PRODUCTS.map((prod) => (
                <button
                  key={prod.id}
                  onClick={() => setSelectedProduct(prod)}
                  className={`text-xs px-3 py-1.5 rounded-lg border transition-all ${
                    selectedProduct.id === prod.id
                      ? 'bg-white text-black font-semibold border-white'
                      : 'bg-zinc-900 text-zinc-400 border-zinc-800 hover:border-zinc-700'
                  }`}
                >
                  {prod.name}
                </button>
              ))}
            </div>
          </div>

          <div className="text-xs font-mono text-zinc-500">
            CURRENT: <span className="text-zinc-300 font-semibold">{selectedProduct.category}</span>
          </div>
        </section>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-6 border-b border-zinc-800 mb-8 text-sm font-medium">
          <button
            onClick={() => setActiveTab('overview')}
            className={`pb-3 transition-colors border-b-2 ${
              activeTab === 'overview'
                ? 'border-white text-white'
                : 'border-transparent text-zinc-500 hover:text-zinc-300'
            }`}
          >
            SAFETY OVERVIEW
          </button>
          <button
            onClick={() => setActiveTab('breakdown')}
            className={`pb-3 transition-colors border-b-2 ${
              activeTab === 'breakdown'
                ? 'border-white text-white'
                : 'border-transparent text-zinc-500 hover:text-zinc-300'
            }`}
          >
            INGREDIENT MATRIX ({selectedProduct.ingredients.length})
          </button>
          <button
            onClick={() => setActiveTab('agent-graph')}
            className={`pb-3 transition-colors border-b-2 ${
              activeTab === 'agent-graph'
                ? 'border-white text-white'
                : 'border-transparent text-zinc-500 hover:text-zinc-300'
            }`}
          >
            RAW OCR & LOGS
          </button>
        </div>

        {/* Tab 1: Safety Overview */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column: Specimen Image & Safety Gauge */}
            <div className="lg:col-span-1 flex flex-col gap-6">
              <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 relative overflow-hidden group">
                <div className="aspect-[4/3] rounded-xl overflow-hidden mb-4 bg-black border border-zinc-800">
                  <img
                    src={selectedProduct.image}
                    alt={selectedProduct.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                </div>
                <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest block mb-1">
                  {selectedProduct.brand}
                </span>
                <h3 className="text-xl font-medium tracking-tight text-white mb-1">
                  {selectedProduct.name}
                </h3>
                <span className="text-xs text-zinc-400">{selectedProduct.category}</span>
              </div>

              {/* Safety Score Card */}
              <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 flex flex-col items-center justify-center text-center">
                <span className="text-xs font-mono text-zinc-400 uppercase tracking-widest mb-3">
                  OVERALL DERMATOLOGICAL SAFETY
                </span>
                
                <div className="relative w-32 h-32 flex items-center justify-center my-2">
                  {/* Circular Score Gauge */}
                  <svg viewBox="0 0 36 36" className="w-full h-full transform -rotate-90">
                    <path
                      className="text-zinc-800 stroke-current"
                      strokeWidth="3.5"
                      fill="none"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                    <path
                      className={`${
                        selectedProduct.safety_analysis.overall_score >= 85
                          ? 'text-white'
                          : selectedProduct.safety_analysis.overall_score >= 70
                          ? 'text-zinc-300'
                          : 'text-amber-400'
                      } stroke-current`}
                      strokeDasharray={`${selectedProduct.safety_analysis.overall_score}, 100`}
                      strokeWidth="3.5"
                      strokeLinecap="round"
                      fill="none"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                  </svg>
                  <div className="absolute flex flex-col items-center">
                    <span className="text-3xl font-bold text-white tracking-tight">
                      {selectedProduct.safety_analysis.overall_score}
                    </span>
                    <span className="text-[10px] text-zinc-400 uppercase font-mono">/ 100</span>
                  </div>
                </div>

                <div className="mt-3 px-3 py-1 bg-zinc-800/80 rounded-full border border-zinc-700 text-xs font-medium text-zinc-200 uppercase tracking-wider">
                  {selectedProduct.safety_analysis.risk_level}
                </div>
              </div>
            </div>

            {/* Right Column: AI Analysis Summary, Warnings, Recommendations */}
            <div className="lg:col-span-2 flex flex-col gap-6">
              {/* AI Executive Summary */}
              <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-3">
                  <ShieldCheck className="w-5 h-5 text-white" />
                  <h3 className="text-base font-semibold tracking-tight text-white">
                    AI Safety Synthesis & Explanation
                  </h3>
                </div>
                <p className="text-sm text-zinc-300 leading-relaxed font-normal">
                  {selectedProduct.safety_analysis.summary}
                </p>
              </div>

              {/* Warnings Card */}
              <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-4 text-amber-400">
                  <AlertTriangle className="w-5 h-5" />
                  <h3 className="text-base font-semibold tracking-tight text-white">
                    Sensitization & Irritation Warnings
                  </h3>
                </div>
                <ul className="space-y-3">
                  {selectedProduct.safety_analysis.warnings.map((warn, idx) => (
                    <li key={idx} className="flex items-start gap-3 text-xs text-zinc-300 leading-relaxed">
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 flex-shrink-0" />
                      <span>{warn}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Consumer Recommendations Card */}
              <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-4 text-white">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  <h3 className="text-base font-semibold tracking-tight text-white">
                    Dermatological Recommendations
                  </h3>
                </div>
                <ul className="space-y-3">
                  {selectedProduct.safety_analysis.recommendations.map((rec, idx) => (
                    <li key={idx} className="flex items-start gap-3 text-xs text-zinc-300 leading-relaxed">
                      <ChevronRight className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Ingredient Breakdown */}
        {activeTab === 'breakdown' && (
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden">
            <div className="p-6 border-b border-zinc-800 flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold tracking-tight text-white">
                  INCI Normalized Ingredient Breakdown
                </h3>
                <p className="text-xs text-zinc-400">
                  Chemical role classification and EWG hazard benchmark scoring
                </p>
              </div>
              <span className="text-xs font-mono text-zinc-400 bg-zinc-800 px-3 py-1 rounded-md">
                TOTAL: {selectedProduct.safety_analysis.breakdown.length} COMPOUNDS
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-zinc-300">
                <thead className="bg-zinc-950 text-zinc-400 uppercase font-mono text-[10px] tracking-wider border-b border-zinc-800">
                  <tr>
                    <th className="px-6 py-3.5">Chemical / Botanical Name</th>
                    <th className="px-6 py-3.5">Formulation Role</th>
                    <th className="px-6 py-3.5 text-center">EWG Risk Score</th>
                    <th className="px-6 py-3.5 text-right">Safety Assessment</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800">
                  {selectedProduct.safety_analysis.breakdown.map((item, i) => (
                    <tr key={i} className="hover:bg-zinc-800/40 transition-colors">
                      <td className="px-6 py-4 font-medium text-white flex items-center gap-2">
                        <Beaker className="w-3.5 h-3.5 text-zinc-400" />
                        <span>{item.name}</span>
                      </td>
                      <td className="px-6 py-4 text-zinc-400">{item.role}</td>
                      <td className="px-6 py-4 text-center">
                        <span className={`inline-block px-2.5 py-0.5 rounded font-mono text-[11px] font-semibold ${
                          item.ewg <= 2
                            ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                            : item.ewg <= 4
                            ? 'bg-amber-950 text-amber-400 border border-amber-800'
                            : 'bg-rose-950 text-rose-400 border border-rose-800'
                        }`}>
                          Score {item.ewg}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <span className={`text-xs font-medium uppercase ${
                          item.safety === 'Safe'
                            ? 'text-emerald-400'
                            : item.safety === 'Caution'
                            ? 'text-amber-400'
                            : 'text-rose-400'
                        }`}>
                          {item.safety}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tab 3: Raw OCR & LangGraph Logs */}
        {activeTab === 'agent-graph' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-white uppercase font-mono">
                  Raw OCR Extraction Output
                </h3>
                <span className="text-[10px] font-mono text-zinc-400">NODE 1: ocr_agent</span>
              </div>
              <div className="bg-black p-4 rounded-xl border border-zinc-800 font-mono text-xs text-zinc-300 leading-relaxed overflow-x-auto">
                {selectedProduct.ocr_text}
              </div>
            </div>

            <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-white uppercase font-mono">
                  Normalized INCI Array
                </h3>
                <span className="text-[10px] font-mono text-zinc-400">NODE 2: ingredient_agent</span>
              </div>
              <pre className="bg-black p-4 rounded-xl border border-zinc-800 font-mono text-xs text-emerald-400 leading-relaxed overflow-x-auto">
                {JSON.stringify(selectedProduct.ingredients, null, 2)}
              </pre>
            </div>
          </div>
        )}

      </main>
    </div>
  );
};
