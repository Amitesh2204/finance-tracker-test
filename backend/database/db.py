
import os
from pathlib import Path
from couchdb import Server
from couchdb.http import ResourceNotFound, Unauthorized
from dotenv import load_dotenv
from urllib.parse import quote_plus

root = Path(__file__).resolve().parent.parent.parent
load_dotenv(root / ".env")

COUCHDB_URL = os.getenv("COUCHDB_URL", "").strip()
COUCHDB_USER = os.getenv("COUCHDB_USER", "").strip()
COUCHDB_PASS = os.getenv("COUCHDB_PASS", "").strip()
COUCHDB_HOST = os.getenv("COUCHDB_HOST", "127.0.0.1").strip()
COUCHDB_PORT = os.getenv("COUCHDB_PORT", "5984").strip()
COUCHDB_DB = os.getenv("COUCHDB_DB", "finance-test").strip()


def get_server():
    if COUCHDB_URL:
        server = Server(COUCHDB_URL)
        if COUCHDB_USER and COUCHDB_PASS:
            server.resource.credentials = (COUCHDB_USER, COUCHDB_PASS)
        return server

    if COUCHDB_USER and COUCHDB_PASS:
        auth = f"{quote_plus(COUCHDB_USER)}:{quote_plus(COUCHDB_PASS)}@"
    else:
        auth = ""

    url = f"http://{auth}{COUCHDB_HOST}:{COUCHDB_PORT}/"
    return Server(url)


def get_db(dbname=None):
    dbname = (dbname or COUCHDB_DB).strip()
    if not dbname:
        raise RuntimeError("COUCHDB_DB must be configured")

    server = get_server()
    try:
        return server[dbname]
    except ResourceNotFound:
        try:
            return server.create(dbname)
        except Unauthorized as err:
            raise RuntimeError(
                "CouchDB requires authentication to create the database. "
                "Check COUCHDB_USER and COUCHDB_PASS."
            ) from err
    except Unauthorized as err:
        raise RuntimeError(
            "CouchDB requires authentication. "
            "Check COUCHDB_USER and COUCHDB_PASS."
        ) from err
