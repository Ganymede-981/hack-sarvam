import os
import io
import time
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import config
import database
import sarvam_client
import rules_engine
import pipeline

# Page Configuration
st.set_page_config(
    page_title="Sarvam Document Intelligence Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Typography & Colors */
    * {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, pre, .stCodeBlock {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Streamlit Main App Container */
    .stApp {
        background-color: #090d16;
        color: #f1f5f9;
    }

    /* Remove Streamlit default header decoration */
    header[data-testid="stHeader"] {
        background: transparent;
    }
    
    #MainMenu, footer {
        visibility: hidden;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0d121f;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #f8fafc;
        font-size: 1.15rem;
        font-weight: 700;
        letter-spacing: -0.01em;
        margin-bottom: 1rem;
    }

    /* Hero Header Card */
    .hero-card {
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-top: 2px solid #06b6d4;
        border-radius: 16px;
        padding: 24px 30px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(6, 182, 212, 0.12);
        color: #22d3ee;
        border: 1px solid rgba(6, 182, 212, 0.3);
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        white-space: nowrap;
    }

    .pulse-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10b981;
        box-shadow: 0 0 8px #10b981;
        display: inline-block;
    }

    /* KPI Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }

    .kpi-box {
        background: #111827;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        position: relative;
        overflow: hidden;
    }

    .kpi-box::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
    }

    .kpi-blue::after { background: linear-gradient(90deg, #38bdf8, #2563eb); }
    .kpi-green::after { background: linear-gradient(90deg, #34d399, #059669); }
    .kpi-amber::after { background: linear-gradient(90deg, #fbbf24, #d97706); }
    .kpi-rose::after { background: linear-gradient(90deg, #f87171, #dc2626); }

    .kpi-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 6px;
    }

    .kpi-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.02em;
        margin-bottom: 4px;
    }

    .kpi-subtext {
        font-size: 0.8rem;
        color: #64748b;
    }

    /* Badges */
    .badge-critical {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.35);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.03em;
    }

    .badge-warning {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.35);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.03em;
    }

    .badge-info {
        background: rgba(6, 182, 212, 0.15);
        color: #22d3ee;
        border: 1px solid rgba(6, 182, 212, 0.35);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.03em;
    }

    /* Streamlit Tabs Polish */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 6px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 42px;
        padding: 0 16px;
        background-color: transparent;
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.92rem;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(6, 182, 212, 0.12) !important;
        color: #22d3ee !important;
        border: 1px solid rgba(6, 182, 212, 0.3) !important;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.15s ease-in-out;
    }

    /* Info card */
    .status-panel {
        background: #111827;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Database
database.init_db()

# Reload environment configuration dynamically
current_api_key = config.reload_config()
is_live_api = bool(current_api_key and current_api_key.strip())

# Sidebar: Controls & Live System Status
with st.sidebar:
    st.markdown("### ⚡ System Status")
    
    status_color = "#10b981" if is_live_api else "#fbbf24"
    status_label = "Live API Connected" if is_live_api else "Standby (Key in .env)"
    dot_html = '<span class="pulse-dot"></span>' if is_live_api else '⚠️'

    st.markdown(f"""
    <div class="status-panel">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 0.82rem; color: #94a3b8; font-weight: 600;">SARVAM ENGINE</span>
            <span style="font-size: 0.78rem; color: {status_color}; font-weight: 700; display: flex; align-items: center; gap: 4px;">
                {dot_html} {status_label}
            </span>
        </div>
        <div style="font-size: 0.85rem; color: #e2e8f0; font-weight: 500;">
            {"Sarvam Document Intelligence + LLM" if is_live_api else "Awaiting SARVAM_API_KEY in .env"}
        </div>
        {"<div style='font-size: 0.75rem; color: #94a3b8; margin-top: 6px;'>Live cloud extraction active for all PDFs, scans & text.</div>" if is_live_api else "<div style='font-size: 0.75rem; color: #fbbf24; margin-top: 6px;'>Add your <code>SARVAM_API_KEY=...</code> to <code>.env</code> to connect live cloud jobs.</div>"}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="status-panel" style="padding: 12px 16px; margin-top: -6px;">
        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px;">
            <span style="color: #64748b;">Pipeline Mode</span>
            <span style="color: #cbd5e1; font-weight: 600;">Sarvam v0.1 SDK</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px;">
            <span style="color: #64748b;">Indic Scripts</span>
            <span style="color: #cbd5e1; font-weight: 600;">Hindi / Regional / En</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
            <span style="color: #64748b;">Storage</span>
            <span style="color: #cbd5e1; font-weight: 600;">SQLite Relational</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### ⚡ Demo Actions")
    
    if st.button("📥 Load 4 Sample Documents", use_container_width=True, type="primary"):
        with st.spinner("Ingesting sample suite (Indic, High-Value, Discrepant, Report)..."):
            results = pipeline.seed_sample_documents(api_key=config.SARVAM_API_KEY)
            st.success(f"Ingested {len(results)} sample documents!")
            st.rerun()

    if st.button("🗑️ Reset Database Records", use_container_width=True):
        conn = database.get_connection()
        conn.execute("DELETE FROM line_items")
        conn.execute("DELETE FROM documents")
        conn.execute("DELETE FROM alerts_log")
        conn.commit()
        conn.close()
        st.warning("Database cleared.")
        st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.82rem; color: #64748b; line-height: 1.6;">
        <strong style="color: #94a3b8;">Key Capabilities:</strong><br>
        • Bilingual Indic &amp; Scans extraction<br>
        • Strict Pydantic v2 schemas<br>
        • Automated business approval rules<br>
        • Natural Language Text-to-SQL
    </div>
    """, unsafe_allow_html=True)

# Main Hero Header
st.markdown("""
<div class="hero-card">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
        <div>
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                <h1 style="margin: 0; font-size: 1.85rem; font-weight: 800; color: #f8fafc; letter-spacing: -0.02em;">
                    Sarvam Document Intelligence Agent
                </h1>
            </div>
            <p style="margin: 0; color: #94a3b8; font-size: 0.95rem; font-weight: 400; max-width: 780px;">
                End-to-end extraction from unstructured Indic &amp; English documents into structured schemas, real-time BI analytics, and automated approval workflows.
            </p>
        </div>
        <div class="hero-badge">
            <span class="pulse-dot"></span>
            Sarvam Indic Engine Connected
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Tabs
tab_ingest, tab_dash, tab_copilot, tab_alerts = st.tabs([
    "📥 Ingest & Live Extract",
    "📊 Executive BI Dashboard",
    "🤖 NL SQL Copilot",
    "🚨 Workflow Rules & Alerts Feed"
])

# -------------------------------------------------------------
# TAB 1: INGESTION & REAL-TIME EXTRACTION
# -------------------------------------------------------------
with tab_ingest:
    st.markdown("### Document Ingestion & Verification")
    st.markdown("Upload any vendor invoice, scan, or report, or select a pre-loaded sample document below.")
    
    col_up, col_preset = st.columns([1, 1], gap="large")
    
    with col_up:
        st.markdown("##### 📁 Option A: Upload Custom Document")
        uploaded_file = st.file_uploader(
            "Upload file",
            type=["txt", "md", "csv", "pdf", "png", "jpg"],
            label_visibility="collapsed"
        )

    with col_preset:
        st.markdown("##### ⚡ Option B: Select Pre-Loaded Sample")
        sample_files = list(config.SAMPLE_DOCS_DIR.glob("*.*"))
        sample_names = ["-- Select Pre-Loaded Sample --"] + [f.name for f in sample_files]
        chosen_sample = st.selectbox("Sample Selector", sample_names, label_visibility="collapsed")
        
        sample_hints = {
            "1_invoice_reliance_indic.txt": "🇮🇳 Reliance Retail: Bilingual Hindi & English invoice.",
            "2_invoice_tcs_high_value.txt": "🚨 TCS Consulting: ₹2.45 Lakh invoice (Triggers >₹1L Approval Rule).",
            "3_invoice_swiggy_mismatch.txt": "⚠️ Swiggy: Line items total ₹1,450 vs Grand Total ₹1,850 (Triggers Discrepancy Flag).",
            "4_quarterly_vendor_audit_report.txt": "📑 Financial Audit Report: Auto-classified as 'report' doc_type."
        }
        if chosen_sample in sample_hints:
            st.caption(f"💡 {sample_hints[chosen_sample]}")

    doc_to_process = None
    doc_filename = ""
    
    if uploaded_file is not None:
        temp_path = config.BASE_DIR / f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        doc_to_process = temp_path
        doc_filename = uploaded_file.name
    elif chosen_sample != "-- Select Pre-Loaded Sample --":
        doc_to_process = config.SAMPLE_DOCS_DIR / chosen_sample
        doc_filename = chosen_sample

    if doc_to_process is not None:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button(f"⚡ Run Pipeline on {doc_filename}", type="primary", use_container_width=True):
            with st.status("Executing Document Intelligence Pipeline...", expanded=True) as status:
                st.write("🔍 **Step 1:** Extracting text & Indic scripts via Sarvam Document Intelligence...")
                time.sleep(0.2)
                
                st.write("📐 **Step 2:** Pydantic schema validation & entity classification via Chat LLM...")
                time.sleep(0.2)
                
                st.write("⚖️ **Step 3:** Evaluating business rules (High Value, Duplicates, Sum Checks)...")
                res = pipeline.process_document(doc_to_process, filename=doc_filename, api_key=config.SARVAM_API_KEY)
                time.sleep(0.1)
                
                st.write("💾 **Step 4:** Persisted records into unified SQLite repository.")
                status.update(label="Document Processed & Saved Successfully!", state="complete", expanded=False)

            st.success(f"Successfully processed **{doc_filename}** (Assigned Document ID #{res['doc_id']})")
            
            c1, c2 = st.columns([1, 1], gap="medium")
            with c1:
                st.markdown("##### 📄 Extracted Structured Entity")
                st.json(res["doc"])
            
            with c2:
                st.markdown("##### 🚨 Triggered Rules & Validation")
                if res["alerts"]:
                    for a in res["alerts"]:
                        badge_class = "badge-critical" if a["severity"] == "CRITICAL" else "badge-warning" if a["severity"] == "WARNING" else "badge-info"
                        border_color = "#ef4444" if a["severity"] == "CRITICAL" else "#f59e0b" if a["severity"] == "WARNING" else "#06b6d4"
                        st.markdown(f"""
                        <div style="background: #111827; border: 1px solid rgba(255,255,255,0.08); border-left: 4px solid {border_color}; border-radius: 8px; padding: 12px 16px; margin-bottom: 10px;">
                            <span class="{badge_class}">{a['rule_name']}</span>
                            <p style="margin: 8px 0 0 0; color: #e2e8f0; font-size: 0.9rem;">{a['message']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No rule violations detected. Document passed validation cleanly.")

                with st.expander("Show Extracted Raw Text"):
                    st.text_area("Raw Text", res["raw_text"], height=180)

# -------------------------------------------------------------
# TAB 2: EXECUTIVE BI DASHBOARD
# -------------------------------------------------------------
with tab_dash:
    df_docs = database.get_all_documents()
    
    if df_docs.empty:
        st.info("No documents in the database yet. Click **'📥 Load 4 Sample Documents'** in the sidebar to populate the dashboard.")
    else:
        # Top KPI Metric Row
        total_docs = len(df_docs)
        total_spend = df_docs["total"].fillna(0).sum()
        flagged_count = (df_docs["needs_review"] == 1).sum()
        alerts_df = database.get_all_alerts(limit=100)
        critical_alerts_count = (alerts_df["severity"] == "CRITICAL").sum() if not alerts_df.empty else 0

        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-box kpi-blue">
                <div class="kpi-label">Total Processed</div>
                <div class="kpi-value">{total_docs}</div>
                <div class="kpi-subtext">Multi-format &amp; Indic documents</div>
            </div>
            <div class="kpi-box kpi-green">
                <div class="kpi-label">Total Spend (INR)</div>
                <div class="kpi-value">₹{total_spend:,.2f}</div>
                <div class="kpi-subtext">Across verified vendors</div>
            </div>
            <div class="kpi-box kpi-amber">
                <div class="kpi-label">Needs Review</div>
                <div class="kpi-value">{flagged_count}</div>
                <div class="kpi-subtext">Discrepancies flagged for audit</div>
            </div>
            <div class="kpi-box kpi-rose">
                <div class="kpi-label">Critical Approvals</div>
                <div class="kpi-value">{critical_alerts_count}</div>
                <div class="kpi-subtext">Exceeding ₹1L or duplicates</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Visual Analytics Row
        ch1, ch2 = st.columns([1.4, 1], gap="medium")
        with ch1:
            vendor_spend = df_docs.groupby("vendor")["total"].sum().reset_index().sort_values(by="total", ascending=True)
            fig_bar = px.bar(
                vendor_spend,
                x="total",
                y="vendor",
                orientation="h",
                title="Spend by Vendor (INR)",
                labels={"total": "Total Amount (₹)", "vendor": "Vendor"},
                color="total",
                color_continuous_scale="Tealgrn"
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickprefix="₹"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
                margin=dict(l=10, r=10, t=35, b=10),
                height=300
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with ch2:
            doc_types = df_docs["doc_type"].value_counts().reset_index()
            doc_types.columns = ["doc_type", "count"]
            fig_pie = px.pie(
                doc_types,
                names="doc_type",
                values="count",
                title="Document Classification Breakdown",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8"),
                margin=dict(l=10, r=10, t=35, b=10),
                height=300
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        # Full Unified Data Table & CSV Export
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        t_col1, t_col2 = st.columns([3, 1])
        with t_col1:
            st.markdown("#### 📑 Unified Document Dataset")
        with t_col2:
            csv_data = df_docs.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export BI-Ready CSV",
                data=csv_data,
                file_name="sarvam_document_intelligence_export.csv",
                mime="text/csv",
                use_container_width=True
            )

        show_flagged_only = st.checkbox("Filter to documents requiring review / audit", value=False)
        display_df = df_docs[df_docs["needs_review"] == 1] if show_flagged_only else df_docs

        st.dataframe(
            display_df[[
                "id", "filename", "doc_type", "vendor", "doc_number", "date", "total", "item_count", "needs_review", "review_reason"
            ]],
            use_container_width=True,
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),
                "total": st.column_config.NumberColumn("Total (₹)", format="₹%.2f"),
                "needs_review": st.column_config.CheckboxColumn("Needs Review?"),
                "item_count": st.column_config.NumberColumn("Items"),
            }
        )

        with st.expander("🔎 Line Items & Document Drill-Down"):
            selected_doc_id = st.selectbox(
                "Select Document to inspect line items",
                df_docs["id"].tolist(),
                format_func=lambda x: f"Doc #{x} - {df_docs.loc[df_docs['id'] == x, 'vendor'].values[0]} (₹{df_docs.loc[df_docs['id'] == x, 'total'].values[0]:,.2f})"
            )
            if selected_doc_id:
                details = database.get_document_details(selected_doc_id)
                d = details["doc"]
                st.markdown(f"**Executive Summary:** {d['summary']}")
                if details["line_items"]:
                    df_items = pd.DataFrame(details["line_items"])
                    st.dataframe(
                        df_items[["description", "qty", "unit_price", "amount"]],
                        use_container_width=True,
                        column_config={"amount": st.column_config.NumberColumn("Amount (₹)", format="₹%.2f")}
                    )
                else:
                    st.info("No individual line items parsed for this document.")

# -------------------------------------------------------------
# TAB 3: NATURAL LANGUAGE SQL COPILOT
# -------------------------------------------------------------
with tab_copilot:
    st.markdown("### 🤖 Natural Language Query Copilot")
    st.markdown("Query the verified database using plain English. The agent converts business intent into safe SQLite SELECT queries.")

    if "copilot_query" not in st.session_state:
        st.session_state["copilot_query"] = "Which vendor did we pay the most?"

    st.markdown("**Suggested Quick Inquiries:**")
    quick_q_cols = st.columns(4)
    with quick_q_cols[0]:
        if st.button("🏆 Highest spend vendor?", key="btn_top_vendor"):
            st.session_state["copilot_query"] = "Which vendor did we pay the most?"
            st.rerun()
    with quick_q_cols[1]:
        if st.button("🚩 Show flagged documents", key="btn_flagged"):
            st.session_state["copilot_query"] = "Show all documents that require audit review"
            st.rerun()
    with quick_q_cols[2]:
        if st.button("📊 Spend by vendor", key="btn_spend"):
            st.session_state["copilot_query"] = "Show total spend broken down by each vendor"
            st.rerun()
    with quick_q_cols[3]:
        if st.button("🔍 Invoices over ₹1 Lakh", key="btn_high_val"):
            st.session_state["copilot_query"] = "Find all invoices with total greater than 100000"
            st.rerun()

    user_query = st.text_input(
        "Enter question:",
        value=st.session_state.get("copilot_query", ""),
        placeholder="e.g. Which vendor did we pay the most this month?",
        label_visibility="collapsed",
        key="query_text_input"
    )

    if st.button("⚡ Execute Query", type="primary") or user_query:
        query_to_run = user_query.strip() if user_query.strip() else st.session_state.get("copilot_query", "")
        if not query_to_run:
            st.warning("Please enter a question.")
        else:
            with st.spinner("Translating natural language intent to SQL with Sarvam AI..."):
                schema_desc = """
                Table documents (id, filename, doc_type, vendor, doc_number, date, currency, total, needs_review, review_reason)
                Table line_items (id, doc_id, description, qty, unit_price, amount)
                Table alerts_log (id, doc_id, rule_name, severity, message, created_at)
                """
                sql = sarvam_client.generate_sql_from_question(query_to_run, schema_desc, api_key=config.SARVAM_API_KEY)
                
                c_sql, c_res = st.columns([1, 1.4], gap="medium")
                with c_sql:
                    st.markdown("##### ⚙️ Generated Safe SQL")
                    st.code(sql, language="sql")
                
                with c_res:
                    st.markdown("##### 📊 Query Execution Result")
                    try:
                        res_df = database.execute_raw_select(sql)
                        if res_df.empty:
                            st.info("Query returned 0 rows.")
                        else:
                            st.dataframe(res_df)
                    except Exception as e:
                        st.error(f"SQL Execution Error: {e}")

# -------------------------------------------------------------
# TAB 4: WORKFLOW RULES & ALERTS FEED
# -------------------------------------------------------------
with tab_alerts:
    st.markdown("### 🚨 Autonomous Workflow Rules & Alerts Feed")
    st.markdown("Automated governance events fired when documents trigger risk conditions (High Value >₹1L, Duplicate detection, or Line-Item Sum mismatches).")

    alerts_df = database.get_all_alerts(limit=50)
    if alerts_df.empty:
        st.info("No alerts logged yet. Process a sample document or load the demo dataset to trigger rules.")
    else:
        for _, row in alerts_df.iterrows():
            severity = row["severity"]
            badge_class = "badge-critical" if severity == "CRITICAL" else "badge-warning" if severity == "WARNING" else "badge-info"
            border_color = "#ef4444" if severity == "CRITICAL" else "#f59e0b" if severity == "WARNING" else "#06b6d4"
            
            st.markdown(f"""
            <div style="background: #111827; border: 1px solid rgba(255,255,255,0.07); border-left: 4px solid {border_color}; border-radius: 10px; padding: 14px 18px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <div>
                        <span class="{badge_class}">{row['rule_name']}</span>
                        <span style="color: #94a3b8; font-size: 0.85rem; margin-left: 8px;">Doc #{row['doc_id']} • {row['vendor'] or 'N/A'}</span>
                    </div>
                    <div style="color: #64748b; font-size: 0.78rem;">{row['created_at']}</div>
                </div>
                <div style="color: #e2e8f0; font-size: 0.92rem; line-height: 1.5;">{row['message']}</div>
            </div>
            """, unsafe_allow_html=True)
