# Finance Tracker Test Environment

This repository is a security/modernization test copy of the personal finance tracker.

## Test environment
- GitHub Pages: https://amitesh2204.github.io/finance-tracker-test/
- CouchDB database: `finance-test`
- Browser-local PouchDB database: `finance-test`
- PostgreSQL target: `finance_test`

## Existing sync path is preserved
`Chrome PouchDB -> Cloudflare temporary URL -> CouchDB finance-test -> PostgreSQL finance_test`

The browser still uses native PouchDB replication. The change is that the CouchDB password is no longer committed to `frontend/config.js`.

## First-time setup
1. Copy `.env.example` to `.env` for the local FastAPI/PostgreSQL sync service.
2. Create/use a dedicated CouchDB test user with access only to `finance-test`.
3. Start the test Cloudflare tunnel.
4. Put only the current tunnel hostname in `frontend/config.js` as `couchHost`.
5. Push this folder to the `finance-tracker-test` repository.
6. Open the GitHub Pages URL in Chrome.
7. Click **Configure test CouchDB sync** and enter the dedicated test CouchDB username/password.
8. Add sample expenses/savings/investments while online and offline.
9. Run `python backend/data_sync/couch-postgreSQL-data-sync.py` after CouchDB contains test records.

## Important
- Never use the production CouchDB database or production credentials here.
- Never commit `.env`.
- The test application intentionally keeps the user database local; only `finance-test` is replicated.
- Existing finance document fields and PouchDB revision behavior are preserved.

## Regression checklist
- Add/edit/delete expense.
- Add savings, budget and investment data.
- Turn Chrome DevTools Network to Offline and add records.
- Re-enable Network and verify replication to CouchDB.
- Verify CouchDB -> PostgreSQL sync.
- Restart the Cloudflare tunnel and update only `couchHost`.
- Confirm old records remain readable.
