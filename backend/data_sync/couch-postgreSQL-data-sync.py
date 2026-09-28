"""One-way CouchDB -> PostgreSQL test synchronizer.

All connection details come from .env. No credentials belong in source control.
"""
import os
from pathlib import Path
import requests
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / '.env')

COUCHDB_URL = os.getenv('COUCHDB_URL', '').rstrip('/')
COUCHDB_USER = os.getenv('COUCHDB_USER', '')
COUCHDB_PASS = os.getenv('COUCHDB_PASS', '')
COUCHDB_DB = os.getenv('COUCHDB_DB', 'finance-test')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'finance_test')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', '127.0.0.1')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

if not COUCHDB_URL:
    raise SystemExit('COUCHDB_URL is required in .env')

url = f'{COUCHDB_URL}/{COUCHDB_DB}/_all_docs'
response = requests.get(url, params={'include_docs': 'true'}, auth=(COUCHDB_USER, COUCHDB_PASS), timeout=30)
response.raise_for_status()
data = response.json()

conn = psycopg2.connect(dbname=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PASSWORD, host=POSTGRES_HOST, port=POSTGRES_PORT)
cur = conn.cursor()

for row in data.get('rows', []):
    doc = row.get('doc') or {}
    if doc.get('_deleted'):
        continue
    cur.execute("""
        INSERT INTO transactions (id, amount, currency, date, notes, type, raw_doc)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
          amount = EXCLUDED.amount,
          currency = EXCLUDED.currency,
          date = EXCLUDED.date,
          notes = EXCLUDED.notes,
          type = EXCLUDED.type,
          raw_doc = EXCLUDED.raw_doc;
    """, (str(doc.get('_id')), doc.get('amount'), doc.get('currency'), doc.get('date'), doc.get('notes'), doc.get('type'), Json(doc)))

conn.commit()
cur.close()
conn.close()
print(f'Synced {len(data.get("rows", []))} CouchDB rows from {COUCHDB_DB} to PostgreSQL database {POSTGRES_DB}.')
