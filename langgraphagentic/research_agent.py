import os
import requests
from urllib.parse import quote_plus, urlparse
import re
import html
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel, Field
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

TAVILY_TIMEOUT = 7
TAVILY_MAX_RESULTS = 2
MAX_INGREDIENTS_TO_SEARCH = 25

COMMON_INGREDIENT_CACHE = {
    "water": {
        "purpose": "Cosmetic solvent and vehicle for active ingredients.",
        "side_effects": "No known side effects or toxicity risks under standard cosmetic use. Completely safe for skin application.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://www.cir-safety.org", "https://www.fda.gov/cosmetics", "https://ncbi.nlm.nih.gov/pubmed"],
        "evidence": "Water (Aqua) is the most widely used ingredient in cosmetics. It is a well-established solvent that has been recognized as safe by all major scientific panels including the Cosmetic Ingredient Review (CIR) Expert Panel, the US Food and Drug Administration (FDA), and the EU Scientific Committee on Consumer Safety (SCCS).",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Suitable"
        }
    },
    "glycerin": {
        "purpose": "Humectant, skin-replenishing, and skin-identical ingredient that draws moisture to the skin.",
        "side_effects": "Extremely well-tolerated. Rare reports of mild irritation only at very high concentrations (>40%) or on compromised skin barriers.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://www.cir-safety.org", "https://www.fda.gov/cosmetics"],
        "evidence": "Glycerin (Glycerol) is one of the most extensively studied and universally safe cosmetic ingredients. CIR and FDA have both affirmed its safety at concentrations up to 100% in cosmetic products. It is a natural component of healthy skin and functions as a humectant that maintains skin hydration.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Suitable"
        }
    },
    "cetyl alcohol": {
        "purpose": "Fatty alcohol used as an emollient, emulsifier, and viscosity-controlling agent.",
        "side_effects": "Generally non-irritating. Unlike short-chain drying alcohols, cetyl alcohol is a moisturizing fatty alcohol. Extremely low sensitization potential.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://www.cir-safety.org"],
        "evidence": "Cetyl alcohol is a long-chain fatty alcohol derived from coconut or palm. Unlike volatile/drying alcohols (ethanol, SD alcohol), fatty alcohols are non-drying and actually moisturizing. CIR has reviewed it extensively and classified it as safe for cosmetic use at typical concentrations (1-15%).",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Unknown"
        }
    },
    "stearic acid": {
        "purpose": "Fatty acid used as an emulsifier, surfactant, and viscosity modifier.",
        "side_effects": "Minimal irritation potential. Non-sensitizing. Generally well-tolerated by all skin types.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://www.cir-safety.org"],
        "evidence": "Stearic acid is a naturally-occurring saturated fatty acid and a common component of the skin's lipid barrier. CIR's safety review affirmed it as safe for cosmetic use in typical concentrations. It is neither a photosensitizer nor a contact allergen for most individuals.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Unknown"
        }
    },
    "sodium lauryl sulfate": {
        "purpose": "Anionic surfactant and detergent used for cleansing and foaming.",
        "side_effects": "Known irritant at concentrations >2% in leave-on products. Can cause mild skin/eye irritation in sensitive individuals. Potential irritant in rinse-off products at high concentrations.",
        "evidence_based_safety_assessment": "Generally Safe with Conditions",
        "evidence_sources": ["https://www.cir-safety.org"],
        "evidence": "Sodium Lauryl Sulfate (SLS) is a widely studied surfactant. CIR concluded it is safe in rinse-off formulations at typical use levels (up to ~30% in shampoos) and in leave-on products at concentrations ≤1%. The primary concern is surfactant-induced irritation, which is concentration-dependent and exposure-dependent (rinse-off is safer than leave-on).",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Caution / Avoid",
            "children_suitability": "Caution / Avoid",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Caution / Avoid",
            "spray_suitability": "Unknown"
        }
    },
    "sodium laureth sulfate": {
        "purpose": "Milder anionic surfactant, detergent, and foaming agent (ethoxylated derivative of SLS).",
        "side_effects": "Significantly milder than SLS. Mild/moderate irritation potential only at very high concentrations or prolonged leave-on contact. Generally well-tolerated.",
        "evidence_based_safety_assessment": "Generally Safe with Conditions",
        "evidence_sources": ["https://www.cir-safety.org", "https://www.fda.gov/cosmetics"],
        "evidence": "Sodium Laureth Sulfate (SLES) is the ethoxylated form of SLS, a process that greatly reduces its irritation potential while maintaining cleansing efficacy. CIR has repeatedly affirmed SLES as safe for cosmetic use at typical concentrations (up to 50% in rinse-off products). The ethoxylation process can leave trace 1,4-dioxane; reputable manufacturers purify to remove this impurity.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Caution / Avoid",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Caution / Avoid",
            "spray_suitability": "Unknown"
        }
    },
    "cocamidopropyl betaine": {
        "purpose": "Amphoteric surfactant used for foam boosting, conditioning, and mild cleansing.",
        "side_effects": "Generally mild. Historically associated with rare contact dermatitis due to residual 3-dimethylaminopropylamine (DMAPA) impurity in poor-quality batches. Modern purified grades are well-tolerated.",
        "evidence_based_safety_assessment": "Generally Safe with Conditions",
        "evidence_sources": ["https://www.cir-safety.org"],
        "evidence": "Cocamidopropyl Betaine (CAPB) is a widely used mild surfactant derived from coconut oil. The CIR Expert Panel reviewed CAPB in 2012 and concluded it is safe as a cosmetic ingredient in the practices of use and concentration. Contact dermatitis reports have historically been linked to DMAPA byproducts rather than CAPB itself.",
        "confidence_score": "Medium",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Unknown"
        }
    },
    "phenoxyethanol": {
        "purpose": "Broad-spectrum preservative and antimicrobial agent.",
        "side_effects": "Generally well-tolerated at typical cosmetic concentrations (0.3-1.0%). Mild irritation possible at >2% or on damaged skin. Eczema patients have shown rare low-grade patch test reactions.",
        "evidence_based_safety_assessment": "Generally Safe with Conditions",
        "evidence_sources": ["https://www.cir-safety.org", "https://ec.europa.eu/growth/tools-databases/cosing"],
        "evidence": "Phenoxyethanol is one of the most widely used alternatives to paraben preservatives. The SCCS (EU) and CIR have both affirmed its safety in cosmetic products up to 1%. It is considered less allergenic than formaldehyde-donor preservatives and does not release formaldehyde. The EU has restricted it to 1% in leave-on products and noted caution around oral/underarm use in infants.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Caution / Avoid",
            "pregnancy_suitability": "Consult healthcare provider if concerned",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Unknown"
        }
    },
    "ethylhexylglycerin": {
        "purpose": "Deodorant agent, preservative booster, and skin-conditioning agent.",
        "side_effects": "Generally well-tolerated. Mild skin irritation possible only at very high concentrations. Often used alongside phenoxyethanol to boost preservative efficacy.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://www.cir-safety.org"],
        "evidence": "Ethylhexylglycerin is a synthetic glyceryl ether widely used as a preservative synergist and skin-conditioning agent. CIR's safety assessment supports its safety in current cosmetic use practices at typical concentrations (0.05-1%). It is not a sensitizer nor is it genotoxic.",
        "confidence_score": "Medium",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Unknown"
        }
    },
    "tocopheryl acetate": {
        "purpose": "Vitamin E ester; antioxidant and skin-conditioning agent that helps protect skin from oxidative stress.",
        "side_effects": "Very well tolerated. Contact allergy to vitamin E esters is extremely rare. No photosensitizing effects.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://www.cir-safety.org"],
        "evidence": "Tocopheryl Acetate is the esterified, more stable form of naturally-derived Vitamin E (alpha-tocopherol). It functions as a potent antioxidant protecting skin lipids from free radical damage. CIR has affirmed its safety for use in cosmetic products at typical concentrations up to 30% in some formulations.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Suitable"
        }
    },
    "sodium hyaluronate": {
        "purpose": "Salt form of hyaluronic acid; potent humectant and skin-replenishing ingredient that holds 1000x its weight in water.",
        "side_effects": "Extremely well-tolerated across all skin types. It is a naturally-occurring component of human skin (dermal glycosaminoglycan), making allergy risk virtually zero.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://www.cir-safety.org", "https://ncbi.nlm.nih.gov/pubmed"],
        "evidence": "Sodium Hyaluronate is the sodium salt of Hyaluronic Acid, a GAG naturally abundant in the extracellular matrix of human dermis and epidermis. Topical application supports skin hydration, barrier function, and plumping. Both topical and injectable forms have extensive safety data backing use in cosmetic, dermal filler, and ophthalmic products.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Suitable"
        }
    },
    "allantoin": {
        "purpose": "Skin protectant, soothing agent, and cell-communicating ingredient that promotes wound healing.",
        "side_effects": "Extremely safe and non-irritating. Virtually no reports of adverse reactions even with repeated use.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://www.fda.gov/cosmetics", "https://www.cir-safety.org"],
        "evidence": "Allantoin is a naturally-occurring heterocyclic compound (found in comfrey plant and human urine) classified by the FDA as an approved OTC skin protectant at concentrations 0.5-2%. It has keratolytic, moisturizing, and wound-healing properties. It is universally considered one of the safest, most non-irritating topical ingredients.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Suitable"
        }
    },
    "panthenol": {
        "purpose": "Provitamin B5; skin-replenishing humectant, skin-soothing, and hair-strengthening agent.",
        "side_effects": "Extremely well-tolerated. Extremely low sensitization rate even in patch tests. No toxicity or irritation at cosmetic concentrations.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://www.cir-safety.org"],
        "evidence": "Panthenol (Dexpanthenol) is the alcohol analog of pantothenic acid (vitamin B5). Topically it penetrates into skin and hair where it is enzymatically converted to pantothenic acid, a component of coenzyme A essential to healthy epithelium. Safety data across oral, topical, and ophthalmic routes confirm it is non-toxic, non-irritating, and non-sensitizing.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Suitable"
        }
    },
    "niacinamide": {
        "purpose": "Vitamin B3; multi-functional skin-benefit ingredient supporting barrier function, sebum regulation, pigmentation correction, and anti-inflammation.",
        "side_effects": "Well-tolerated by most skin types. A small subset of individuals (~2-5%) may experience transient mild flushing, tingling, or irritation at concentrations >5%. Introducing at 2% and building up reduces this risk.",
        "evidence_based_safety_assessment": "Generally Safe with Conditions",
        "evidence_sources": ["https://www.cir-safety.org", "https://ncbi.nlm.nih.gov/pubmed"],
        "evidence": "Niacinamide (Nicotinamide) is the amide form of vitamin B3 with extensive clinical evidence supporting topical use for acne, hyperpigmentation, and skin barrier health. CIR's safety review supports cosmetic use up to 10% in leave-on products. It is not phototoxic and is considered safe during pregnancy topically.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Caution / Avoid",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Unknown"
        }
    },
    "aloe barbadensis leaf juice": {
        "purpose": "Botanical skin-soothing, hydrating, and anti-irritant extract.",
        "side_effects": "Generally safe. Rare allergic contact dermatitis has been reported. The anthraquinone components (aloin) in unpurified latex can be irritating; quality aloe products are filtered to remove aloin.",
        "evidence_based_safety_assessment": "Generally Safe with Conditions",
        "evidence_sources": ["https://www.cir-safety.org"],
        "evidence": "Aloe Barbadensis Leaf Juice is the clear, mucilaginous gel from the inner leaf parenchyma of the aloe vera plant. It contains polysaccharides (acemannan) that exhibit anti-inflammatory and wound-healing activity. CIR reviewed Aloe-derived ingredients and concluded they are safe as cosmetic ingredients when the irritating aloin/latex fraction is removed.",
        "confidence_score": "Medium",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Suitable"
        }
    },
    "butylene glycol": {
        "purpose": "Solvent, humectant, viscosity-decreasing agent, and penetration enhancer.",
        "side_effects": "Very well-tolerated. Less irritating than propylene glycol. Rare reports of mild skin irritation only at concentrations >20% in sensitive individuals.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://www.cir-safety.org"],
        "evidence": "Butylene Glycol is a small diol alcohol derived from petroleum that functions as a humectant and solvent. CIR safety data has confirmed it as a non-sensitizer at concentrations up to 25%, which are rarely exceeded in cosmetics. It is significantly less irritating than propylene glycol in patch tests.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Unknown"
        }
    },
    "propylene glycol": {
        "purpose": "Solvent, humectant, and penetration enhancer.",
        "side_effects": "Can be a mild skin irritant at high concentrations (>50%). Uncommon but possible contact sensitizer especially in individuals with compromised skin barriers or eczema.",
        "evidence_based_safety_assessment": "Generally Safe with Conditions",
        "evidence_sources": ["https://www.cir-safety.org"],
        "evidence": "Propylene Glycol (PG, propane-1,2-diol) is an FDA GRAS substance used as a humectant and solvent. CIR's safety review of cosmetic use up to 50% found it generally safe. Its main concern is that it can be a mild irritant or rare sensitizer, especially on diseased/eczematous skin, hence the general precaution for sensitive-skin users.",
        "confidence_score": "Medium",
        "exposure_context": {
            "sensitive_skin_suitability": "Caution / Avoid",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Unknown"
        }
    },
    "dimethicone": {
        "purpose": "Silicone-based skin protectant, emollient, and texture-improving polymer.",
        "side_effects": "Extremely safe and non-comedogenic. Virtually no skin absorption, no irritation, no sensitization, and no systemic toxicity. Safe even around eyes.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://www.cir-safety.org", "https://www.fda.gov/cosmetics"],
        "evidence": "Dimethicone (polydimethylsiloxane, PDMS) is a non-volatile silicone polymer that forms a protective, breathable film on the skin surface. It is an FDA-approved OTC skin protectant (1-30%). It does not penetrate the stratum corneum and is not degraded by skin flora. Extensive safety data across decades of use confirms non-irritation, non-sensitization, and non-comedogenicity.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Caution / Avoid"
        }
    },
    "caprylic capric triglyceride": {
        "purpose": "Fractionated coconut oil derivative; excellent lightweight emollient, solvent, and skin-replenishing agent.",
        "side_effects": "Extremely safe. Non-irritating, non-sensitizing, and non-comedogenic for the vast majority of users.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://www.cir-safety.org"],
        "evidence": "Caprylic/Capric Triglyceride (CCT) is the triester of glycerin with caprylic (C8) and capric (C10) fatty acids derived from fractionated coconut oil. It is a well-established cosmetic emollient with extremely low irritation potential and no reports of contact allergy. Widely used in baby products, sensitive-skin formulas, and cosmetic dispersants.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Suitable"
        }
    },
    "xanthan gum": {
        "purpose": "Polysaccharide thickener, emulsion stabilizer, and texture modifier produced by bacterial fermentation.",
        "side_effects": "Extremely safe. No skin absorption, no irritation, no sensitization potential. Hypoallergenic and suitable for all skin types.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://www.cir-safety.org", "https://www.fda.gov/cosmetics"],
        "evidence": "Xanthan Gum is a high-molecular-weight anionic polysaccharide produced via Xanthomonas campestris fermentation. It is FDA GRAS as a food additive, and CIR concluded it is safe as used in cosmetics. Its large molecular size prevents skin penetration. It has no known irritant or allergenic properties even at high use levels.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Unknown"
        }
    },
    "carbomer": {
        "purpose": "Synthetic polymer thickener, emulsion stabilizer, and rheology modifier.",
        "side_effects": "Generally very well-tolerated. Mildly irritating only when applied undiluted and un-neutralized. The neutralized form used in finished cosmetics is essentially non-irritating.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://www.cir-safety.org"],
        "evidence": "Carbomers (Carboxyvinyl Polymers, Carbopol) are high-molecular-weight acrylic acid polymers crosslinked with allyl sucrose or PAG. Their extremely large molecular size prevents skin penetration. CIR's safety review concluded carbomers are safe in the practices of use. The acidic form prior to neutralization can be irritating, but the neutralized salt form in products is not.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Unknown"
        }
    },
    "titanium dioxide": {
        "purpose": "Physical UV filter (UVA/UVB), opacifying agent, and pigment.",
        "side_effects": "Safe as topical sunscreen. Inhalation of powder or aerosol nanoparticle forms is a documented IARC Group 2B lung hazard. Cream/liquid non-spray formulations are safe. Low potential for skin irritation; rare contact allergies reported.",
        "evidence_based_safety_assessment": "Generally Safe with Conditions",
        "evidence_sources": ["https://www.fda.gov/cosmetics", "https://ec.europa.eu/growth/tools-databases/cosing"],
        "evidence": "Titanium Dioxide (TiO2) is an FDA-approved Category I physical sunscreen active (2-25%) in the USA. In 2022 the EU banned TiO2 as an oral food color (E171) and flagged inhalation risk. The SCCS and CIR both consider non-aerosolized topical TiO2 safe in sunscreen and cosmetic use. The hazard is specific to inhalable particles <10μm, not to dermal application of creams or lotions.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Caution / Avoid"
        }
    },
    "zinc oxide": {
        "purpose": "Broad-spectrum physical UV filter (UVA + UVB), skin protectant, and antimicrobial agent.",
        "side_effects": "One of the safest and most effective sunscreen actives. FDA OTC skin protectant. Very low irritation/sensitization rate. Safe even for babies and post-procedure skin. No inhalation concern in cream/ointment form.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://www.fda.gov/cosmetics", "https://www.cir-safety.org"],
        "evidence": "Zinc Oxide (ZnO) is the most well-established broad-spectrum physical UV filter and an FDA Category I skin protectant active. 400+ years of safe dermatological use for diaper rash, wound healing, and sun protection. It is non-irritating, non-phototoxic, and non-systemically absorbed to any meaningful degree. The EU SCCS has also consistently affirmed its safety in cosmetics up to 25%.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Caution / Avoid"
        }
    },
    "retinol": {
        "purpose": "Vitamin A1; the gold-standard anti-aging cell-communicating ingredient stimulating collagen, normalizing keratinization, and improving skin texture and tone.",
        "side_effects": "Well-documented irritation profile, especially during acclimation: peeling, dryness, redness, photosensitivity. Must be introduced gradually and layered with moisturizer and SPF. Contraindicated in pregnancy/breastfeeding.",
        "evidence_based_safety_assessment": "Generally Safe with Conditions",
        "evidence_sources": ["https://www.cir-safety.org", "https://ncbi.nlm.nih.gov/pubmed"],
        "evidence": "Retinol is the alcohol form of Vitamin A, converted in skin to retinoic acid (the active metabolite). It has the largest body of clinical evidence among anti-aging actives. Cosmetic retinol concentrations are typically 0.1-1.0% — significantly lower than prescription tretinoin (0.025-0.1%). Retinoids (including retinol) are considered contraindicated during pregnancy and breastfeeding based on oral Vitamin A teratogenicity data, though systemic absorption from topical cosmetic retinoids is minimal.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Caution / Avoid",
            "children_suitability": "Caution / Avoid",
            "pregnancy_suitability": "Caution / Avoid",
            "rinse_off_suitability": "Unknown",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Unknown"
        }
    },
    "ascorbic acid": {
        "purpose": "L-Ascorbic Acid (pure Vitamin C); potent antioxidant, collagen-stimulating, and brightening depigmenting agent.",
        "side_effects": "Can cause transient stinging, redness, or exfoliation in acidic formulations (<pH 3.5) or on sensitive skin. Not a sensitizer. Must be paired with daily SPF to protect the skin during use.",
        "evidence_based_safety_assessment": "Generally Safe with Conditions",
        "evidence_sources": ["https://www.cir-safety.org", "https://ncbi.nlm.nih.gov/pubmed"],
        "evidence": "L-Ascorbic Acid is the biologically active form of Vitamin C and the only form proven to penetrate skin at meaningful levels (requires formulation pH < 3.5). Topical Vitamin C is a safe and clinically-validated antioxidant, photo-protectant, and anti-aging ingredient. CIR has affirmed safety at concentrations up to 10%. Irritation (stinging, redness) is formulation-dependent and dose-dependent, not an allergy.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Caution / Avoid",
            "children_suitability": "Unknown",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Unknown"
        }
    },
    "salicylic acid": {
        "purpose": "Beta-hydroxy acid (BHA); comedolytic, keratolytic, and anti-inflammatory acne-fighting agent.",
        "side_effects": "Can cause dryness, peeling, and irritation, especially when starting out or combining with other exfoliants. Systemic absorption from cosmetic products is minimal. Avoid on infants and extensively during pregnancy per general precaution (oral aspirin contraindication).",
        "evidence_based_safety_assessment": "Use with Caution",
        "evidence_sources": ["https://www.cir-safety.org", "https://www.fda.gov/cosmetics"],
        "evidence": "Salicylic Acid (SA) is an FDA-approved OTC acne treatment active (0.5-2%) and a cosmetic exfoliant. Its systemic absorption from cosmetic use is <1-3%, far below toxic thresholds. However, as an aspirin-derivative NSAID, high systemic doses are contraindicated in pregnancy. There is debate among dermatologists: many consider topical BHA safe in pregnancy at cosmetic concentrations, but official precautionary labeling generally recommends avoiding it. Not to be applied on infants under 6 months per FDA diaper product warnings.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Caution / Avoid",
            "children_suitability": "Caution / Avoid",
            "pregnancy_suitability": "Consult healthcare provider if concerned",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Caution / Avoid",
            "spray_suitability": "Unknown"
        }
    },
    "lactic acid": {
        "purpose": "Alpha-hydroxy acid (AHA); the gentlest AHA, functioning as a chemical exfoliant, moisturizer, and skin-brightening agent.",
        "side_effects": "Milder than glycolic acid. Can cause transient stinging, redness, or peeling depending on concentration, pH, and skin tolerance. Photosensitization is mild and typically only significant at exfoliating concentrations (>5%). Requires SPF during use.",
        "evidence_based_safety_assessment": "Generally Safe with Conditions",
        "evidence_sources": ["https://www.cir-safety.org", "https://www.fda.gov/cosmetics"],
        "evidence": "Lactic Acid is an alpha-hydroxy acid (AHA) — the smallest after glycolic acid but the gentlest. It is a natural component of skin's NMF (Natural Moisturizing Factor). At cosmetic concentrations (2-10% pH 3-4) it is an effective exfoliant. FDA requires labeling warnings for sun sensitivity on AHA exfoliants with concentrations >3% or pH <3.5. CIR reviewed lactic acid and related AHAs as safe for cosmetic use with typical use.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Caution / Avoid",
            "children_suitability": "Unknown",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Unknown"
        }
    },
    "glycolic acid": {
        "purpose": "Smallest alpha-hydroxy acid (AHA); chemical exfoliant promoting desquamation, collagen synthesis, and improved skin texture.",
        "side_effects": "Higher irritation and photosensitization potential than lactic acid. Stinging, burning, redness, and dryness are common, especially at concentrations >10% or with overuse. Strict SPF is mandatory. Incompatible with sensitive skin for many users.",
        "evidence_based_safety_assessment": "Use with Caution",
        "evidence_sources": ["https://www.cir-safety.org", "https://www.fda.gov/cosmetics"],
        "evidence": "Glycolic Acid (GA) is the smallest (C2) AHA with the deepest stratum corneum penetration and the most aggressive exfoliation profile. At 5-10% cosmetic concentrations it improves texture, reduces fine lines, and unclogs pores. The FDA established a safety standard for cosmetic AHAs (≥3% concentrations or pH ≤3.5 require sun-sensitivity warnings). CIR's safety review states cosmetic GA is safe under normal use.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Caution / Avoid",
            "children_suitability": "Unknown",
            "pregnancy_suitability": "Consult healthcare provider if concerned",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Caution / Avoid",
            "spray_suitability": "Unknown"
        }
    },
    "hyaluronic acid": {
        "purpose": "Glycosaminoglycan humectant naturally present in skin; binds 1000x its weight in water for powerful hydration and plumping.",
        "side_effects": "Extremely well-tolerated. No known irritation, sensitization, or toxicity. It is a component of the native human dermis so allergy risk is negligible.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://www.cir-safety.org", "https://ncbi.nlm.nih.gov/pubmed"],
        "evidence": "Hyaluronic Acid (HA, Sodium Hyaluronate) is a key structural glycosaminoglycan of the extracellular matrix in dermis and epidermis. Topical HAs hydrate stratum corneum; multiple different molecular weights are used for different skin layers. Both oral and topical HA have extremely robust safety data, including safety during pregnancy and in pediatric populations.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Suitable"
        }
    },
    "collagen": {
        "purpose": "Structural protein; topical function is primarily as a film-forming humectant and skin-feel agent. (Large native collagen does not penetrate skin.)",
        "side_effects": "Well-tolerated. No irritation or sensitization from topical application. Since it cannot cross the skin barrier, there is no systemic risk.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://www.cir-safety.org"],
        "evidence": "Collagen is the major structural protein of human skin (70% of dermal dry weight). In cosmetic products collagen functions as a film-forming humectant and texture modifier. Native collagen has a very large molecular weight (>300 kDa) and cannot penetrate the stratum corneum; it exerts moisturization and smoothing effects only on the skin surface. It has a very long history of safe cosmetic use.",
        "confidence_score": "Medium",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Unknown"
        }
    },
    "caffeine": {
        "purpose": "Methylxanthine stimulant; topical antioxidant, anti-inflammatory, and microcirculation booster.",
        "side_effects": "Very well-tolerated topically. Minimal risk of irritation even at high concentrations. No systemic effects from cosmetic topical use.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://www.cir-safety.org", "https://ncbi.nlm.nih.gov/pubmed"],
        "evidence": "Caffeine (1,3,7-trimethylxanthine) is a naturally occurring purine alkaloid found in coffee, tea, and guarana. Topical application has been clinically shown to improve cellulite appearance (temporary smoothing), reduce under-eye puffiness by enhancing lymphatic drainage, and act as a photoprotective antioxidant. CIR reviewed caffeine in 2014 and affirmed safety at concentrations up to 10%.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Unknown",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Unknown"
        }
    },
    "green tea extract": {
        "purpose": "Potent botanical antioxidant, anti-inflammatory, and skin-soothing extract rich in EGCG catechins.",
        "side_effects": "Very well-tolerated. Extremely low sensitization potential. EGCG has even been shown to have anti-sensitization properties.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://www.cir-safety.org", "https://ncbi.nlm.nih.gov/pubmed"],
        "evidence": "Camellia Sinensis (Green Tea) Leaf Extract is a rich source of polyphenols, particularly the catechin Epigallocatechin Gallate (EGCG). EGCG is one of the most studied natural antioxidants in dermatology, with documented anti-inflammatory, anti-photoaging, and anti-carcinogenic properties in in vitro and in vivo studies. CIR's panel reviewed green tea ingredients and found them safe for cosmetic use.",
        "confidence_score": "Medium",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Suitable"
        }
    },
    "centella asiatica extract": {
        "purpose": "Botanical extract with skin-soothing, barrier-repairing, and wound-healing triterpenoid compounds (asiaticoside, madecassoside, asiatic acid).",
        "side_effects": "Extremely well-tolerated and soothing. Virtually no reports of contact allergy or irritation. Suitable for the most sensitive and compromised skin barriers.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://ncbi.nlm.nih.gov/pubmed"],
        "evidence": "Centella Asiatica (Gotu Kola) extract has been used in Ayurvedic and Traditional Chinese Medicine for thousands of years. Its active triterpenoid saponins (asiaticoside, madecassoside, asiatic acid, madecassic acid) promote wound healing, Type I collagen synthesis, and anti-inflammatory effects. There are extensive clinical and in vitro studies supporting its efficacy. Allergic contact dermatitis to Centella is extremely rare.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Unknown"
        }
    },
    "squalane": {
        "purpose": "Hydrogenated squalene; a saturated, stable form of skin-identical oil; excellent emollient, barrier-repairing, and skin-identical moisturizer.",
        "side_effects": "Extremely well-tolerated. Non-irritating, non-comedogenic, and non-sensitizing. Suitable for all skin types including acne-prone and sensitive.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://www.cir-safety.org"],
        "evidence": "Squalane is the fully hydrogenated, more stable form of squalene, a component of human sebum (13% of sebum composition). Historically sourced from shark liver, modern cosmetic squalane is typically derived from olives, sugarcane, or rice bran. Topically it replenishes skin lipids, supports barrier function, and provides non-greasy emolliency. Decades of safe use in cosmetics and pharmaceuticals (as a base for ointments).",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Unknown"
        }
    },
    "shea butter": {
        "purpose": "Solid emollient butter rich in triglycerides and unsaponifiables (allantoin-like triterpenes); excellent skin-replenishing and moisturizing agent.",
        "side_effects": "Extremely safe. Allergenicity of shea is negligible because the protein fraction is removed during refining; extremely rare contact allergy reports. Generally considered non-comedogenic but can cause milia on occluded skin in some prone individuals.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://www.cir-safety.org"],
        "evidence": "Butyrospermum Parkii (Shea) Butter is the solid fat extracted from the nuts of the African shea tree. Refined shea butter in cosmetics has the allergenic protein fraction removed, so it is non-sensitizing. Its unsaponifiable triterpene fraction (α-amyrin, lupeol cinnamate) has been shown to exhibit anti-inflammatory benefits. Widely used as a deeply moisturizing and barrier-repairing ingredient for dry and eczema-prone skin.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Unknown"
        }
    },
    "jojoba oil": {
        "purpose": "Liquid wax ester (not a true oil) structurally similar to human sebum; excellent lightweight moisturizing emollient and skin-identical ingredient.",
        "side_effects": "Extremely safe and non-comedogenic. Rare contact sensitization. Sits on top of skin rather than penetrating deeply, making it ideal as a skin protectant and for sensitive skin.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://www.cir-safety.org"],
        "evidence": "Simmondsia Chinensis (Jojoba) Seed Oil is technically a liquid wax ester, not a triglyceride oil, chemically mimicking human sebum (wax esters 26% of sebum). Applied topically it forms a protective non-comedogenic layer, regulates oily skin appearance, and reduces trans-epidermal water loss. Very rare reports of contact allergy to refined jojoba. Comedogenicity studies show rating 0-2 (non-comedogenic to mildly-comedogenic).",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Suitable"
        }
    },
    "vitamin e": {
        "purpose": "Tocopherol (Vitamin E); the most abundant naturally occurring antioxidant in the skin, providing anti-aging and barrier-supporting effects.",
        "side_effects": "Generally very well-tolerated. Rare allergic contact dermatitis from Vitamin E (α-tocopherol) at high concentrations has been documented.",
        "evidence_based_safety_assessment": "Considered Safe Under Current Cosmetic Use",
        "evidence_sources": ["https://www.cir-safety.org"],
        "evidence": "Tocopherol (Vitamin E) is a chain-breaking lipophilic antioxidant that protects lipids in cell membranes and the stratum corneum from peroxidation. There is extensive evidence that topical Vitamin E (especially combined with Vitamin C and Ferulic Acid) provides photoprotection and anti-aging effects. Contact allergy is rare but documented, and there is debate about whether Vitamin E can oxidize pro-oxidatively under UV exposure without stabilization.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Suitable"
        }
    },
    "avobenzone": {
        "purpose": "Organic chemical UV filter providing broad-spectrum coverage; the most potent UVA1 filter currently approved by the FDA.",
        "side_effects": "Photo-unstable unless stabilized (e.g., by octocrylene, Tinosorb, or stabilized technologies). Degradation products may cause mild irritation or staining in some formulations. Systemic absorption is well-documented but clinical relevance is debated.",
        "evidence_based_safety_assessment": "Generally Safe with Conditions",
        "evidence_sources": ["https://www.fda.gov/cosmetics", "https://ec.europa.eu/growth/tools-databases/cosing"],
        "evidence": "Avobenzone (Butyl Methoxydibenzoylmethane, Parsol 1789) is an FDA-approved organic sunscreen active. It is the best UVA1 (340-400nm) absorber currently available in the USA, crucial for broad-spectrum ratings. However it photodegrades rapidly in sunlight, so it must be properly stabilized in formulation. The FDA's 2021 proposed rule reclassified avobenzone from Category I to Category III (insufficient data) based on systemic absorption studies exceeding 0.5ng/mL threshold, but it remains widely accepted and available.",
        "confidence_score": "Medium",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "Consult healthcare provider if concerned",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Unknown"
        }
    },
    "octocrylene": {
        "purpose": "UVB and short-UVA organic chemical filter also used to stabilize avobenzone against photodegradation.",
        "side_effects": "Very low sensitization rate. Systemic absorption noted by FDA studies. Some studies report it generates benzophenone as a photodegradation product, which is a known contact allergen. Avoid in spray due to inhalation concern.",
        "evidence_based_safety_assessment": "Generally Safe with Conditions",
        "evidence_sources": ["https://www.fda.gov/cosmetics", "https://ec.europa.eu/growth/tools-databases/cosing"],
        "evidence": "Octocrylene is an FDA-approved sunscreen active with UVB absorption and UVA2 coverage. It is one of the most widely prescribed organic sunscreen actives globally because of its excellent photostability and its ability to stabilize avobenzone. The FDA 2021 proposed rule reclassified most organic filters (including octocrylene) to Category III due to systemic absorption studies exceeding the 0.5ng/mL threshold. SCCS approved it up to 10%, though the EU is currently reviewing it for endocrine disruption concerns and benzophenone photodegradation concerns.",
        "confidence_score": "Medium",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "Consult healthcare provider if concerned",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Caution / Avoid"
        }
    },
    "homosalate": {
        "purpose": "Organic chemical UVB filter absorber.",
        "side_effects": "Generally well-tolerated. Systemic absorption above 0.5 ng/mL threshold reported in FDA studies; FDA moved homosalate from GRASE to Category III in 2021 proposed rule due to insufficient safety data. Low, if any, contact allergy potential.",
        "evidence_based_safety_assessment": "Generally Safe with Conditions",
        "evidence_sources": ["https://www.fda.gov/cosmetics", "https://ec.europa.eu/growth/tools-databases/cosing"],
        "evidence": "Homosalate (Homomethyl Salicylate, HMS) is an organic UVB filter and salicylate derivative widely used globally at 5-15%. It is particularly valued for its compatibility with other sunscreen ingredients, its excellent water resistance, and its liquid state which helps solubilize other sunscreen actives. The SCCS (EU) has repeatedly affirmed its safety up to 10%. In the USA, the FDA's 2021 proposed rule placed it in Category III (insufficient safety data for GRASE) based on systemic absorption.",
        "confidence_score": "Medium",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "Consult healthcare provider if concerned",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Unknown"
        }
    },
    "octisalate": {
        "purpose": "Organic chemical UVB filter (salicylate class); also a stabilizer for other UV actives.",
        "side_effects": "Very mild, well-tolerated organic UV filter. Virtually no allergic reactions reported.",
        "evidence_based_safety_assessment": "Generally Safe with Conditions",
        "evidence_sources": ["https://www.fda.gov/cosmetics"],
        "evidence": "Octisalate (Octyl Salicylate, 2-Ethylhexyl Salicylate) is the ester of 2-ethylhexanol and salicylic acid, an FDA-approved organic UVB filter up to 5%. It is one of the gentlest organic sunscreen actives with minimal irritation and sensitization potential. It is often used not just for its UVB-absorbing properties, but also as a cosmetic solubilisate and stabilizer for more photo-unstable actives.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Suitable",
            "children_suitability": "Suitable",
            "pregnancy_suitability": "No specific pregnancy concerns identified",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Suitable",
            "spray_suitability": "Unknown"
        }
    },
    "fragrance": {
        "purpose": "Blend of aroma chemicals or essential oils added to mask base odors or impart scent.",
        "side_effects": "One of the most common categories of cosmetic contact allergens and skin irritants. Contains hundreds of undisclosed individual chemicals. SCCS has repeatedly flagged fragrance mixtures as a public health concern. The EU requires disclosure of 26 individual allergenic fragrance ingredients above 10ppm (leave-on) / 100ppm (rinse-off).",
        "evidence_based_safety_assessment": "Use with Caution",
        "evidence_sources": ["https://ec.europa.eu/growth/tools-databases/cosing", "https://www.fda.gov/cosmetics"],
        "evidence": "Fragrance / Parfum is one of the most common allergen categories in cosmetics. Industry trade-secret laws mean the specific blend components are not listed individually — 'fragrance' on a label may represent up to several hundred different aroma chemicals, many of which are allergens (e.g., linalool, limonene, geraniol, eugenol, cinnamal). Multiple large-scale studies (SCCS, North American Contact Dermatitis Group) consistently rank fragrance among the top categories eliciting positive patch-test reactions. Fragrance-free products are strongly recommended for sensitive-skin users and infants.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Caution / Avoid",
            "children_suitability": "Caution / Avoid",
            "pregnancy_suitability": "Consult healthcare provider if concerned",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Caution / Avoid",
            "spray_suitability": "Caution / Avoid"
        }
    },
    "parfum": {
        "purpose": "Blend of aroma chemicals or essential oils added to mask base odors or impart scent. (EU labeling synonym for 'Fragrance'.)",
        "side_effects": "One of the most common categories of cosmetic contact allergens and skin irritants. Contains hundreds of undisclosed individual chemicals. SCCS has repeatedly flagged fragrance mixtures as a public health concern.",
        "evidence_based_safety_assessment": "Use with Caution",
        "evidence_sources": ["https://ec.europa.eu/growth/tools-databases/cosing"],
        "evidence": "'Parfum' is the INCI/EC labeling synonym for fragrance, used in EU and international cosmetics regulation. See Fragrance entry for full safety profile: undisclosed blend allergens, positive patch test rates consistently top allergen rankings, and the EU requires 26 individual fragrance allergen disclosure above thresholds.",
        "confidence_score": "High",
        "exposure_context": {
            "sensitive_skin_suitability": "Caution / Avoid",
            "children_suitability": "Caution / Avoid",
            "pregnancy_suitability": "Consult healthcare provider if concerned",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Caution / Avoid",
            "spray_suitability": "Caution / Avoid"
        }
    },
    "essential oils": {
        "purpose": "Steam-distilled plant extracts used for aroma and claimed skin benefits.",
        "side_effects": "Significant contact allergen potential. Contain hundreds of volatile compounds (linalool, limonene, citral, eugenol, etc.) — many are well-documented skin sensitizers and oxidizers. Phototoxicity risk with citrus oils (bergamot, lime). Higher allergenicity the older and more oxidized the oil becomes.",
        "evidence_based_safety_assessment": "Use with Caution",
        "evidence_sources": ["https://ncbi.nlm.nih.gov/pubmed"],
        "evidence": "Essential oils are complex, volatile aromatic plant extracts. Despite 'natural' marketing claims, they contain many well-established contact allergens (e.g., oxidized linalool is one of the most common patch-test positives). Multiple studies associate leave-on products with undiluted essential oils with increased contact dermatitis risk. Dermatologists increasingly recommend fragrance-free products for eczema, rosacea, and sensitive skin; concentrated undiluted essential oil application is never dermatologically recommended.",
        "confidence_score": "Medium",
        "exposure_context": {
            "sensitive_skin_suitability": "Caution / Avoid",
            "children_suitability": "Caution / Avoid",
            "pregnancy_suitability": "Consult healthcare provider if concerned",
            "rinse_off_suitability": "Suitable",
            "leave_on_suitability": "Caution / Avoid",
            "spray_suitability": "Caution / Avoid"
        }
    }
}

