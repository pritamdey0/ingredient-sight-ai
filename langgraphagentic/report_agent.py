import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def extract_safety_score(state: dict, safety_analysis: dict) -> str:
    """
    Extracts a numeric safety score from the state or safety analysis if available.
    """
    # Check for direct key in state or safety_analysis
    score = state.get("safety_score") or safety_analysis.get("safety_score")
    if score is not None:
        return str(score)
        
    # Check if overall_score is numeric or contains a numeric score (e.g., "88/100")
    overall_score = safety_analysis.get("overall_score", "")
    if isinstance(overall_score, (int, float)):
        return str(overall_score)
        
    # Regex search for a score
    match = re.search(r'\b(100|[1-9]?[0-9])\b', str(overall_score))
    if match:
        return match.group(1)
        
    return None


def determine_ingredient_risk(report: dict) -> str:
    """
    Determines risk level for an ingredient based on its report.
    """
    human_safety = str(report.get("human_safety_status", "")).lower()
    
    if "not recommended" in human_safety:
        return "High Risk"
    elif "use with caution" in human_safety:
        return "Medium Risk"
    elif "generally safe with conditions" in human_safety:
        return "Low Risk (Conditional)"
    elif "generally safe" in human_safety or "verified safe" in human_safety or "considered safe" in human_safety:
        return "Low Risk"
    elif "insufficient" in human_safety:
        return "Needs More Evidence"

    # Check explicit keys if human_safety_status was not clear
    for key in ["risk_level", "risk", "overall_risk"]:
        val = report.get(key)
        if val:
            val_lower = str(val).lower()
            if "high" in val_lower or "danger" in val_lower:
                return "High Risk"
            elif "medium" in val_lower or "caution" in val_lower:
                return "Medium Risk"
            elif "low" in val_lower or "safe" in val_lower:
                return "Low Risk"
            return str(val)

    # Keyword fallback (only if human_safety is empty or doesn't match above)
    side_effects = str(report.get("side_effects", "")).lower()
    evidence = str(report.get("evidence", "")).lower()

    # Avoid false positives like "no known toxicity risks" by doing smart negative keyword filtering
    def is_negated(keyword, text):
        pattern = rf"\b(no|not|without|low|none|free of)\s+\w*\s*\b{keyword}"
        return bool(re.search(pattern, text))

    high_keywords = ["toxic", "carcinogen", "banned", "prohibited", "severe allergy", "sensitizer", "contact dermatitis", "hazardous", "formaldehyde"]
    medium_keywords = ["irritant", "irritation", "irritating", "allergy", "allergic", "caution", "sensitizing", "sensitization"]

    has_high = False
    for kw in high_keywords:
        if kw in side_effects and not is_negated(kw, side_effects):
            has_high = True
            break

    if has_high:
        return "High Risk"

    safe_phrases = [
        "safe" in side_effects,
        "no known side effects" in side_effects,
        "none known" in side_effects,
        "generally none" in side_effects,
        "generally considered safe" in side_effects,
        "low potential for irritation" in side_effects,
        "generally safe" in side_effects,
        "well-tolerated" in side_effects,
    ]
    if any(safe_phrases):
        return "Low Risk"

    has_medium = False
    for kw in medium_keywords:
        if (kw in side_effects and not is_negated(kw, side_effects)) or \
           (kw in evidence and not is_negated(kw, evidence)):
            has_medium = True
            break

    if has_medium:
        return "Medium Risk"

    return "Needs More Evidence"



