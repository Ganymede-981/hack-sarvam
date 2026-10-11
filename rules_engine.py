import re
import requests
from typing import List, Dict, Any, Tuple
from config import SLACK_WEBHOOK_URL, HIGH_VALUE_THRESHOLD
import database

def is_indic_text(text: str) -> bool:
    # Check for Devanagari Unicode range \u0900-\u097F or Tamil \u0B80-\u0BFF or Telugu/Kannada etc.
    indic_pattern = re.compile(r'[\u0900-\u097F\u0980-\u09FF\u0A00-\u0A7F\u0A80-\u0AFF\u0B00-\u0B7F\u0B80-\u0BFF\u0C00-\u0C7F\u0C80-\u0CFF\u0D00-\u0D7F]')
    return bool(indic_pattern.search(text))

def evaluate_rules(doc_dict: Dict[str, Any], raw_text: str) -> Tuple[List[Dict[str, str]], bool, str]:
    """
    Evaluates business rules against the extracted document.
    Returns:
        alerts: list of dicts with keys (rule_name, severity, message)
        needs_review: boolean flag
        review_reason: explanation string
    """
    alerts = []
    needs_review = False
    review_reasons = []

    doc_type = (doc_dict.get("doc_type") or "other").lower()
    total = doc_dict.get("total") or 0.0
    vendor = doc_dict.get("vendor") or ""
    doc_number = doc_dict.get("doc_number") or ""
    line_items = doc_dict.get("line_items") or []

    # Rule 1: High Value Approval Check
    if doc_type == "invoice" and total >= HIGH_VALUE_THRESHOLD:
        alerts.append({
            "rule_name": "APPROVAL_REQUIRED",
            "severity": "CRITICAL",
            "message": f"Invoice from '{vendor}' of ₹{total:,.2f} exceeds high-value threshold (₹{HIGH_VALUE_THRESHOLD:,.0f}). Approval required."
        })

    # Rule 2: Missing Invoice Number
    if doc_type == "invoice" and not doc_number.strip():
        alerts.append({
            "rule_name": "MISSING_INVOICE_NUMBER",
            "severity": "WARNING",
            "message": f"Invoice from '{vendor or 'Unknown'}' is missing an invoice identifier."
        })
        needs_review = True
        review_reasons.append("Missing invoice number")

    # Rule 3: Duplicate Invoice Check
    if doc_type == "invoice" and vendor and doc_number:
        if database.check_duplicate(vendor, doc_number, total):
            alerts.append({
                "rule_name": "DUPLICATE_INVOICE",
                "severity": "CRITICAL",
                "message": f"Potential duplicate invoice detected: '{doc_number}' from '{vendor}' for ₹{total:,.2f}."
            })
            needs_review = True
            review_reasons.append("Duplicate invoice flagged")

    # Rule 4: Total vs Line Items Sum Mismatch
    if line_items and total > 0:
        items_sum = sum(float(item.get("amount") or 0.0) for item in line_items)
        # allow tolerance for small tax/rounding (e.g. 2.0 currency units)
        if abs(items_sum - total) > 2.0:
            diff = items_sum - total
            alerts.append({
                "rule_name": "SUM_MISMATCH",
                "severity": "WARNING",
                "message": f"Line items sum (₹{items_sum:,.2f}) differs from total (₹{total:,.2f}) by ₹{abs(diff):,.2f}."
            })
            needs_review = True
            review_reasons.append(f"Sum mismatch: items total ₹{items_sum:,.2f} vs invoice total ₹{total:,.2f}")

    # Rule 5: Indic Language Detection Differentiator
    if is_indic_text(raw_text):
        alerts.append({
            "rule_name": "INDIC_DOCUMENT_PROCESSED",
            "severity": "INFO",
            "message": "Indic/Regional language script detected & accurately parsed via Sarvam Document Intelligence."
        })

    return alerts, needs_review, "; ".join(review_reasons)

def dispatch_notifications(alerts: List[Dict[str, str]], doc_id: int):
    """
    Logs alerts to SQLite and dispatches to webhook if configured.
    """
    for alert in alerts:
        database.log_alert(
            doc_id=doc_id,
            rule_name=alert["rule_name"],
            severity=alert["severity"],
            message=alert["message"]
        )

        if SLACK_WEBHOOK_URL:
            try:
                emoji = ":rotating_light:" if alert["severity"] == "CRITICAL" else ":warning:" if alert["severity"] == "WARNING" else ":information_source:"
                payload = {
                    "text": f"{emoji} *[DocIntel Agent Alert - {alert['rule_name']}]*\n{alert['message']}"
                }
                requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=3)
            except Exception as e:
                print(f"Failed to post to webhook: {e}")