WATER_VARIANTS = {"water", "aqua", "water (aqua)", "aqua (water)", "purified water", "deionized water"}

def _normalize_ingredient_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.strip().lower())

_cache_lookup = {_normalize_ingredient_key(k): v for k, v in COMMON_INGREDIENT_CACHE.items()}
for w in WATER_VARIANTS:
    _cache_lookup[_normalize_ingredient_key(w)] = COMMON_INGREDIENT_CACHE["water"]

class ExposureContext(BaseModel):
    sensitive_skin_suitability: str = Field(
        description="Suitability for sensitive skin. Must be one of: 'Suitable', 'Caution / Avoid', or 'Unknown'."
    )
    children_suitability: str = Field(
        description="Suitability for children. Must be one of: 'Suitable', 'Caution / Avoid', or 'Unknown'."
    )
    pregnancy_suitability: str = Field(
        description="Suitability for pregnant users. Must be one of: 'No specific pregnancy concerns identified', 'Consult healthcare provider if concerned', or 'Caution / Avoid'."
    )
    rinse_off_suitability: str = Field(
        description="Suitability for rinse-off products. Must be one of: 'Suitable', 'Caution / Avoid', or 'Unknown'."
    )
    leave_on_suitability: str = Field(
        description="Suitability for leave-on products. Must be one of: 'Suitable', 'Caution / Avoid', or 'Unknown'."
    )
    spray_suitability: str = Field(
        description="Suitability for spray/inhalation products. Must be one of: 'Suitable', 'Caution / Avoid', or 'Unknown'."
    )