def report_node(state: dict) -> dict:
    """
    Report Agent Node.
    
    Reads the entire state and generates:
    1. A polished, professional Markdown safety report conforming to 10 sections.
    2. A JSON export of all structured data with additional metadata.
    
    Stores the reports in state["markdown_report"] and state["json_report"].
    Also saves them to disk.
    """
    ocr_text = state.get("ocr_text", "N/A")
    ingredients = state.get("ingredients", [])
    research_results = state.get("research_results", {})
    safety_analysis = state.get("safety_analysis", {})
    image_path = state.get("image_path", "N/A")
    
    # ---------------------------------------------
    # 0. Preparation & Math Risk Calculation
    # ---------------------------------------------
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Compute per-ingredient risk counts for math score
    risk_counts = {"Low Risk": 0, "Low Risk (Conditional)": 0, "Medium Risk": 0,
                   "High Risk": 0, "Needs More Evidence": 0}
    for ing in ingredients:
        r = determine_ingredient_risk(research_results.get(ing, {}))
        if r in risk_counts:
            risk_counts[r] += 1
        else:
            risk_counts["Needs More Evidence"] += 1

    # Math score: start at 100, apply capped deductions
    math_score = 100
    math_score -= min(risk_counts["High Risk"] * 25, 50)
    math_score -= min(risk_counts["Medium Risk"] * 10, 30)
    math_score -= min(risk_counts["Low Risk (Conditional)"] * 3, 15)
    math_score -= min(risk_counts["Needs More Evidence"] * 2, 10)
    math_score = max(0, min(100, math_score))

    # Derive rating and badge from math_score
    if math_score >= 80:
        overall_score = "Safe / Low Risk"
        overall_badge = "🟢 LOW RISK"
    elif math_score >= 50:
        overall_score = "Caution / Medium Risk"
        overall_badge = "🟡 MEDIUM RISK"
    else:
        overall_score = "Danger / High Risk"
        overall_badge = "🔴 HIGH RISK"

    # Evidence Coverage counts
    confidence_counts = {"High": 0, "Medium": 0, "Low": 0, "Unknown": 0}
    for ing in ingredients:
        rep = research_results.get(ing, {})
        conf = rep.get("confidence_score", "").capitalize()
        if conf in confidence_counts:
            confidence_counts[conf] += 1
        else:
            confidence_counts["Unknown"] += 1
    
    # Warnings & Recommendations
    warnings = safety_analysis.get("warnings", [])
    recommendations = safety_analysis.get("recommendations", [])
    
    # References gathering
    references = []
    state_refs = state.get("references") or state.get("sources")
    if state_refs:
        if isinstance(state_refs, list):
            references.extend(state_refs)
        elif isinstance(state_refs, str):
            references.append(state_refs)
            
    for ing, report in research_results.items():
        # Collect real source URLs from safety_sources (populated by web search)
        safety_srcs = report.get("safety_sources", [])
        if isinstance(safety_srcs, list):
            references.extend(safety_srcs)
        # Also scan evidence text for any inline URLs
        evidence = report.get("evidence", "")
        urls = re.findall(r'https?://[^\s\)\],]+', str(evidence))
        if urls:
            references.extend(urls)
            
    unique_refs = []
    for ref in references:
        ref_str = str(ref).strip()
        if ref_str and ref_str not in unique_refs:
            unique_refs.append(ref_str)
            
    # Check if confidence exists for any ingredient
    has_confidence = any("confidence" in report for report in research_results.values())
    
    # ---------------------------------------------
    # 1. COVER SECTION
    # ---------------------------------------------
    md_lines = []
    md_lines.append("# IngredientSight AI")
    md_lines.append("## AI Product Safety Report")
    md_lines.append("")
    md_lines.append(f"**Generated**: {timestamp}")
    md_lines.append(f"**Source Image**: `{image_path}`")
    md_lines.append("")
    md_lines.append("### Overall Safety Rating")
    md_lines.append(overall_badge)
    md_lines.append("")
    md_lines.append("### Safety Score")
    md_lines.append(f"{math_score} / 100")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    
    # ---------------------------------------------
    # 2. EXECUTIVE SUMMARY
    # ---------------------------------------------
    md_lines.append("## Executive Summary")
    md_lines.append("")

    # Evidence Coverage Table
    md_lines.append("### Evidence Coverage")
    md_lines.append("")
    md_lines.append(f"| Ingredients Analysed | High Confidence | Medium Confidence | Low Confidence | Unknown |")
    md_lines.append(f"|---------------------|-----------------|-------------------|----------------|---------|")
    md_lines.append(f"| {len(ingredients)} | {confidence_counts['High']} | {confidence_counts['Medium']} | {confidence_counts['Low']} | {confidence_counts['Unknown']} |")
    md_lines.append("")

    # Risk Score Breakdown
    md_lines.append("### Risk Score Breakdown")
    md_lines.append("")
    md_lines.append(f"| Risk Category | Count | Points Deducted |")
    md_lines.append(f"|---------------|-------|-----------------|")
    md_lines.append(f"| Low Risk | {risk_counts['Low Risk']} | 0 |")
    md_lines.append(f"| Low Risk (Conditional) | {risk_counts['Low Risk (Conditional)']} | {min(risk_counts['Low Risk (Conditional)'] * 3, 15)} |")
    md_lines.append(f"| Medium Risk | {risk_counts['Medium Risk']} | {min(risk_counts['Medium Risk'] * 10, 30)} |")
    md_lines.append(f"| High Risk | {risk_counts['High Risk']} | {min(risk_counts['High Risk'] * 25, 50)} |")
    md_lines.append(f"| Needs More Evidence | {risk_counts['Needs More Evidence']} | {min(risk_counts['Needs More Evidence'] * 2, 10)} |")
    md_lines.append("")
    md_lines.append(f"**Final Product Safety Score: {math_score} / 100 → {overall_score}**")
    md_lines.append("")

    md_lines.append(f"• **Number of detected ingredients**: {len(ingredients)}")
    md_lines.append(f"• **Overall risk level**: {overall_score}")
    md_lines.append(f"• **Number of warnings**: {len(warnings)}")
    md_lines.append(f"• **Number of recommendations**: {len(recommendations)}")
    md_lines.append("")
    md_lines.append("### Consumer Summary")
    md_lines.append(safety_analysis.get("summary", "No summary available."))
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    
    # ---------------------------------------------
    # 3. PRODUCT INFORMATION
    # ---------------------------------------------
    md_lines.append("## Product Information")
    md_lines.append("")
    md_lines.append(f"- **Source Image Path**: `{image_path}`")
    md_lines.append(f"- **Normalized Ingredient Count**: {len(ingredients)}")
    md_lines.append(f"- **Normalized Ingredient List**: {', '.join(ingredients)}")
    md_lines.append("")
    md_lines.append("### Raw OCR Text")
    md_lines.append("```")
    md_lines.append(ocr_text)
    md_lines.append("```")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    
    # ---------------------------------------------
    # 4. INGREDIENT SUMMARY TABLE
    # ---------------------------------------------
    md_lines.append("## Ingredient Summary Table")
    md_lines.append("")
    md_lines.append("| # | Ingredient | Risk Level | Purpose | Human Safety Verification | Confidence | Verified Sources |")
    md_lines.append("|---|------------|------------|---------|---------------------------|------------|-----------------|")

    for idx, ing in enumerate(ingredients, 1):
        report = research_results.get(ing, {})
        risk = determine_ingredient_risk(report)
        purpose = report.get("purpose") or "N/A"
        human_safety = report.get("human_safety_status") or "Insufficient Web Data"
        confidence = report.get("confidence_score") or "Low"
        sources = report.get("safety_sources", [])
        sources_str = ", ".join(sources) if sources else "No sources found"
        md_lines.append(f"| {idx} | {ing} | {risk} | {purpose} | {human_safety} | {confidence} | {sources_str} |")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    
    # ---------------------------------------------
    # 5. DETAILED INGREDIENT PROFILES
    # ---------------------------------------------
    md_lines.append("## Detailed Ingredient Profiles")
    md_lines.append("")
    for ing in ingredients:
        report = research_results.get(ing, {})
        risk = determine_ingredient_risk(report)
        rec_val = report.get("recommendations") or report.get("recommendation") or "N/A"
        human_safety = report.get("human_safety_status") or "Insufficient Web Data"
        confidence = report.get("confidence_score") or "Low"
        safety_sources = report.get("safety_sources", [])

        md_lines.append(f"### {ing}")
        md_lines.append("")
        md_lines.append(f"- **Purpose**: {report.get('purpose') or 'N/A'}")
        md_lines.append(f"- **Side Effects**: {report.get('side_effects') or 'N/A'}")
        md_lines.append(f"- **Human Safety Verification**: {human_safety}")
        md_lines.append(f"- **Confidence Score**: {confidence}")
        
        # Exposure Suitability — supports both old bool and new string-based schemas
        exp_ctx = report.get("exposure_context", {})
        if hasattr(exp_ctx, "model_dump"):
            exp_ctx = exp_ctx.model_dump()
        elif not isinstance(exp_ctx, dict):
            exp_ctx = {}

        def get_ctx_label(str_key, bool_key=None):
            # New string-based schema
            val = exp_ctx.get(str_key)
            if val is not None:
                if isinstance(val, bool):
                    return "✓ Suitable" if val else "⚠ Caution / Avoid"
                # String value
                v = str(val).strip()
                if v in ("Suitable", "No specific pregnancy concerns identified"):
                    return f"✓ {v}"
                elif v in ("Caution / Avoid", "Consult healthcare provider if concerned"):
                    return f"⚠ {v}"
                elif v == "Unknown":
                    return "— Unknown"
                return v
            # Legacy bool schema fallback
            if bool_key:
                old = exp_ctx.get(bool_key)
                if old is True:
                    return "✓ Suitable"
                elif old is False:
                    return "⚠ Caution / Avoid"
            return "— N/A"

        md_lines.append("- **Applicable To / Suitability Context**:")
        md_lines.append(f"  - Sensitive Skin: {get_ctx_label('sensitive_skin_suitability', 'safe_for_sensitive_skin')}")
        md_lines.append(f"  - Children: {get_ctx_label('children_suitability', 'safe_for_children')}")
        md_lines.append(f"  - Pregnant Users: {get_ctx_label('pregnancy_suitability', 'safe_for_pregnant_users')}")
        md_lines.append(f"  - Rinse-off Products: {get_ctx_label('rinse_off_suitability', 'suitable_for_rinse_off')}")
        md_lines.append(f"  - Leave-on Products: {get_ctx_label('leave_on_suitability', 'suitable_for_leave_on')}")
        md_lines.append(f"  - Spray/Inhalation Products: {get_ctx_label('spray_suitability', 'suitable_for_spray_products')}")
        
        if safety_sources:
            md_lines.append(f"- **Verification Sources**:")
            for src in safety_sources:
                md_lines.append(f"  - {src}")
        else:
            md_lines.append(f"- **Verification Sources**: No web sources found")
        md_lines.append(f"- **Scientific Evidence**: {report.get('evidence') or 'N/A'}")
        md_lines.append(f"- **Overall Risk**: {risk}")
        md_lines.append(f"- **Recommendations**: {rec_val}")
        md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    
    # ---------------------------------------------
    # 6. WARNINGS
    # ---------------------------------------------
    md_lines.append("## ⚠ Warnings")
    md_lines.append("")
    if warnings:
        md_lines.append("> [!WARNING]")
        for warn in warnings:
            md_lines.append(f"> • {warn}")
    else:
        md_lines.append("> [!NOTE]")
        md_lines.append("> • No warnings identified.")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    
    # ---------------------------------------------
    # 7. RECOMMENDATIONS
    # ---------------------------------------------
    md_lines.append("## Recommendations")
    md_lines.append("")
    if recommendations:
        for rec in recommendations:
            prefix = "" if rec.strip().startswith("✔") else "✔ "
            md_lines.append(f"{prefix}{rec}")
    else:
        md_lines.append("✔ No specific recommendations.")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    
    # ---------------------------------------------
    # 8. REGULATORY COMPLIANCE (DYNAMICAL)
    # ---------------------------------------------
    cir_consulted = any("cir" in ref.lower() or "cosmetic ingredient review" in ref.lower() for ref in unique_refs)
    fda_consulted = any("fda" in ref.lower() or "food and drug administration" in ref.lower() for ref in unique_refs)
    sccs_consulted = any("sccs" in ref.lower() or "scientific committee" in ref.lower() or "europa" in ref.lower() for ref in unique_refs)
    hc_consulted = any("canada" in ref.lower() or "health canada" in ref.lower() for ref in unique_refs)
    pubmed_consulted = any("pubmed" in ref.lower() or "nih.gov" in ref.lower() or "ncbi" in ref.lower() for ref in unique_refs)

    md_lines.append("## Regulatory Sources Consulted")
    md_lines.append("")
    md_lines.append(f"- [{'✓' if cir_consulted else ' '}] CIR (Cosmetic Ingredient Review)")
    md_lines.append(f"- [{'✓' if fda_consulted else ' '}] FDA (Food and Drug Administration)")
    md_lines.append(f"- [{'✓' if sccs_consulted else ' '}] SCCS (Scientific Committee on Consumer Safety)")
    md_lines.append(f"- [{'✓' if hc_consulted else ' '}] Health Canada")
    md_lines.append(f"- [{'✓' if pubmed_consulted else ' '}] PubMed")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    
    # ---------------------------------------------
    # 9. REFERENCES (GROUPED AND REPRESENTATIVE)
    # ---------------------------------------------
    pubmed_refs = []
    cir_refs = []
    hc_refs = []
    fda_refs = []
    sccs_refs = []
    other_refs = []
    
    for ref in unique_refs:
        ref_lower = ref.lower()
        if "pubmed" in ref_lower or "ncbi.nlm.nih.gov" in ref_lower or "nih.gov" in ref_lower:
            pubmed_refs.append(ref)
        elif "cir-safety.org" in ref_lower or "cosmetic ingredient review" in ref_lower:
            cir_refs.append(ref)
        elif "fda.gov" in ref_lower:
            fda_refs.append(ref)
        elif "canada.ca" in ref_lower or "health canada" in ref_lower:
            hc_refs.append(ref)
        elif "ec.europa.eu" in ref_lower or "europa.eu" in ref_lower or "sccs" in ref_lower:
            sccs_refs.append(ref)
        else:
            other_refs.append(ref)

    md_lines.append("## References")
    md_lines.append("")
    md_lines.append("### Evidence Sources")
    md_lines.append("")
    if pubmed_refs:
        md_lines.append(f"- **PubMed** ({len(pubmed_refs)} paper{'s' if len(pubmed_refs) > 1 else ''})")
    if cir_refs:
        md_lines.append(f"- **CIR** ({len(cir_refs)} report{'s' if len(cir_refs) > 1 else ''})")
    if fda_refs:
        md_lines.append(f"- **FDA** ({len(fda_refs)} source{'s' if len(fda_refs) > 1 else ''})")
    if hc_refs:
        md_lines.append(f"- **Health Canada** ({len(hc_refs)} source{'s' if len(hc_refs) > 1 else ''})")
    if sccs_refs:
        md_lines.append(f"- **SCCS** ({len(sccs_refs)} source{'s' if len(sccs_refs) > 1 else ''})")
    if other_refs:
        md_lines.append(f"- **Other Web Databases** ({len(other_refs)} source{'s' if len(other_refs) > 1 else ''})")
    md_lines.append("")
    
    md_lines.append("### Representative References")
    md_lines.append("")
    
    # Choose max 2 from each authority, and max 3 from other
    rep_refs = []
    rep_refs.extend(pubmed_refs[:2])
    rep_refs.extend(cir_refs[:2])
    rep_refs.extend(fda_refs[:2])
    rep_refs.extend(hc_refs[:2])
    rep_refs.extend(sccs_refs[:2])
    rep_refs.extend(other_refs[:3])
    
    if rep_refs:
        for ref in rep_refs:
            md_lines.append(f"- {ref}")
    else:
        md_lines.append("Research generated from available knowledge base.")
    md_lines.append("")
    
    # ---------------------------------------------
    # 10. FOOTER
    # ---------------------------------------------
    md_lines.append("---")
    md_lines.append("")
    md_lines.append("Generated by IngredientSight AI")
    md_lines.append("AI-powered ingredient safety analysis.")
    md_lines.append("")
    
    markdown_report = "\n".join(md_lines)
    state["markdown_report"] = markdown_report
    
    # ---------------------------------------------
    # JSON REPORT
    # ---------------------------------------------
    json_report = {
        # Keep original compatibility keys:
        "generated_at": timestamp,
        "source_image": image_path,
        "raw_ocr_text": ocr_text,
        "normalized_ingredients": ingredients,
        "research_results": research_results,
        "safety_analysis": safety_analysis,
        
        # Additionally include required new keys:
        "report_version": "1.0.0",
        "overall_risk": overall_score,
        "ingredient_count": len(ingredients),
        "warning_count": len(warnings),
        "recommendation_count": len(recommendations),
        "references": unique_refs
    }
    state["json_report"] = json_report
    
    # --- Save to disk ---
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
    os.makedirs(output_dir, exist_ok=True)
    
    safe_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    md_path = os.path.join(output_dir, f"report_{safe_timestamp}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_report)
        
    json_path = os.path.join(output_dir, f"report_{safe_timestamp}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_report, f, indent=2, ensure_ascii=False)
        
    state["report_md_path"] = os.path.abspath(md_path)
    state["report_json_path"] = os.path.abspath(json_path)
    
    print(f"Markdown report saved to: {os.path.abspath(md_path)}")
    print(f"JSON report saved to: {os.path.abspath(json_path)}")
    
    return state
