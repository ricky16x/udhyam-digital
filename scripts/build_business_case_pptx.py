#!/usr/bin/env python3
"""Build the official 10-slide Business Case presentation using the Airtel SYNC template."""
import os, sys
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

TEMPLATE_PATH = "instructions/6ad9d4887d445_airtel_sync/Submission Template_Sync.pptx"
OUTPUT_PATH = "Business_Case_Project_Udyam_Digital_10_Slides.pptx"
BG_COVER = "/tmp/ppt/media/image2.jpg"
BG_CONTENT = "/tmp/ppt/media/image1.jpg"

# Brand colors
C_RED = RGBColor(228, 0, 0)         # Airtel Brand Red
C_DARK = RGBColor(27, 31, 36)        # Dark Charcoal
C_WHITE = RGBColor(255, 255, 255)    # White
C_MUTED = RGBColor(90, 100, 110)     # Muted Grey
C_LIGHT_BG = RGBColor(246, 248, 250) # Light Box Fill
C_GREEN = RGBColor(15, 138, 75)      # Success Green
C_BORDER = RGBColor(215, 220, 226)   # Border Grey
C_LIGHT_RED = RGBColor(254, 243, 243)# Light Red tint

def create_deck():
    prs = pptx.Presentation(TEMPLATE_PATH)
    
    # Remove existing blank placeholder slides
    while len(prs.slides) > 0:
        rId = prs.slides._sldIdLst[0].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[0]
        
    blank_layout = prs.slide_layouts[10]

    def add_content_slide(title_text, subtitle_text=""):
        s = prs.slides.add_slide(blank_layout)
        if os.path.exists(BG_CONTENT):
            s.shapes.add_picture(BG_CONTENT, 0, 0, prs.slide_width, prs.slide_height)
        
        t_box = s.shapes.add_textbox(Inches(0.6), Inches(0.28), Inches(8.8), Inches(0.7))
        tf = t_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(21)
        p.font.bold = True
        p.font.color.rgb = C_DARK
        p.font.name = "Arial"
        
        if subtitle_text:
            p2 = tf.add_paragraph()
            p2.text = subtitle_text
            p2.font.size = Pt(10.5)
            p2.font.color.rgb = C_MUTED
            p2.font.name = "Arial"
        return s

    def add_card(slide, left, top, width, height, bg_color=C_LIGHT_BG, border_color=C_BORDER):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
        return shape

    # =========================================================================
    # SLIDE 1: Title & Executive Summary
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    if os.path.exists(BG_COVER):
        s1.shapes.add_picture(BG_COVER, 0, 0, prs.slide_width, prs.slide_height)
    
    t_card = add_card(s1, Inches(0.8), Inches(1.2), Inches(8.4), Inches(3.2), C_WHITE, C_RED)
    tf1 = t_card.text_frame
    tf1.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf1.margin_left = Inches(0.4); tf1.margin_right = Inches(0.4)
    
    p = tf1.paragraphs[0]
    p.text = "BUSINESS CASE: PROJECT UDYAM DIGITAL"
    p.font.size = Pt(28); p.font.bold = True; p.font.color.rgb = C_RED; p.font.name = "Arial"
    
    p = tf1.add_paragraph()
    p.text = "Making India's MSMEs Go Digital in One Sitting"
    p.font.size = Pt(17); p.font.bold = True; p.font.color.rgb = C_DARK; p.font.name = "Arial"
    
    p = tf1.add_paragraph()
    p.text = "\nStrategic Business Case & Investment Memo · Airtel SYNC Hackathon 2026 (Enterprise Track A)\nTarget Customer | Value Creation | Right-Sized Pricing | Field Symbiosis | Phased Rollout | Risk Controls"
    p.font.size = Pt(11); p.font.color.rgb = C_MUTED; p.font.name = "Arial"

    # =========================================================================
    # SLIDE 2: The MSME Opportunity & Broken Funnel
    # =========================================================================
    s2 = add_content_slide("The Opportunity: 6.3 Crore MSMEs vs A Broken Funnel",
                           "Analysis of 5,000 SMB leads reveals friction, delayed cycles, and massive drop-offs")
    
    metrics = [
        ("7.4% Conversion", "Only 368 / 5,000 leads activate", C_RED),
        ("17.6 Days", "Average onboarding cycle time", C_DARK),
        ("3.0 Chase Calls", "Customer chasing status updates", C_DARK),
        ("₹15,000 CAC", "Blended acquisition cost per SMB", C_DARK)
    ]
    for i, (val, desc, col) in enumerate(metrics):
        c = add_card(s2, Inches(0.6 + i * 2.22), Inches(1.12), Inches(2.15), Inches(0.85), C_WHITE)
        tf = c.text_frame
        tf.margin_left = Inches(0.12); tf.margin_top = Inches(0.08)
        p = tf.paragraphs[0]
        p.text = val; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = col
        p2 = tf.add_paragraph()
        p2.text = desc; p2.font.size = Pt(8.5); p2.font.color.rgb = C_MUTED

    c_f = add_card(s2, Inches(0.6), Inches(2.1), Inches(4.35), Inches(3.15), C_WHITE)
    tf = c_f.text_frame; tf.margin_left = tf.margin_right = Inches(0.2); tf.margin_top = Inches(0.15)
    p = tf.paragraphs[0]
    p.text = "The 5-Stage Drop-Off Breakdown (smb_leads.csv)"
    p.font.bold = True; p.font.size = Pt(10.5); p.font.color.rgb = C_DARK
    stages = [
        ("1. Leads Generated", "5,000", "Baseline pool"),
        ("2. Contacted", "3,406 (68%)", "32% unreachable / drop"),
        ("3. Needs Assessed", "1,974 (58%)", "Slow field rep visits"),
        ("4. Quote Accepted", "861 (44%)", "CRITICAL CLIFF: 56% lost to sticker shock"),
        ("5. KYC Complete", "588 (68%)", "Paper friction: GST, Udyam, utility bills"),
        ("6. Activated", "368 (63%)", "Installation delays & chase calls")
    ]
    for st, cnt, note in stages:
        p = tf.add_paragraph()
        p.text = f"• {st}: "; p.font.bold = True; p.font.size = Pt(8.5); p.font.color.rgb = C_RED if "CLIFF" in note else C_DARK
        p.text += f"{cnt} – {note}"; p.font.bold = False; p.font.size = Pt(8.2); p.font.color.rgb = C_MUTED

    c_r = add_card(s2, Inches(5.1), Inches(2.1), Inches(4.3), Inches(3.15), C_WHITE)
    tf = c_r.text_frame; tf.margin_left = tf.margin_right = Inches(0.2); tf.margin_top = Inches(0.15)
    p = tf.paragraphs[0]
    p.text = "Core Market Imperatives"
    p.font.bold = True; p.font.size = Pt(10.5); p.font.color.rgb = C_DARK
    insights = [
        ("The Quote Barrier", "Sales reps send 5-page enterprise PDF quotes with codes owners don't understand, causing 56% abandonment."),
        ("GSTIN Disparity", "Leads with active GSTIN activate at 9.6% vs 2.0% without (a 4.8x multiplier). Verification must be instant."),
        ("Micro-Churn Danger", "Micro SMBs billed >₹3,000/mo churn at 36% within 6 months vs 7% under ₹3,000. Packages must be right-sized."),
        ("Digital-First Competitors", "Point players offer instant digital apps. Accel must offer unified bundles on 1 bill.")
    ]
    for h, d in insights:
        p = tf.add_paragraph()
        p.text = f"• {h}: "; p.font.bold = True; p.font.size = Pt(8.8); p.font.color.rgb = C_DARK
        p.text += d; p.font.size = Pt(8.2); p.font.color.rgb = C_MUTED

    # =========================================================================
    # SLIDE 3: Target Segmentation & Right-Sized Bundles
    # =========================================================================
    s3 = add_content_slide("Target Customer Segmentation & Winning Bundles",
                           "Four distinct MSME segments prioritized by commercial value, GST compliance, and churn risk")
    
    segs = [
        ("Priority 1: Professional Offices", "Clinics, CA firms, coaching centres (25% base)",
         "Biz Fibre 300 + Cloud Email + Endpoint Security + 1 TB Cloud Backup", "₹5,200 – ₹5,400 /mo",
         "90%+ GST compliance; high willingness to pay for data protection and reliable uptime."),
        ("Priority 2: Micro Retail & Services", "Kirana, salon, chemist, pharmacy (55% base)",
         "Starter Pack: Biz Fibre 100 + 1 Business SIM (replaces personal hotspot tether)", "₹1,448 – ₹2,499 /mo",
         "Strict ₹1,500 low-spend cap; Cloud POS billing as modular add-on prevents 36% churn cliff."),
        ("Priority 3: Multi-Site Retail Chains", "3–10 store restaurants / apparel chains (15% base)",
         "Biz Fibre (all sites) + Managed SD-WAN + Cloud CCTV + 4G/5G Failover", "₹21,000 – ₹33,000 /mo",
         "Single consolidated bill; 24-month contract waives up to ₹71,000 in setup fees."),
        ("Priority 4: Small Manufacturers", "Auto-parts, textiles, light engineering (5% base)",
         "Internet Leased Line (ILL) + IoT Machine Sensors + Fleet GPS + Firewall", "₹32,000 – ₹58,000 /mo",
         "Guaranteed symmetrical bandwidth with 99.5% commercial SLA and telemetry.")
    ]
    for i, (name, target, bundle, price, why) in enumerate(segs):
        card = add_card(s3, Inches(0.6 + (i%2)*4.5), Inches(1.15 + (i//2)*2.05), Inches(4.3), Inches(1.95), C_WHITE)
        tf = card.text_frame; tf.margin_left = tf.margin_right = Inches(0.2); tf.margin_top = Inches(0.12)
        p = tf.paragraphs[0]
        p.text = name; p.font.bold = True; p.font.size = Pt(11); p.font.color.rgb = C_RED
        p = tf.add_paragraph()
        p.text = f"Target: {target}"; p.font.size = Pt(8.5); p.font.color.rgb = C_MUTED
        p = tf.add_paragraph()
        p.text = f"Bundle: {bundle}"; p.font.bold = True; p.font.size = Pt(9.5); p.font.color.rgb = C_DARK
        p = tf.add_paragraph()
        p.text = f"Price: {price}"; p.font.bold = True; p.font.size = Pt(10); p.font.color.rgb = C_GREEN
        p = tf.add_paragraph()
        p.text = f"Value Proposition: {why}"; p.font.size = Pt(8.5); p.font.color.rgb = C_MUTED

    # =========================================================================
    # SLIDE 4: Solution Architecture & Conversational Advisor
    # =========================================================================
    s4 = add_content_slide("Solution Architecture & Conversational Advisor",
                           "Replacing human sales discovery with an ultra-fast (<5ms), privacy-preserving local engine")
    
    pillars = [
        ("Deterministic Slot Engine", "Zero External LLM Dependency",
         ["Natural language multi-slot parsing in English, Hindi, and Hinglish.",
          "Takes 6 business facts or 1 free-text sentence and fills slots in 1 turn.",
          "Zero 3rd-party LLM API cost, zero downtime, zero latency (<5ms), zero hallucination.",
          "Generates plain-language explanation of bundle value."]),
        ("Catalogue Verification", "Strict Mathematical Rules",
         ["Enforces city-tier availability (Tier 1 vs Tier 2 coverage).",
          "Validates minimum employee count and branch site limits.",
          "Resolves prerequisite dependency trees (requires_one_of).",
          "Calculates transparent setup fees and bundle discounts."]),
        ("Warm Handoff Protocol", "Field Sales Integration",
         ["Direct integration with Back-Office Executive Desk.",
          "When customer requests human ('talk to an expert'), all captured answers sync instantly.",
          "Field reps call within 2 hours without asking repetitive questions.",
          "Zero context loss across digital and human channels."])
    ]
    for i, (title, sub, bullets) in enumerate(pillars):
        c = add_card(s4, Inches(0.6 + i * 2.95), Inches(1.15), Inches(2.85), Inches(4.1), C_WHITE)
        tf = c.text_frame; tf.margin_left = tf.margin_right = Inches(0.18); tf.margin_top = Inches(0.15)
        p = tf.paragraphs[0]
        p.text = title; p.font.bold = True; p.font.size = Pt(11); p.font.color.rgb = C_RED
        p2 = tf.add_paragraph()
        p2.text = sub; p2.font.size = Pt(9); p2.font.color.rgb = C_MUTED
        for b in bullets:
            p = tf.add_paragraph()
            p.text = f"• {b}"; p.font.size = Pt(8.5); p.font.color.rgb = C_DARK

    # =========================================================================
    # SLIDE 5: Instant Smart KYC & 1-Click DigiLocker
    # =========================================================================
    s5 = add_content_slide("Instant Smart KYC & 1-Click DigiLocker Integration",
                           "From 5 days of document chasing to 60 seconds of automated verification")
    
    kyc_cards = [
        ("1-Click DigiLocker Pull", "MeitY Integration",
         "Eliminates camera uploads entirely. Customers authenticate and pull authentic Udyam registration and GST certificates in 1 click, auto-filling trade name, address, and legal constitution."),
        ("Computer Vision Pipeline", "Resilient Document OCR",
         "Handles real-world mobile photo defects: automatic watermark removal, line projection deskewing (±12°), Laplacian blur rescue, and confusable character repair (O/0, I/J)."),
        ("Live Registry Cross-Checks", "Fraud Prevention",
         "Real Mod-36 checksum verification + instant cross-reference against 3,534 GSTIN and 2,723 Udyam records. Instantly flags cancelled GSTINs, tampered numbers, and altered legal names."),
        ("100% Precision on Case Specimens", "Ground-Truth Verification",
         "Evaluated across all 12 specimen applicants (K01–K12). Catches expired utility bills (>90 days in K11), cancelled GSTINs (K01), unreadable blurry scans (K04), and name variance (K07).")
    ]
    for i, (h, sub, desc) in enumerate(kyc_cards):
        card = add_card(s5, Inches(0.6 + (i%2)*4.5), Inches(1.15 + (i//2)*2.05), Inches(4.3), Inches(1.95), C_WHITE)
        tf = card.text_frame; tf.margin_left = tf.margin_right = Inches(0.2); tf.margin_top = Inches(0.15)
        p = tf.paragraphs[0]
        p.text = h; p.font.bold = True; p.font.size = Pt(11); p.font.color.rgb = C_RED
        p.text += f" ({sub})"; p.font.size = Pt(9); p.font.color.rgb = C_MUTED
        p = tf.add_paragraph()
        p.text = desc; p.font.size = Pt(9); p.font.color.rgb = C_DARK

    # =========================================================================
    # SLIDE 6: Transparent Quote & Automated Order Tracker
    # =========================================================================
    s6 = add_content_slide("Transparent Quote & Automated Order Tracker",
                           "Eliminating quote confusion and status chase calls with full visibility")
    
    c_q = add_card(s6, Inches(0.6), Inches(1.15), Inches(4.35), Inches(4.1), C_WHITE)
    tf = c_q.text_frame; tf.margin_left = tf.margin_right = Inches(0.2); tf.margin_top = Inches(0.15)
    p = tf.paragraphs[0]
    p.text = "Transparent Digital Quote & Checkout"
    p.font.bold = True; p.font.size = Pt(11); p.font.color.rgb = C_DARK
    q_points = [
        ("Single Monthly Bill", "Clear itemized pricing with 18% GST calculation; eliminates multi-vendor subscription sprawl."),
        ("12 vs 24 Month Contracts", "24-month contract incentivizes long-term retention by waiving up to ₹71,000 in one-time setup fees."),
        ("Interactive Add-on Toggles", "Modular check/uncheck for Cloud POS, Static IP, and CCTV with instant dynamic total re-calculation."),
        ("Automated UPI Autopay", "Instant digital mandate authorization on checkout; zero paper cheques or manual invoicing friction.")
    ]
    for h, d in q_points:
        p = tf.add_paragraph()
        p.text = f"• {h}: "; p.font.bold = True; p.font.size = Pt(9); p.font.color.rgb = C_RED
        p.text += d; p.font.size = Pt(8.5); p.font.color.rgb = C_MUTED

    c_t = add_card(s6, Inches(5.1), Inches(1.15), Inches(4.3), Inches(4.1), C_WHITE)
    tf = c_t.text_frame; tf.margin_left = tf.margin_right = Inches(0.2); tf.margin_top = Inches(0.15)
    p = tf.paragraphs[0]
    p.text = "Milestone Tracker: Zero Chase Calls"
    p.font.bold = True; p.font.size = Pt(11); p.font.color.rgb = C_DARK
    t_points = [
        ("5-Stage Visual State Machine", "Order Placed → KYC Verified → Feasibility Check → Engineer Assigned → Live."),
        ("Named Technician SLA", "Shows assigned local field engineer, direct contact, and arrival time window."),
        ("Proactive WhatsApp Alerts", "Pushes instant updates on stage changes, eliminating the 3.0 chase calls customers made historically."),
        ("5.0-Day Activation", "Slashes historical 17.6-day onboarding cycle down to a 5-day median.")
    ]
    for h, d in t_points:
        p = tf.add_paragraph()
        p.text = f"• {h}: "; p.font.bold = True; p.font.size = Pt(9); p.font.color.rgb = C_DARK
        p.text += d; p.font.size = Pt(8.5); p.font.color.rgb = C_MUTED

    # =========================================================================
    # SLIDE 7: Field Force & Channel Partner Symbiosis
    # =========================================================================
    s7 = add_content_slide("Field Force & Channel Partner Symbiosis",
                           "Digital supercharges local partners and field reps instead of competing with them")
    
    pillars_partner = [
        ("Assisted In-Store Portal", "Local Channel Partners",
         "Local computer retailers and telecom dealers use the same mobile web journey to onboard walk-in kirana owners in 5 minutes, receiving instant digital commission attribution."),
        ("Warm Live Handoffs", "Zero Customer Repetition",
         "When an SMB drops off or requests a callback, session state and declared needs sync directly to the Back Office. Field reps call within 2 hours with full context."),
        ("ML Propensity Scoring", "Logistic Regression (AUC 0.76)",
         "Trained on 5,000 historical leads. Scores dropped prospects as HIGH, MEDIUM, or LOW propensity. Top 30% of leads hold 68% of potential activations."),
        ("Smart Field Dispatch", "CAC Slashed to ₹5,200",
         "High-value multi-site and manufacturing leads routed for physical field visits; low-value micro leads receive automated WhatsApp recovery nudges.")
    ]
    for i, (h, sub, desc) in enumerate(pillars_partner):
        card = add_card(s7, Inches(0.6 + (i%2)*4.5), Inches(1.15 + (i//2)*2.05), Inches(4.3), Inches(1.95), C_WHITE)
        tf = card.text_frame; tf.margin_left = tf.margin_right = Inches(0.2); tf.margin_top = Inches(0.15)
        p = tf.paragraphs[0]
        p.text = h; p.font.bold = True; p.font.size = Pt(11); p.font.color.rgb = C_RED
        p.text += f" ({sub})"; p.font.size = Pt(9); p.font.color.rgb = C_MUTED
        p = tf.add_paragraph()
        p.text = desc; p.font.size = Pt(9); p.font.color.rgb = C_DARK

    # =========================================================================
    # SLIDE 8: Data Privacy & Security Choices (DPDP Act 2023)
    # =========================================================================
    s8 = add_content_slide("Data Privacy & Security Choices (DPDP Act, 2023)",
                           "Privacy-by-design architecture treating customer data with strict statutory safeguards")
    
    privacy_cards = [
        ("Consent Before Ingestion (DPDP §6)", "Itemized Purpose Limitation",
         "Dedicated consent screen appears before any upload. KYC and activation purposes are itemized and required; WhatsApp marketing is optional and unticked by default."),
        ("Data Minimization (DPDP §4, §8)", "Zero Sensitive Storage",
         "The advisor asks strictly about business requirements. No Aadhaar or PAN numbers collected. Document images processed in memory and discarded immediately after OCR."),
        ("Right to Erasure (DPDP §12)", "1-Tap Consent Withdrawal",
         "Single-click withdrawal button (DELETE /api/kyc/consent) purges all temporary KYC extractions and session tokens immediately from system memory."),
        ("Masking & Access Controls", "Enterprise Hardening",
         "All identifiers displayed as 37**********1ZS across UI, back office, and logs. Role-based access ensures unmasking is restricted and audited.")
    ]
    for i, (h, sub, desc) in enumerate(privacy_cards):
        card = add_card(s8, Inches(0.6 + (i%2)*4.5), Inches(1.15 + (i//2)*2.05), Inches(4.3), Inches(1.95), C_WHITE)
        tf = card.text_frame; tf.margin_left = tf.margin_right = Inches(0.2); tf.margin_top = Inches(0.15)
        p = tf.paragraphs[0]
        p.text = h; p.font.bold = True; p.font.size = Pt(11); p.font.color.rgb = C_RED
        p.text += f" ({sub})"; p.font.size = Pt(9); p.font.color.rgb = C_MUTED
        p = tf.add_paragraph()
        p.text = desc; p.font.size = Pt(9); p.font.color.rgb = C_DARK

    # =========================================================================
    # SLIDE 9: Business Impact & Unit Economics
    # =========================================================================
    s9 = add_content_slide("Business Impact & Unit Economics: The 5 Core Metrics",
                           "Quantified transformation across conversion, cycle time, acquisition cost, and churn")
    
    # Table of 5 metrics
    table_shape = s9.shapes.add_table(6, 4, Inches(0.6), Inches(1.2), Inches(8.8), Inches(3.8))
    t = table_shape.table
    t.columns[0].width = Inches(2.2)
    t.columns[1].width = Inches(1.6)
    t.columns[2].width = Inches(1.6)
    t.columns[3].width = Inches(3.4)

    h_titles = ["Key Success Metric", "Baseline (smb_leads.csv)", "Udyam Digital Target", "Impact Mechanism"]
    for col_idx, text in enumerate(h_titles):
        cell = t.cell(0, col_idx)
        cell.fill.solid(); cell.fill.fore_color.rgb = C_RED if col_idx == 2 else C_DARK
        p = cell.text_frame.paragraphs[0]
        p.text = text; p.font.bold = True; p.font.size = Pt(9.5); p.font.color.rgb = C_WHITE
        p.alignment = PP_ALIGN.CENTER if col_idx in (1, 2) else PP_ALIGN.LEFT

    impact_data = [
        ("Lead-to-Activation Rate", "7.4% (368 / 5,000)", "15.5% (774 / 5,000)", "+110% lift; eliminates 56% quote cliff and 32% KYC drop"),
        ("Onboarding Cycle Time", "17.6 days", "5.0 days (median)", "-72% cycle reduction via instant DigiLocker & slot booking"),
        ("Blended CAC", "₹15,000 / customer", "₹5,200 / customer", "-65% reduction; digital self-serve + ML propensity routing"),
        ("Customer Chase Calls", "3.0 calls / lead", "0.2 calls / lead", "-93% reduction; live visual milestone tracker & WhatsApp alerts"),
        ("6-Month Micro Churn", "36% (on >₹3k bundles)", "<7% (capped starter)", "Enforces strict ₹1,500–₹2,999 affordability guardrails")
    ]
    for row_idx, row in enumerate(impact_data, 1):
        for col_idx, text in enumerate(row):
            cell = t.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(254, 243, 243) if col_idx == 2 else (C_WHITE if row_idx % 2 == 0 else C_LIGHT_BG)
            p = cell.text_frame.paragraphs[0]
            p.text = text; p.font.size = Pt(8.5); p.font.bold = (col_idx == 2 or col_idx == 0)
            p.font.color.rgb = C_GREEN if col_idx == 2 else C_DARK
            p.alignment = PP_ALIGN.CENTER if col_idx in (1, 2) else PP_ALIGN.LEFT

    # =========================================================================
    # SLIDE 10: 12-Month Rollout Roadmap, Risks & Mitigations
    # =========================================================================
    s10 = add_content_slide("12-Month Rollout Roadmap, Risks & Mitigation Controls",
                            "Phased execution blueprint ensuring operational stability and channel alignment")
    
    # Left: Roadmap
    c_road = add_card(s10, Inches(0.6), Inches(1.15), Inches(4.35), Inches(4.1), C_WHITE)
    tf = c_road.text_frame; tf.margin_left = tf.margin_right = Inches(0.2); tf.margin_top = Inches(0.15)
    p = tf.paragraphs[0]
    p.text = "12-Month Phased Rollout Plan"
    p.font.bold = True; p.font.size = Pt(11); p.font.color.rgb = C_DARK
    phases = [
        ("Months 1–3: Pilot in Delhi NCR & Pune", "Deploy digital journey for Professional Offices & Kirana. Test DigiLocker and UPI Autopay."),
        ("Months 4–6: Partner Portal Enablement", "Onboard 500+ local channel partners with assisted portal and automated commission attribution."),
        ("Months 7–9: Regional Language Expansion", "Scale vernacular voice and chat support to Marathi, Tamil, Telugu, and Gujarati."),
        ("Months 10–12: Pan-India Expansion", "Full nationwide rollout across Tier 1 & Tier 2 cities. Target: 50,000 active SMB bundles.")
    ]
    for h, d in phases:
        p = tf.add_paragraph()
        p.text = f"▶ {h}"; p.font.bold = True; p.font.size = Pt(9); p.font.color.rgb = C_RED
        p = tf.add_paragraph()
        p.text = d; p.font.size = Pt(8.5); p.font.color.rgb = C_DARK

    # Right: Risks & Mitigations
    c_risk = add_card(s10, Inches(5.1), Inches(1.15), Inches(4.3), Inches(4.1), C_WHITE)
    tf = c_risk.text_frame; tf.margin_left = tf.margin_right = Inches(0.2); tf.margin_top = Inches(0.15)
    p = tf.paragraphs[0]
    p.text = "Key Operational Risks & Mitigations"
    p.font.bold = True; p.font.size = Pt(11); p.font.color.rgb = C_DARK
    risks = [
        ("Risk: Field Force Channel Conflict", "Mitigation: Partner commission parity. Field reps and partners receive 100% digital commission for assisted sign-ups."),
        ("Risk: Micro-Merchant Price Churn", "Mitigation: Enforced ₹1,500 starter cap for merchants spending ≤₹800/mo; billing software kept as optional add-on."),
        ("Risk: Incomplete Document Scans", "Mitigation: DigiLocker integration eliminates photo uploads; computer vision blur rescue and warm handoffs to back office."),
        ("Risk: DPDP Statutory Liability", "Mitigation: Ephemeral in-memory OCR, zero sensitive ID storage, and automated 1-tap consent revocation.")
    ]
    for h, d in risks:
        p = tf.add_paragraph()
        p.text = f"⚠ {h}: "; p.font.bold = True; p.font.size = Pt(8.8); p.font.color.rgb = C_DARK
        p.text += d; p.font.size = Pt(8.2); p.font.color.rgb = C_MUTED

    prs.save(OUTPUT_PATH)
    print(f"Business Case presentation successfully saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    create_deck()