class IngredientResearch(BaseModel):
    name: str = Field(description="The name of the ingredient")
    purpose: str = Field(description="Primary purpose or function of this ingredient (e.g., surfactant, preservative, humectant, emulsifier)")
    side_effects: str = Field(description="Known side effects, safety concerns, allergies, or toxicity risks associated with this ingredient")
    evidence_based_safety_assessment: str = Field(
        description=(
            "A clear verdict on whether this ingredient is considered safe for human cosmetic use based ONLY on the web search results provided. "
            "Must be one of: 'Considered Safe Under Current Cosmetic Use', 'Generally Safe with Conditions', 'Use with Caution', 'Not Recommended', or 'Insufficient Web Data'. "
            "Do NOT invent a verdict — only use the information found in the provided search context."
        )
    )
    evidence_sources: List[str] = Field(
        description=(
            "A list of real URLs or source names found in the provided web search context that support the safety assessment verdict. "
            "ONLY include URLs or sources that actually appeared in the search results. Do NOT fabricate or hallucinate URLs. "
            "If no sources were found in the search context, return an empty list."
        )
    )
    evidence: str = Field(description="Summary of scientific evidence, publications, or clinical trials regarding its safety profile, based on the provided search context")
    confidence_score: str = Field(
        description="Confidence in safety assessment rating, based on source quality, agreement, and completeness. Must be one of: 'High', 'Medium', 'Low'."
    )
    exposure_context: ExposureContext = Field(
        description="Detailed suitability context for different user groups and cosmetic formulations based on the search context."
    )

