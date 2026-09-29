import os
from pathlib import Path
from urllib.parse import quote_plus

from couchdb import Server
from couchdb.http import ResourceNotFound, Unauthorized
from dotenv import load_dotenv


# Project root
root = Path(__file__).resolve().parents[2]
load_dotenv(root / ".env")

COUCHDB_URL = os.getenv("COUCHDB_URL", "").strip()
COUCHDB_USER = os.getenv("COUCHDB_USER", "").strip()
COUCHDB_PASS = os.getenv("COUCHDB_PASS", "").strip()
COUCHDB_HOST = os.getenv("COUCHDB_HOST", "127.0.0.1").strip()
COUCHDB_PORT = os.getenv("COUCHDB_PORT", "5984").strip()
COUCHDB_DB = os.getenv("COUCHDB_DB", "finance-test").strip() or "finance-test"


def get_server():
    """
    Create an authenticated CouchDB server connection.

    Authentication is configured explicitly on the CouchDB
    Resource object so it works whether COUCHDB_URL is provided
    directly or constructed from host/port.
    """

    if COUCHDB_URL:
        server = Server(COUCHDB_URL)
    else:
        auth = (
            f"{quote_plus(COUCHDB_USER)}:{quote_plus(COUCHDB_PASS)}@"
            if COUCHDB_USER and COUCHDB_PASS
            else ""
        )

        server = Server(
            f"http://{auth}{COUCHDB_HOST}:{COUCHDB_PORT}/"
        )

    # Explicitly configure authentication.
    if COUCHDB_USER and COUCHDB_PASS:
        server.resource.credentials = (
            COUCHDB_USER,
            COUCHDB_PASS,
        )

    return server


def get_db(dbname=None):
    name = dbname or COUCHDB_DB
    server = get_server()

    try:
        return server[name]

    except ResourceNotFound:
        try:
            return server.create(name)

        except Unauthorized as err:
            raise RuntimeError(
                "CouchDB authentication does not allow database "
                "creation. Create the test database first or grant "
                "the required test-user permission."
            ) from err

    except Unauthorized as err:
        raise RuntimeError(
            "CouchDB authentication failed. "
            "Check the test environment credentials."
        ) from err