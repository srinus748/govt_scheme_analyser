# utils/db_cache.py

import sqlite3
import hashlib
import os
import datetime
from utils.logger import logger

DB_NAME = "cache.db"

def _get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    return conn

def init_db():
    """Initializes the database and creates the cache tables if they don't exist."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    # Original scheme_cache table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scheme_cache (
            source_key TEXT PRIMARY KEY,
            source_type TEXT NOT NULL,
            summary_en TEXT,
            summary_te TEXT,
            pdf_path TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # NEW: URL cache table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS url_cache (
            url TEXT PRIMARY KEY,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized with scheme_cache and url_cache tables.")

def compute_source_key(source_type: str, content: str) -> str:
    """Computes a SHA256 hash for the given content to be used as a cache key."""
    return hashlib.sha256(f"{source_type}:{content}".encode()).hexdigest()

def get_cached_summary(source_key: str) -> dict | None:
    """Retrieves a cached summary by its source key."""
    conn = _get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scheme_cache WHERE source_key = ?", (source_key,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None

def save_to_cache(source_key: str, source_type: str, summary_en: str, summary_te: str, pdf_path: str):
    """Saves a new summary to the cache."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO scheme_cache (source_key, source_type, summary_en, summary_te, pdf_path)
        VALUES (?, ?, ?, ?, ?)
    ''', (source_key, source_type, summary_en, summary_te, pdf_path))
    conn.commit()
    conn.close()
    logger.info(f"Saved new summary to cache with key: {source_key[:16]}...")

# --- NEW FUNCTIONS FOR URL CACHING ---

def save_url_cache(url: str, content: str):
    """Save extracted content from a URL to cache."""
    try:
        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO url_cache (url, content, timestamp)
            VALUES (?, ?, ?)
        ''', (url, content, datetime.datetime.now()))
        conn.commit()
        conn.close()
        logger.info(f"Saved URL content to cache: {url}")
    except Exception as e:
        logger.error(f"Error saving URL cache: {e}")

def get_url_cache(url: str) -> str | None:
    """Get cached content for a URL."""
    try:
        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM url_cache WHERE url = ?", (url,))
        result = cursor.fetchone()
        conn.close()
        if result:
            logger.info(f"Found cached content for URL: {url}")
            return result[0]
        return None
    except Exception as e:
        logger.error(f"Error retrieving URL cache: {e}")
        return None

def clear_old_cache(days_old: int = 30):
    """Deletes cache entries older than the specified number of days."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_old)
    
    # Clear old scheme cache
    cursor.execute("DELETE FROM scheme_cache WHERE timestamp < ?", (cutoff_date,))
    
    # Clear old URL cache
    cursor.execute("DELETE FROM url_cache WHERE timestamp < ?", (cutoff_date,))
    
    conn.commit()
    conn.close()
    logger.info(f"Cleared cache entries older than {days_old} days.")