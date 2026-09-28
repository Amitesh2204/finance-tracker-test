"""Legacy investment route placeholder.

The active application uses FastAPI routes in backend/main.py and the browser
currently performs investment document operations directly through PouchDB.
This legacy Flask blueprint was not registered by the FastAPI application and
contained imports for removed helpers. It is intentionally kept as a valid,
non-mounted module so it cannot break backend startup while preserving the
original project file for later migration.
"""

ROUTE_STATUS = "legacy-not-mounted"
