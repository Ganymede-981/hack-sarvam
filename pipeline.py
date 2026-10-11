import os
from pathlib import Path
from typing import Dict, Any, Optional

import database
import sarvam_client
import rules_engine
from config import SAMPLE_DOCS_DIR

def process_document(file_path: Path, filename: Optional[str] = None, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Executes the end-to-end pipeline:
    Extraction -> Pydantic Structuring -> Rules Engine -> DB Persist -> Alerts
    """
    fname = filename or file_path.name
    
    # 1. Extraction (Sarvam Document Intelligence / Cache)
    raw_text = sarvam_client.extract_text_from_file(file_path, api_key=api_key)

    # 2. Structuring (Sarvam Chat / Heuristic schema validation)
    doc_struct = sarvam_client.structure_document(raw_text, fname, api_key=api_key)
    doc_dict = doc_struct.model_dump()

    # 3. Rules Engine (Approvals, duplicates, sum checks, Indic detection)
    alerts, needs_review, review_reason = rules_engine.evaluate_rules(doc_dict, raw_text)

    # 4. Storage (SQLite documents + line_items)
    doc_id = database.save_document(
        filename=fname,
        doc_type=doc_dict.get("doc_type", "other"),
        vendor=doc_dict.get("vendor"),
        doc_number=doc_dict.get("doc_number"),
        date=doc_dict.get("date"),
        currency=doc_dict.get("currency", "INR"),
        total=doc_dict.get("total"),
        summary=doc_dict.get("summary", ""),
        needs_review=needs_review,
        review_reason=review_reason,
        raw_text=raw_text,
        line_items=doc_dict.get("line_items", [])
    )

    # 5. Dispatch alerts to DB and Slack/Discord webhook
    rules_engine.dispatch_notifications(alerts, doc_id)

    return {
        "doc_id": doc_id,
        "doc": doc_dict,
        "alerts": alerts,
        "needs_review": needs_review,
        "review_reason": review_reason,
        "raw_text": raw_text
    }

def seed_sample_documents(api_key: Optional[str] = None):
    """
    Ingests all files in the sample_docs directory.
    """
    database.init_db()
    results = []
    if SAMPLE_DOCS_DIR.exists():
        for file in sorted(SAMPLE_DOCS_DIR.glob("*.*")):
            if file.is_file():
                res = process_document(file, api_key=api_key)
                results.append(res)
    return results