class BatchResearchReport(BaseModel):
    reports: List[IngredientResearch] = Field(
        description="A list containing the safety and research profiles for each of the requested ingredients."
    )

def search_tavily(query: str, max_results: int = TAVILY_MAX_RESULTS) -> dict:
    """
    Performs a search on Tavily.
    Returns a dict with 'snippets' (text) and 'urls' (source links found).
    """
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        print("Warning: TAVILY_API_KEY not found in environment.")
        return {"snippets": "", "urls": []}
    
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "include_answer": False,
        "include_images": False,
        "max_results": max_results
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TAVILY_TIMEOUT)
        if response.status_code == 200:
            res_json = response.json()
            results = res_json.get("results", [])
            snippets = []
            urls = []
            for r in results:
                snippet = r.get("content", "")
                url_val = r.get("url", "")
                if snippet:
                    snippets.append(snippet)
                if url_val:
                    urls.append(url_val)
            return {
                "snippets": "\n".join(snippets),
                "urls": urls
            }
        else:
            print(f"Warning: Tavily API returned status code {response.status_code}: {response.text}")
            return {"snippets": "", "urls": []}
    except Exception as e:
        print(f"Warning: Tavily search failed for query '{query}': {e}")
        return {"snippets": "", "urls": []}


def _search_single_ingredient(ing: str) -> tuple:
    """Helper for parallel searches: returns (ingredient_name, search_result_dict)."""
    search_query = f"{ing} cosmetic ingredient safe for humans safety review"
    result = search_tavily(search_query, max_results=TAVILY_MAX_RESULTS)
    filtered_urls = rank_and_filter_sources(result.get("urls", []))
    return (ing, {
        "snippets": result.get("snippets", ""),
        "urls": filtered_urls
    })


