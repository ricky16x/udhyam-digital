#!/usr/bin/env python3
"""Build the official 7-slide presentation using the Airtel SYNC template."""
import os, sys
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

TEMPLATE_PATH = "instructions/6ad9d4887d445_airtel_sync/Submission Template_Sync.pptx"
OUTPUT_PATH = "Submission_Project_Udyam_Digital_TrackA.pptx"
BG_COVER = "/tmp/ppt/media/image2.jpg"
BG_CONTENT = "/tmp/ppt/media/image1.jpg"

# Airtel brand color palette
C_RED = RGBColor(228, 0, 0)         # Airtel Brand Red
C_DARK = RGBColor(27, 31, 36)        # Dark Slate Charcoal
C_WHITE = RGBColor(255, 255, 255)    # White
C_MUTED = RGBColor(90, 100, 110)     # Muted Cool Grey
C_LIGHT_BG = RGBColor(246, 248, 250) # Light Box Fill
C_GREEN = RGBColor(15, 138, 75)      # Success Green
C_BORDER = RGBColor(215, 220, 226)   # Border Grey
C_ACCENT_BLUE = RGBColor(24, 76, 120)# Subtle Enterprise Navy

def create_deck():
    prs = pptx.Presentation(TEMPLATE_PATH)
    
    # Remove existing blank placeholder slides
    while len(prs.slides) > 0:
        rId = prs.slides._sldIdLst[0].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[0]
        
    blank_layout = prs.slide_layouts[10] # blank

    # Helper: add content slide with template background
    def add_content_slide(title_text, subtitle_text=""):
        s = prs.slides.add_slide(blank_layout)
        if os.path.exists(BG_CONTENT):
            s.shapes.add_picture(BG_CONTENT, 0, 0, prs.slide_width, prs.slide_height)
        
        # Header title box
        t_box = s.shapes.add_textbox(Inches(0.6), Inches(0.28), Inches(8.8), Inches(0.7))
        tf = t_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = C_DARK
        p.font.name = "Arial"
        
        if subtitle_text:
            p2 = tf.add_paragraph()
            p2.text = subtitle_text
            p2.font.size = Pt(11)
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
    # SLIDE 1: Title Slide
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    if os.path.exists(BG_COVER):
        s1.shapes.add_picture(BG_COVER, 0, 0, prs.slide_width, prs.slide_height)
    
    t_card = add_card(s1, Inches(0.8), Inches(1.3), Inches(8.4), Inches(2.9), C_WHITE, C_RED)
    tf1 = t_card.text_frame
    tf1.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf1.margin_left = Inches(0.4)
    tf1.margin_right = Inches(0.4)
    
    p = tf1.paragraphs[0]
    p.text = "PROJECT UDYAM DIGITAL"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = C_RED
    p.font.name = "Arial"
    
    p = tf1.add_paragraph()
    p.text = "Making India's MSMEs Go Digital in One Sitting"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_DARK
    p.font.name = "Arial"
    
    p = tf1.add_paragraph()
    p.text = "\nAirtel SYNC Hackathon 2026 · Enterprise Track A\nAutomated Needs Discovery | Smart KYC & DigiLocker | Transparent Bundling | Field Symbiosis"
    p.font.size = Pt(12)
    p.font.color.rgb = C_MUTED
    p.font.name = "Arial"

    # =========================================================================
    # SLIDE 2: Problem Statement & Funnel Breakdown
    # =========================================================================
    s2 = add_content_slide("The MSME Problem: A Broken Acquisition Funnel",
                           "Analysis of 5,000 SMB leads reveals friction, sticker shock, and massive drop-offs")
    
    # 3 Stat Cards on Top
    stats = [
        ("7.4% Conversion", "Only 368 of 5,000 leads activate", C_RED),
        ("17.6 Days Delay", "Average time from lead to activation", C_DARK),
        ("₹15,000 CAC", "Blended acquisition cost per customer", C_DARK)
    ]
    for i, (head, sub, col) in enumerate(stats):
        c = add_card(s2, Inches(0.6 + i * 2.95), Inches(1.15), Inches(2.85), Inches(0.85), C_WHITE)
        tf = c.text_frame
        tf.margin_left = Inches(0.15); tf.margin_top = Inches(0.1)
        p = tf.paragraphs[0]
        p.text = head; p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = col
        p2 = tf.add_paragraph()
        p2.text = sub; p2.font.size = Pt(10); p2.font.color.rgb = C_MUTED

    # Left Box: Funnel Fall-off
    c_left = add_card(s2, Inches(0.6), Inches(2.15), Inches(4.3), Inches(3.1), C_WHITE)
    tf = c_left.text_frame
    tf.margin_left = tf.margin_right = Inches(0.25); tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]
    p.text = "Where SMBs Drop Out (smb_leads.csv)"
    p.font.bold = True; p.font.size = Pt(12); p.font.color.rgb = C_DARK
    
    items_left = [
        ("Leads Generated (5,000)", "Base pool of potential small businesses"),
        ("Needs Assessed → Quote (56% Lost)", "Steepest drop! Jargon PDFs & price shock"),
        ("Quote Accepted → KYC (32% Lost)", "Paper-heavy KYC: GST, Udyam, utility bills"),
        ("Active Churn (36% Churn in Micro)", "Micro bundles >₹3k churn rapidly vs 7% <₹3k")
    ]
    for h, d in items_left:
        p = tf.add_paragraph()
        p.text = f"• {h}: "; p.font.bold = True; p.font.size = Pt(10); p.font.color.rgb = C_RED
        p.text += d; p.font.bold = False; p.font.color.rgb = C_DARK

    # Right Box: Root Cause Diagnosis
    c_right = add_card(s2, Inches(5.1), Inches(2.15), Inches(4.3), Inches(3.1), C_WHITE)
    tf = c_right.text_frame
    tf.margin_left = tf.margin_right = Inches(0.25); tf.margin_top = Inches(0.2)
    p = tf.paragraphs[0]
    p.text = "Root Causes Identified"
    p.font.bold = True; p.font.size = Pt(12); p.font.color.rgb = C_DARK
    
    items_right = [
        ("Slow Field Discovery", "Reps pitch monthly targets, not customer needs."),
        ("No Unified Bill", "SMBs buy fragmented pieces from 4 different local vendors."),
        ("Status Blindness", "Customers make 3.0 chase calls over 17 days with zero tracking."),
        ("Competitor Threat", "Digital-first players offer 1-click single products. Accel needs unified bundles.")
    ]
    for h, d in items_right:
        p = tf.add_paragraph()
        p.text = f"• {h}: "; p.font.bold = True; p.font.size = Pt(10); p.font.color.rgb = C_DARK
        p.text += d; p.font.bold = False; p.font.color.rgb = C_MUTED

    # =========================================================================
    # SLIDE 3: Target Segmentation & Right-Sized Bundles
    # =========================================================================
    s3 = add_content_slide("Target Customer Segmentation & Right-Sized Bundles",
                           "Strategic prioritisation based on volume, ARPU, GST compliance, and churn guardrails")
    
    segs = [
        ("1. Professional Offices", "PRIORITY 1 (HIGH ARPU)", "Clinics, CA firms, coaching centres",
         "Biz Fibre 300 + Cloud Email + Endpoint Security + Cloud Backup", "₹5,200 – ₹5,400 /mo",
         "90%+ GST compliance; high willingness to pay for data backup & SLA."),
        ("2. Micro Retail & Services", "PRIORITY 2 (HIGH VOLUME)", "Kirana, salon, chemist, bakery",
         "Starter Pack: Biz Fibre 100 + 1 SIM (replaces mobile hotspot tether)", "₹1,448 – ₹2,499 /mo",
         "Strict ₹1,500 low-spend cap; optional POS billing prevents 36% churn cliff."),
        ("3. Multi-Site Retail Chains", "PRIORITY 3", "3–10 store restaurants / apparel",
         "Multi-Fibre + SD-WAN + Cloud CCTV + 4G Failover", "₹21,000 – ₹33,000 /mo",
         "Centralised IT management, 1 bill, 24m contract waives setup fee."),
        ("4. Small Manufacturers", "PRIORITY 4", "Auto-parts, textiles, packaging",
         "Internet Leased Line (ILL) + IoT Sensors + Fleet GPS", "₹32,000 – ₹58,000 /mo",
         "Dedicated symmetrical bandwidth, machine uptime monitoring.")
    ]
    for i, (name, tag, ex, bundle, price, why) in enumerate(segs):
        card = add_card(s3, Inches(0.6 + (i%2)*4.5), Inches(1.15 + (i//2)*2.05), Inches(4.3), Inches(1.95), C_WHITE)
        tf = card.text_frame
        tf.margin_left = tf.margin_right = Inches(0.2); tf.margin_top = Inches(0.12)
        p = tf.paragraphs[0]
        p.text = name; p.font.bold = True; p.font.size = Pt(11); p.font.color.rgb = C_RED
        p.text += f" | {tag}"; p.font.size = Pt(9); p.font.color.rgb = C_MUTED
        
        p = tf.add_paragraph()
        p.text = f"Bundle: {bundle}"; p.font.bold = True; p.font.size = Pt(9.5); p.font.color.rgb = C_DARK
        p = tf.add_paragraph()
        p.text = f"Price: {price}"; p.font.bold = True; p.font.size = Pt(10); p.font.color.rgb = C_GREEN
        p = tf.add_paragraph()
        p.text = f"Insight: {why}"; p.font.size = Pt(8.5); p.font.color.rgb = C_MUTED

    # =========================================================================
    # SLIDE 4: Solution Architecture & Approach
    # =========================================================================
    s4 = add_content_slide("Our Approach: The 4 Pillars of Udyam Digital",
                           "End-to-end self-serve acquisition architecture with zero external LLM dependencies")
    
    pillars = [
        ("1. Conversational Advisor", "EN / HI / Voice (<5ms)",
         ["Deterministic multi-slot entity parsing",
          "Takes 6 business facts or 1 natural sentence",
          "Zero LLM API risk, 0 hallucination, 100% privacy",
          "Plain-language explanation of bundle value"]),
        ("2. Dynamic Bundle Engine", "Catalogue & Rules",
         ["Strict eligibility: city tier, staff, GSTIN",
          "Prerequisite dependency resolution",
          "Transparent pricing with bundle discounts",
          "Micro-spend right-sizing (<₹1,500 cap)"]),
        ("3. Instant Smart KYC", "DPDP 2023 Compliant",
         ["1-click DigiLocker Udyam/GST retrieval",
          "Computer vision OCR (auto-deskew, repair)",
          "Cross-checks mock GST/Udyam registries",
          "1-tap data withdrawal & erasure button"]),
        ("4. Proactive Tracker", "Self-Serve Activation",
         ["Live milestone visual tracking",
          "SLA countdown & technician arrival window",
          "Proactive WhatsApp status updates",
          "Cuts customer status chase calls to near 0"])
    ]
    for i, (title, sub, bullets) in enumerate(pillars):
        c = add_card(s4, Inches(0.6 + i * 2.2), Inches(1.15), Inches(2.1), Inches(4.1), C_WHITE)
        tf = c.text_frame
        tf.margin_left = tf.margin_right = Inches(0.15); tf.margin_top = Inches(0.15)
        p = tf.paragraphs[0]
        p.text = title; p.font.bold = True; p.font.size = Pt(10.5); p.font.color.rgb = C_RED
        p2 = tf.add_paragraph()
        p2.text = sub; p2.font.size = Pt(8.5); p2.font.color.rgb = C_MUTED
        
        for b in bullets:
            p = tf.add_paragraph()
            p.text = f"• {b}"; p.font.size = Pt(8.5); p.font.color.rgb = C_DARK

    # =========================================================================
    # SLIDE 5: Detailed Competitive Analysis
    # =========================================================================
    s5 = add_content_slide("Detailed Competitive Analysis: Accel's Unfair Advantage",
                           "How Project Udyam Digital outmaneuvers traditional telcos, SaaS point tools, and resellers")
    
    # Comparison Table
    table_shape = s5.shapes.add_table(5, 5, Inches(0.6), Inches(1.2), Inches(8.8), Inches(3.8))
    t = table_shape.table
    t.columns[0].width = Inches(2.0)
    t.columns[1].width = Inches(1.8)
    t.columns[2].width = Inches(1.7)
    t.columns[3].width = Inches(1.7)
    t.columns[4].width = Inches(1.6)

    headers = ["Evaluation Metric", "Accel Udyam Digital", "Legacy Telcos (Jio/Vi)", "SaaS Point Tools", "Local Resellers"]
    for col_idx, h in enumerate(headers):
        cell = t.cell(0, col_idx)
        cell.fill.solid(); cell.fill.fore_color.rgb = C_RED if col_idx == 1 else C_DARK
        p = cell.text_frame.paragraphs[0]
        p.text = h; p.font.bold = True; p.font.size = Pt(9.5); p.font.color.rgb = C_WHITE
        p.alignment = PP_ALIGN.CENTER if col_idx > 0 else PP_ALIGN.LEFT

    matrix = [
        ("Onboarding Journey", "5-Min Digital Self-Serve\n(Phone, DigiLocker, Voice)", "14–20 Days Field Visits\n(Paper forms & physical reps)", "Instant App Download\n(Self-serve, card payment)", "Fragmented Manual\n(Cash / unorganised)"),
        ("Product Offering", "Unified Bundle\n(Broadband + SIMs + Cloud + POS)", "Siloed Products\n(SIM separate from fiber)", "Single Point Tool\n(Accounting OR POS only)", "Single piece\n(Dongle or local ISP)"),
        ("Billing & Support", "1 Consolidated Bill\nSingle enterprise support no.", "Multiple Separate Bills\nConfusing account codes", "Multiple Subscriptions\n3-4 different vendors", "No formal contract\nZero SLA or GST credit"),
        ("Network SLA & Rel.", "Commercial 99% SLA\n4-hr local fiber restoration", "Best-effort consumer SLA\nfor retail SMBs", "Dependent on 3rd-party\ninternet connectivity", "Consumer prepaid\nFrequent evening lag")
    ]
    for row_idx, row_data in enumerate(matrix, 1):
        for col_idx, text in enumerate(row_data):
            cell = t.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(254, 243, 243) if col_idx == 1 else (C_WHITE if row_idx % 2 == 0 else C_LIGHT_BG)
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.size = Pt(8.5)
            p.font.bold = (col_idx == 1 or col_idx == 0)
            p.font.color.rgb = C_RED if col_idx == 1 else C_DARK
            p.alignment = PP_ALIGN.CENTER if col_idx > 0 else PP_ALIGN.LEFT

    # =========================================================================
    # SLIDE 6: Field Force & Channel Partner Symbiosis
    # =========================================================================
    s6 = add_content_slide("Field Force & Partner Symbiosis: Empowering the Channel",
                           "Digital does not replace the human field force—it supercharges it with ML routing & warm handoffs")
    
    pillars_partner = [
        ("Assisted In-Store Portal", "For Local Channel Partners",
         "Local computer shops and retail partners use the same mobile web journey to onboard walk-in kirana owners in 5 minutes, earning instant digital commission attribution."),
        ("Warm Live Handoffs", "Zero Customer Repetition",
         "When an SMB asks for a human or KYC has a legal variance, the chat context, declared needs, and GST details sync directly to the Back Office. Reps call within 2 hours fully prepared."),
        ("ML Propensity Scoring", "Logistic Regression (AUC 0.76)",
         "Trained on 5,000 historical leads. Scores dropped leads as HIGH, MEDIUM, or LOW propensity. Top 30% of leads capture 68% of potential activations."),
        ("Optimised Dispatch", "CAC Reduction from ₹15k to ₹5.2k",
         "High-value leads get dispatched for physical field visits; low-value micro leads receive automated WhatsApp recovery nudges, maximizing field rep ROI.")
    ]
    for i, (h, sub, desc) in enumerate(pillars_partner):
        card = add_card(s6, Inches(0.6 + (i%2)*4.5), Inches(1.15 + (i//2)*2.05), Inches(4.3), Inches(1.95), C_WHITE)
        tf = card.text_frame
        tf.margin_left = tf.margin_right = Inches(0.2); tf.margin_top = Inches(0.15)
        p = tf.paragraphs[0]
        p.text = h; p.font.bold = True; p.font.size = Pt(11); p.font.color.rgb = C_RED
        p.text += f" ({sub})"; p.font.size = Pt(9); p.font.color.rgb = C_MUTED
        
        p = tf.add_paragraph()
        p.text = desc; p.font.size = Pt(9); p.font.color.rgb = C_DARK

    # =========================================================================
    # SLIDE 7: Business Impact & Rollout Plan
    # =========================================================================
    s7 = add_content_slide("Business Impact, Unit Economics & 12-Month Rollout",
                           "Measurable business transformation backed by empirical data and phased execution")
    
    # Left: Impact Metrics Table
    c_m = add_card(s7, Inches(0.6), Inches(1.15), Inches(5.0), Inches(4.1), C_WHITE)
    tf = c_m.text_frame
    tf.margin_left = tf.margin_right = Inches(0.2); tf.margin_top = Inches(0.15)
    p = tf.paragraphs[0]
    p.text = "Key Success Metrics (Target vs Baseline)"
    p.font.bold = True; p.font.size = Pt(11); p.font.color.rgb = C_DARK
    
    kpis = [
        ("Lead-to-Activation Rate", "7.4%", "15.5%", "+110% lift (removes quote & KYC cliffs)"),
        ("Time to Activate", "17.6 days", "5.0 days", "-72% cycle time reduction"),
        ("Blended CAC", "₹15,000", "₹5,200", "-65% via digital self-serve & ML routing"),
        ("Support Chase Calls", "3.0 calls", "0.2 calls", "Proactive tracker & WhatsApp alerts"),
        ("6-Month Micro Churn", "36%", "<7%", "Right-sized starter pricing (<₹1,500 cap)")
    ]
    for kpi, base, tgt, note in kpis:
        p = tf.add_paragraph()
        p.text = f"• {kpi}: "; p.font.bold = True; p.font.size = Pt(9); p.font.color.rgb = C_DARK
        p.text += f"{base} → "; p.font.size = Pt(9); p.font.color.rgb = C_MUTED
        p.text += f"{tgt} "; p.font.bold = True; p.font.size = Pt(9.5); p.font.color.rgb = C_GREEN
        p.text += f"({note})"; p.font.size = Pt(8); p.font.color.rgb = C_MUTED

    # Right: 12-Month Rollout Roadmap
    c_r = add_card(s7, Inches(5.8), Inches(1.15), Inches(3.6), Inches(4.1), C_WHITE)
    tf = c_r.text_frame
    tf.margin_left = tf.margin_right = Inches(0.2); tf.margin_top = Inches(0.15)
    p = tf.paragraphs[0]
    p.text = "12-Month Rollout Roadmap"
    p.font.bold = True; p.font.size = Pt(11); p.font.color.rgb = C_DARK
    
    phases = [
        ("Months 1–3: Pilot Launch", "Deploy in Delhi NCR & Pune across Professional Offices & Kirana segments. Validate DigiLocker & UPI Autopay."),
        ("Months 4–6: Partner Enablement", "Integrate 500+ local channel partners with the assisted onboarding portal and live commission tracking."),
        ("Months 7–9: Regional Scale", "Expand vernacular support to Tamil, Telugu, Marathi, and Bengali. Scale back-office ML lead recovery."),
        ("Months 10–12: Pan-India Expansion", "Full nationwide rollout across 100+ cities. Target: 50,000 active MSME bundles activated.")
    ]
    for ph, det in phases:
        p = tf.add_paragraph()
        p.text = f"▶ {ph}"; p.font.bold = True; p.font.size = Pt(9); p.font.color.rgb = C_RED
        p = tf.add_paragraph()
        p.text = det; p.font.size = Pt(8.5); p.font.color.rgb = C_DARK

    prs.save(OUTPUT_PATH)
    print(f"Presentation successfully saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    create_deck()
