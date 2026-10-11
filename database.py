import sqlite3
from typing import List, Dict, Any, Optional
import pandas as pd
from config import DB_PATH

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        doc_type TEXT DEFAULT 'other',
        vendor TEXT,
        doc_number TEXT,
        date TEXT,
        currency TEXT DEFAULT 'INR',
        total REAL,
        summary TEXT,
        needs_review INTEGER DEFAULT 0,
        review_reason TEXT,
        raw_text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS line_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_id INTEGER NOT NULL,
        description TEXT,
        qty REAL,
        unit_price REAL,
        amount REAL NOT NULL,
        FOREIGN KEY(doc_id) REFERENCES documents(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_id INTEGER,
        rule_name TEXT NOT NULL,
        severity TEXT DEFAULT 'WARNING',
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()

def save_document(
    filename: str,
    doc_type: str,
    vendor: Optional[str],
    doc_number: Optional[str],
    date: Optional[str],
    currency: Optional[str],
    total: Optional[float],
    summary: str,
    needs_review: bool,
    review_reason: str,
    raw_text: str,
    line_items: List[Dict[str, Any]]
) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO documents (
        filename, doc_type, vendor, doc_number, date, currency, total, summary, needs_review, review_reason, raw_text
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        filename,
        doc_type,
        vendor,
        doc_number,
        date,
        currency or "INR",
        total,
        summary,
        1 if needs_review else 0,
        review_reason,
        raw_text
    ))
    doc_id = cursor.lastrowid

    for item in line_items:
        cursor.execute("""
        INSERT INTO line_items (doc_id, description, qty, unit_price, amount)
        VALUES (?, ?, ?, ?, ?)
        """, (
            doc_id,
            item.get("description", "Item"),
            item.get("qty"),
            item.get("unit_price"),
            item.get("amount", 0.0)
        ))

    conn.commit()
    conn.close()
    return doc_id

def log_alert(doc_id: Optional[int], rule_name: str, severity: str, message: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO alerts_log (doc_id, rule_name, severity, message)
    VALUES (?, ?, ?, ?)
    """, (doc_id, rule_name, severity, message))
    conn.commit()
    conn.close()

def get_all_documents() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("""
    SELECT 
        d.id, d.filename, d.doc_type, d.vendor, d.doc_number, d.date, 
        d.currency, d.total, d.summary, d.needs_review, d.review_reason, d.created_at,
        COUNT(l.id) as item_count
    FROM documents d
    LEFT JOIN line_items l ON d.id = l.doc_id
    GROUP BY d.id
    ORDER BY d.id DESC
    """, conn)
    conn.close()
    return df

def get_document_details(doc_id: int) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    doc_row = cursor.fetchone()
    
    cursor.execute("SELECT * FROM line_items WHERE doc_id = ?", (doc_id,))
    items = cursor.fetchall()
    
    cursor.execute("SELECT * FROM alerts_log WHERE doc_id = ? ORDER BY id DESC", (doc_id,))
    alerts = cursor.fetchall()
    
    conn.close()
    return {
        "doc": dict(doc_row) if doc_row else None,
        "line_items": [dict(i) for i in items],
        "alerts": [dict(a) for a in alerts]
    }

def get_all_alerts(limit: int = 50) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query(f"""
    SELECT a.id, a.doc_id, d.filename, d.vendor, a.rule_name, a.severity, a.message, a.created_at
    FROM alerts_log a
    LEFT JOIN documents d ON a.doc_id = d.id
    ORDER BY a.id DESC
    LIMIT {limit}
    """, conn)
    conn.close()
    return df

def execute_raw_select(query: str) -> pd.DataFrame:
    clean_query = query.strip()
    if not clean_query.upper().startswith("SELECT"):
        raise ValueError("Security check: Only SELECT queries are permitted.")
    conn = get_connection()
    df = pd.read_sql_query(clean_query, conn)
    conn.close()
    return df

def check_duplicate(vendor: Optional[str], doc_number: Optional[str], total: Optional[float]) -> bool:
    if not vendor or not doc_number:
        return False
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id FROM documents 
    WHERE LOWER(vendor) = LOWER(?) AND LOWER(doc_number) = LOWER(?) AND ABS(total - ?) < 0.01
    LIMIT 1
    """, (vendor, doc_number, total or 0.0))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists
