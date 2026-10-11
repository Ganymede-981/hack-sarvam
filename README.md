# ⚡ Sarvam Document Intelligence Agent

An autonomous Document Intelligence Agent built with **Sarvam AI** for the hackathon. It ingests unstructured documents (scanned invoices, bilingual Indic forms, financial reports), extracts validated structured entities, stores them in a unified analytics repository, renders a real-time BI dashboard, triggers risk/approval workflows, and provides a Natural Language SQL Copilot.

---

## 🏗️ Architecture

```
PDF / Scan / Indic Invoice
        │
        ▼
[1] Sarvam Document Intelligence API
    ➔ Extracted markdown / text (with native Indic script & scan support)
        │
        ▼
[2] Sarvam Chat LLM + Pydantic v2 Schema
    ➔ Document classification + line items + entity extraction
        │
        ▼
[3] SQLite Unified Data Repository
    ➔ `documents`, `line_items`, and `alerts_log` tables
        │
        ├──▶ [4] Streamlit Executive BI Dashboard
        │         KPIs · Vendor Spend · Trends · Power BI/Tableau CSV Export
        │
        ├──▶ [5] Autonomous Rules Engine
        │         High-value approval (>₹1L) · Duplicates · Sum mismatch · Slack alerts
        │
        └──▶ [6] Natural Language SQL Copilot
                  Text ➔ Validated SQLite ➔ Live data insight
```

---

## 🚀 Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
# or: pip install streamlit plotly pandas pydantic requests python-dotenv
```

### 2. Configure Environment (Optional)
Create a `.env` file or enter your API key directly in the Streamlit UI sidebar:
```env
SARVAM_API_KEY=your_sarvam_api_key_here
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/... (optional)
```

*(Note: The agent contains an offline high-fidelity fallback cache so the entire pipeline and dashboard can also be demoed with zero downtime even without an active internet connection).*

### 3. Launch the Application
```bash
streamlit run app.py
```

---

## 🎬 2-Minute Demo Script

1. **Load Pre-Packaged Dataset:**
   - In the sidebar, click **"📥 Load 4 Samples"**.
   - Notice all 4 diverse documents ingested simultaneously: Indic bilingual bill, high-value consulting invoice, audit compliance report, and an invoice with a line item mismatch.
2. **Explore Executive BI Dashboard (Tab 2):**
   - Review high-level KPIs (Total Spend, Flagged Count, Critical Approvals).
   - Show interactive Plotly charts: Horizontal spend by vendor and classification donut chart.
   - Click **"📥 Export BI-Ready CSV"** to demonstrate Power BI / Tableau readiness.
   - Expand the **"🔎 Line Items Drill-Down"** to show individual item records.
3. **Trigger Workflow Rules & Approvals (Tab 4):**
   - Point out the **`CRITICAL`** approval triggered on the ₹2.45L TCS invoice.
   - Point out the **`WARNING`** flagged on the Swiggy invoice where line items sum differs from printed grand total.
   - Point out the **`INFO`** badge for native Indic script recognition on the Reliance Retail invoice.
4. **Natural Language Query Copilot (Tab 3):**
   - Click one of the prompt chips (e.g., *"🏆 Highest spend vendor?"* or *"🚩 Show flagged documents"*).
   - Watch the agent translate natural language to safe SQLite queries and execute them live.