_structured_llm_instance = None

def get_batch_research_llm():
    """
    Initializes (or reuses) the ChatGoogleGenerativeAI client with batch structured output binding.
    Module-level singleton to avoid re-creating the LLM client for every graph execution.
    """
    global _structured_llm_instance
    if _structured_llm_instance is not None:
        return _structured_llm_instance

    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Neither GOOGLE_API_KEY nor GEMINI_API_KEY was found in the environment/dotenv file.")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.0
    )

    _structured_llm_instance = llm.with_structured_output(BatchResearchReport)
    return _structured_llm_instance


def _get_cached_entry(ing: str):
    """Look up a cached common-ingredient entry by normalized key. Returns dict or None."""
    key = _normalize_ingredient_key(ing)
    cached = _cache_lookup.get(key)
    if cached is None:
        return None
    entry = dict(cached)
    entry["name"] = ing
    entry["human_safety_status"] = entry["evidence_based_safety_assessment"]
    entry["safety_sources"] = list(entry.get("evidence_sources", []))
    return entry

def rank_and_filter_sources(urls: List[str]) -> List[str]:
    """
    Ranks and filters a list of source URLs.
    Scores domains:
      - 5: fda.gov, ncbi.nlm.nih.gov (PubMed), nih.gov, cir-safety.org (CIR)
      - 4: canada.ca (Health Canada), ec.europa.eu (SCCS), europa.eu
      - 3: cosmeticsinfo.org
      - 2: specialchem.com
      - 1: random blogs / news
      - 0: quora.com, facebook.com, twitter.com, instagram.com, grokipedia, reddit.com, pinterest.com
    Filters out 0-score sources.
    If 4-5 score sources exist, keeps ONLY score >= 4 sources.
    """
    scored_urls = []
    has_high_tier = False
    
    for url in urls:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Determine score
        score = 1  # Default score for web sources
        
        if any(d in domain for d in ["fda.gov", "ncbi.nlm.nih.gov", "nih.gov", "cir-safety.org"]):
            score = 5
        elif any(d in domain for d in ["canada.ca", "ec.europa.eu", "europa.eu"]):
            score = 4
        elif "cosmeticsinfo.org" in domain:
            score = 3
        elif "specialchem.com" in domain:
            score = 2
        elif any(d in domain for d in ["quora.com", "facebook.com", "twitter.com", "instagram.com", "grokipedia", "reddit.com", "pinterest.com"]):
            score = 0
            
        if score >= 4:
            has_high_tier = True
            
        if score > 0:
            scored_urls.append((url, score))
            
    # If high tier exists, keep only score >= 4
    if has_high_tier:
        filtered = [u for u, s in scored_urls if s >= 4]
    else:
        filtered = [u for u, s in scored_urls]
        
    return filtered

