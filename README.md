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

<img width="1897" height="823" alt="Screenshot 2026-10-11 204741" src="https://github.com/user-attachments/assets/c8c3e72c-09f6-4992-a095-d61081384b8f" />
