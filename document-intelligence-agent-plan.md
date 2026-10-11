# Document Intelligence Agent: 45-Minute Implementation Plan

*Sarvam Hackathon build plan. One thin vertical slice: upload, extract, structure, query/dashboard, trigger alert.*

## 1. Goal and Strategy

Build an agent that turns unstructured documents (PDFs, forms, invoices, reports, scans) into a unified queryable dataset, produces analytics-ready dashboards, and triggers business workflows (alerts, approvals) from the extracted data.

**Strategy:** a working loop on 3 to 4 sample documents beats a broad half-built system. Demo one complete flow end to end.

**Non-negotiable core:** extraction, database, dashboard, one alert.

## 2. Architecture

```
 PDF / scan / invoice
        |
        v
 [1] Sarvam Document Intelligence API -> markdown/text (scans + Indic languages)
        |
        v
 [2] Sarvam chat LLM (JSON prompt) -> classify doc type + extract fields
        |
        v
 [3] Validation (pydantic) -> SQLite (documents + line_items)
        |
        +--> [4] Streamlit dashboard: KPIs, vendor spend, trends, NL query box
        |
        +--> [5] Rules engine -> alerts / approvals (Slack webhook or UI log)
```

## 3. Stack

- Python with the `sarvamai` SDK; Sarvam API key in an environment variable
- pydantic for schemas, SQLite plus pandas for storage
- Streamlit for upload UI, dashboard and chat in a single file
- Plotly for charts
- Slack or Discord webhook for alerts (fallback: an "Actions" panel in the UI)

Install: `pip install sarvamai streamlit pandas plotly pydantic`

## 4. Timeline

| Minutes | Task | Done when |
|---|---|---|
| 0-5 | Setup: API key, install packages, collect 3-4 sample docs (2 invoices, 1 scanned or Hindi/Indic doc, 1 report) | Hello-world API call works |
| 5-15 | Extraction: Document Intelligence call to text/markdown | A sample PDF returns clean text |
| 15-25 | Structuring: LLM classifies doc type and extracts JSON, validated and saved to SQLite | 3 docs in the DB |
| 25-33 | Dashboard: KPIs, spend by vendor, monthly trend, raw table | Charts render from the DB |
| 33-39 | Workflow: rules trigger alert or approval | Uploading a large invoice fires an alert |
| 39-43 | NL query: question to SQL to result to answer | One query works live |
| 43-45 | Rehearse demo | Demo runs clean |

## 5. Component Details

### 5.1 Extraction (min 5-15)

Call the Sarvam Document Intelligence API with the file, wait for the job, download the markdown output. Verify exact method names in the Sarvam docs, as the SDK changes between releases.

```python
from sarvamai import SarvamAI
client = SarvamAI(api_subscription_key=KEY)

def ocr(path):
    job = client.document_intelligence.create_job(language="en-IN", output_format="md")
    job.upload_file(path)
    job.start()
    job.wait_until_complete()
    job.download_output("out.zip")   # unzip, read the .md
    return open("out/doc.md").read()
```

### 5.2 Structuring (min 15-25)

Use a pydantic schema and a strict JSON-only prompt. Retry once on validation failure.

```python
from pydantic import BaseModel
from typing import Optional, List

class LineItem(BaseModel):
    description: str
    qty: Optional[float]
    amount: float

class Doc(BaseModel):
    doc_type: str            # invoice | report | form | other
    vendor: Optional[str]
    doc_number: Optional[str]
    date: Optional[str]
    currency: Optional[str]
    total: Optional[float]
    line_items: List[LineItem] = []
    summary: str

SYSTEM = """Extract fields from the document. Return ONLY valid JSON matching:
{doc_type, vendor, doc_number, date(YYYY-MM-DD), currency, total,
line_items[{description,qty,amount}], summary}.
Use null for missing values. No markdown fences."""

def extract(text):
    r = client.chat.completions(messages=[
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": text[:12000]}])
    raw = r.choices[0].message.content.strip().strip("`").removeprefix("json")
    return Doc.model_validate_json(raw)   # retry once on ValidationError
```

**Storage:** two SQLite tables, `documents` (one row per doc, including a review flag and source filename) and `line_items` (foreign key to documents).

### 5.3 Dashboard (min 25-33)

Streamlit page with:

- KPI row: total documents, total spend, number flagged for review
- Bar chart: spend by vendor
- Line chart: monthly spend trend
- Raw table of all documents
- "Download CSV" button (covers the BI-ready requirement for Power BI or Tableau)

### 5.4 Workflow Rules (min 33-39)

```python
RULES = [
  (lambda d: d.doc_type == "invoice" and (d.total or 0) > 100000, "APPROVAL_REQUIRED"),
  (lambda d: d.doc_type == "invoice" and not d.doc_number,        "MISSING_FIELDS"),
  (lambda d: is_duplicate(d),                                      "DUPLICATE_INVOICE"),
]

def run_rules(d):
    for cond, action in RULES:
        if cond(d):
            notify_slack(f"{action}: {d.vendor} {d.total}")
```

Also log every fired action to an "Actions" panel in the UI so the demo works even if the webhook fails.

### 5.5 Natural-Language Query (min 39-43)

1. Give the LLM the table schema and the user's question.
2. Ask for a single `SELECT` statement only.
3. Reject anything that is not a `SELECT` (safety check).
4. Execute on SQLite.
5. Have the LLM summarize the returned rows in plain language.

## 6. Differentiators (Cheap Wins)

- **Indic-language documents:** Sarvam's strength is Indic scripts. Include at least one Hindi or other Indic invoice or scan in the demo.
- **Confidence flags:** if the sum of line items does not equal the total, mark "needs review". Three lines of code, and it shows real-world thinking.
- **Unified dataset:** CSV export for BI tools.
- **Optional voice:** if time remains, use Sarvam speech-to-text to ask dashboard questions by voice.

## 7. Risks and Cut Lines

| Risk | Mitigation |
|---|---|
| OCR job is slow or async | Pre-process demo docs ahead of time, cache outputs, run live on only one doc |
| LLM returns invalid JSON | One retry with "Return only JSON", plus a try/except fallback |
| Webhook fails | Show alerts in the UI Actions panel |
| SDK method names differ | Check the Sarvam docs in the first 5 minutes |

**Cut order:** NL query, then voice, then duplicate check.

**Never cut:** extraction, database, dashboard, one alert.

## 8. Demo Script (2-3 Minutes)

1. Drop in 3 messy documents, including a scan or Indic-language one.
2. Show the structured table appear.
3. Dashboard updates with spend by vendor.
4. Upload an oversized invoice and the approval alert fires.
5. Ask "Which vendor did we pay the most this month?" and show the answer.

## 9. Pre-Start Checklist

- [ ] Sarvam API key works
- [ ] 3-4 sample documents ready (at least one scanned or Indic)
- [ ] Package install complete
- [ ] Slack or Discord webhook URL ready (optional)
- [ ] Exact SDK method and model names verified in the Sarvam docs