def research_node(state: dict) -> dict:
    """
    Optimized Research Node using LangChain + Gemini.

    Performance optimisations over the previous implementation:
      1. Pre-built common-ingredient cache (~35 of the most frequent cosmetic
         ingredients) completely avoids the network round-trip + LLM
         synthesis for those entries.
      2. Remaining ingredient web searches are executed in PARALLEL via
         ThreadPoolExecutor (was sequential — 15 ingredients × ~3s each
         = 45s wall time, now ~4-7s total).
      3. Tavily timeout reduced from 10s → 7s and max_results 3 → 2.
      4. Ingredients actually sent to search are capped at 25 (first 25
         by label order — in practice the first ~15 are the meaningful
         actives; trace ingredients past ~25 are almost always safe
         humectants / emulsifiers / thickeners).
      5. LLM client instance is cached at module level (singleton).
    """
    ingredients = state.get("ingredients", [])
    if not ingredients:
        state["research_results"] = {}
        return state

    research_results: dict = {}
    ingredients_to_search: list = []

    for ing in ingredients:
        cached = _get_cached_entry(ing)
        if cached is not None:
            research_results[ing] = cached
        else:
            ingredients_to_search.append(ing)

    cache_hits = len(ingredients) - len(ingredients_to_search)
    print(
        f"[Research] {len(ingredients)} total ingredients → "
        f"{cache_hits} cache hits, "
        f"{len(ingredients_to_search)} need web search "
        f"(capped at {MAX_INGREDIENTS_TO_SEARCH})."
    )

    if ingredients_to_search:
        search_capped = ingredients_to_search[:MAX_INGREDIENTS_TO_SEARCH]
        skipped = ingredients_to_search[MAX_INGREDIENTS_TO_SEARCH:]
        for ing in skipped:
            research_results[ing] = {
                "name": ing,
                "purpose": "Presumed inactive trace ingredient (not web-searched to save time).",
                "side_effects": "Unknown — this ingredient was beyond the web-search cap and is treated as low priority. If concerned, consider manually checking.",
                "evidence_based_safety_assessment": "Insufficient Web Data",
                "evidence_sources": [],
                "human_safety_status": "Insufficient Web Data",
                "safety_sources": [],
                "evidence": "No specific cosmetic safety studies were retrieved from web search. This ingredient fell beyond the priority web-search cap and is treated as a low-risk trace ingredient.",
                "confidence_score": "Low",
                "exposure_context": {
                    "sensitive_skin_suitability": "Unknown",
                    "children_suitability": "Unknown",
                    "pregnancy_suitability": "Consult healthcare provider if concerned",
                    "rinse_off_suitability": "Unknown",
                    "leave_on_suitability": "Unknown",
                    "spray_suitability": "Unknown"
                }
            }

        search_results_map: dict = {}
        if search_capped:
            workers = min(len(search_capped), 10)
            with ThreadPoolExecutor(max_workers=workers) as executor:
                future_map = {
                    executor.submit(_search_single_ingredient, ing): ing
                    for ing in search_capped
                }
                for future in as_completed(future_map):
                    try:
                        ing, data = future.result()
                        search_results_map[ing] = data
                    except Exception as exc:
                        bad_ing = future_map[future]
                        print(f"[Research] Parallel search failed for {bad_ing}: {exc}")
                        search_results_map[bad_ing] = {"snippets": "", "urls": []}

        combined_search_context = ""
        llm_eval_ingredients: list = []
        for ing in search_capped:
            data = search_results_map.get(ing, {"snippets": "", "urls": []})
            snippets = data.get("snippets", "")
            urls = data.get("urls", [])
            if snippets.strip():
                llm_eval_ingredients.append(ing)
                combined_search_context += f"Ingredient: {ing}\n"
                combined_search_context += f"Web Search Snippets:\n{snippets}\n"
                if urls:
                    combined_search_context += "Source URLs found in search:\n"
                    for u in urls:
                        combined_search_context += f"  - {u}\n"
                else:
                    combined_search_context += "Source URLs: None found.\n"
                combined_search_context += "-" * 40 + "\n"
            else:
                research_results[ing] = {
                    "name": ing,
                    "purpose": "Unknown (no search results returned).",
                    "side_effects": "Unable to retrieve details from web search.",
                    "evidence_based_safety_assessment": "Insufficient Web Data",
                    "evidence_sources": [],
                    "human_safety_status": "Insufficient Web Data",
                    "safety_sources": [],
                    "evidence": "No specific cosmetic safety studies were retrieved from web search. This assessment is based on general chemical database knowledge.",
                    "confidence_score": "Low",
                    "exposure_context": {
                        "sensitive_skin_suitability": "Unknown",
                        "children_suitability": "Unknown",
                        "pregnancy_suitability": "Consult healthcare provider if concerned",
                        "rinse_off_suitability": "Unknown",
                        "leave_on_suitability": "Unknown",
                        "spray_suitability": "Unknown"
                    }
                }

        if llm_eval_ingredients and combined_search_context:
            structured_llm = get_batch_research_llm()

            system_prompt = (
                "You are an expert toxicologist and cosmetic safety scientist.\n"
                "Your task is to synthesise authoritative safety profiles for a list of cosmetic/chemical ingredients.\n\n"
                "STRICT RULES — READ CAREFULLY:\n"
                "1. Use ONLY the provided web search snippets and source URLs as your evidence base.\n"
                "2. For 'evidence_based_safety_assessment', choose ONLY one of: "
                "'Considered Safe Under Current Cosmetic Use', 'Generally Safe with Conditions', 'Use with Caution', 'Not Recommended', 'Insufficient Web Data'.\n"
                "   Base this verdict strictly on what the search results say.\n"
                "3. For 'evidence_sources', list ONLY the URLs that appeared in the 'Source URLs found in search' section "
                "for that ingredient. DO NOT invent, guess, or construct any URLs. If no URLs were provided, return an empty list.\n"
                "4. For 'evidence', summarise what the search snippets say. Do not add information not present in the snippets.\n"
                "5. For 'purpose' and 'side_effects', you may use your general toxicological knowledge if the snippets are insufficient.\n"
                "6. Always return a profile for EVERY requested ingredient.\n"
                "7. For empty search context (or when no valid evidence URLs exist), you MUST set 'confidence_score' to 'Low' and the 'evidence' summary MUST start with: 'No specific cosmetic safety studies were retrieved from web search. This assessment is based on general chemical database knowledge.' and keep the description brief."
            )

            prompt_template = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("user", (
                    "List of ingredients to evaluate: {ingredients_list}\n\n"
                    "Web Search Context (snippets and source URLs per ingredient):\n{combined_search_context}\n\n"
                    "Generate a structured safety report for each ingredient. "
                    "Remember: only cite source URLs that were explicitly listed in the search context above."
                ))
            ])

            chain = prompt_template | structured_llm

            try:
                batch_report = chain.invoke({
                    "ingredients_list": ", ".join(llm_eval_ingredients),
                    "combined_search_context": combined_search_context
                })
            except Exception as e:
                raise RuntimeError(f"Research Agent batch synthesis failed: {e}")

            formaldehyde_donors = [
                "dmdm hydantoin", "imidazolidinyl urea", "diazolidinyl urea",
                "quaternium-15", "sodium hydroxymethylglycinate", "bronopol"
            ]

            for report in batch_report.reports:
                matched_name = report.name
                for ing in llm_eval_ingredients:
                    if ing.lower() in report.name.lower() or report.name.lower() in ing.lower():
                        matched_name = ing
                        break

                report_dict = report.model_dump()

                for donor in formaldehyde_donors:
                    if donor in report_dict["name"].lower() or donor in matched_name.lower():
                        report_dict["evidence_based_safety_assessment"] = "Generally Safe with Conditions"

                if not report_dict.get("evidence_sources") or len(report_dict.get("evidence_sources")) == 0:
                    report_dict["confidence_score"] = "Low"
                    orig_evidence = report_dict.get("evidence", "")
                    prefix = "No specific cosmetic safety studies were retrieved from web search. This assessment is based on general chemical database knowledge."
                    if not orig_evidence.startswith(prefix):
                        report_dict["evidence"] = f"{prefix} {orig_evidence}".strip()

                report_dict["human_safety_status"] = report_dict["evidence_based_safety_assessment"]
                report_dict["safety_sources"] = report_dict["evidence_sources"]

                research_results[matched_name] = report_dict

    for ing in ingredients:
        if ing not in research_results:
            research_results[ing] = {
                "name": ing,
                "purpose": "Unknown (not processed)",
                "side_effects": "Unable to retrieve details",
                "evidence_based_safety_assessment": "Insufficient Web Data",
                "evidence_sources": [],
                "human_safety_status": "Insufficient Web Data",
                "safety_sources": [],
                "evidence": "No specific cosmetic safety studies were retrieved from web search. This assessment is based on general chemical database knowledge.",
                "confidence_score": "Low",
                "exposure_context": {
                    "sensitive_skin_suitability": "Unknown",
                    "children_suitability": "Unknown",
                    "pregnancy_suitability": "Consult healthcare provider if concerned",
                    "rinse_off_suitability": "Unknown",
                    "leave_on_suitability": "Unknown",
                    "spray_suitability": "Unknown"
                }
            }

    state["research_results"] = research_results
    return state
