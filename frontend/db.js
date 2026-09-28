// db.js - local-first PouchDB and authenticated test CouchDB sync.
// The finance document flow is intentionally preserved: PouchDB <-> CouchDB.
(function () {
  'use strict';
  const cfg = () => window.__CONFIG__ || {};
  const SYNC_SESSION_KEY = 'finance-test:couch-sync-credentials';
  const db = new PouchDB('finance-test');
  window.financeDB = db;
  let syncHandle = null;

  function setSyncStatus(state, detail) {
    window.__FINANCE_SYNC_STATUS__ = { state, detail: detail || '', at: new Date().toISOString() };
    window.dispatchEvent(new CustomEvent('finance-sync-status', { detail: window.__FINANCE_SYNC_STATUS__ }));
  }

  function getStoredCredentials() {
    try {
      const raw = sessionStorage.getItem(SYNC_SESSION_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch { return null; }
  }

  function saveCredentials(username, password) {
    if (!username || !password) throw new Error('CouchDB username and password are required.');
    sessionStorage.setItem(SYNC_SESSION_KEY, JSON.stringify({ username, password }));
  }

  function clearCredentials() {
    sessionStorage.removeItem(SYNC_SESSION_KEY);
    if (syncHandle) { try { syncHandle.cancel(); } catch {} syncHandle = null; }
    setSyncStatus('signed-out', 'CouchDB credentials cleared');
  }

  function buildRemoteUrl() {
    const host = String(cfg().couchHost || '').trim().replace(/^https?:\/\//i, '').replace(/\/$/, '');
    const dbName = String(cfg().couchDbName || 'finance-test').trim();
    if (!host) return null;
    if (!/^[A-Za-z0-9.-]+(?::\d+)?$/.test(host)) throw new Error('Invalid Cloudflare/CouchDB host in config.js');
    if (!/^[A-Za-z0-9_$()+\-\/]+$/.test(dbName)) throw new Error('Invalid CouchDB database name');
    return `https://${host}/${dbName}`;
  }

  function startRemoteSync(credentials) {
    const remoteUrl = buildRemoteUrl();
    if (!remoteUrl) {
      setSyncStatus('not-configured', 'Set couchHost in frontend/config.js');
      return false;
    }
    if (!credentials?.username || !credentials?.password) {
      setSyncStatus('auth-required', 'Enter the dedicated test CouchDB credentials');
      return false;
    }
    if (syncHandle) { try { syncHandle.cancel(); } catch {} }

    const remoteDB = new PouchDB(remoteUrl, {
      skip_setup: true,
      auth: { username: credentials.username, password: credentials.password }
    });

    syncHandle = db.sync(remoteDB, { live: true, retry: true })
      .on('change', info => {
        setSyncStatus('synced', `Change replicated (${info.direction || 'sync'})`);
        window.dispatchEvent(new CustomEvent('finance-sync-change', { detail: info }));
      })
      .on('paused', info => setSyncStatus('synced', info ? 'Waiting for changes' : 'Paused'))
      .on('active', () => setSyncStatus('syncing', 'Replication active'))
      .on('denied', err => setSyncStatus('error', 'CouchDB denied the replication request'))
      .on('error', err => setSyncStatus('error', 'Replication error; check Cloudflare/CouchDB availability'));

    setSyncStatus('syncing', `Connected to ${cfg().couchDbName}`);
    return true;
  }

  window.financeSync = {
    configure(username, password) {
      saveCredentials(username, password);
      return startRemoteSync({ username, password });
    },
    start() { return startRemoteSync(getStoredCredentials()); },
    clear: clearCredentials,
    status() { return window.__FINANCE_SYNC_STATUS__ || { state: 'not-started' }; },
    isConfigured() { return !!buildRemoteUrl(); }
  };

  setSyncStatus('local-only', 'Offline/local PouchDB mode until test CouchDB is configured');
  try { startRemoteSync(getStoredCredentials()); } catch (err) { setSyncStatus('error', err.message); }

  window.addEntry = async function(entry) { return db.post(entry); };
  window.fetchEntries = async function() {
    const result = await db.allDocs({ include_docs: true });
    return result.rows.map(r => r.doc).filter(Boolean);
  };
  window.deleteEntry = async function(docOrId) {
    const id = typeof docOrId === 'string' ? docOrId : docOrId && docOrId._id;
    if (!id) throw new Error('deleteEntry: no _id provided');
    return db.remove(await db.get(id));
  };
  window.updateEntry = async function(docOrId, patchedData) {
    const id = typeof docOrId === 'string' ? docOrId : docOrId && docOrId._id;
    if (!id) throw new Error('updateEntry: no _id provided');
    const latest = await db.get(id);
    return db.put({ ...latest, ...patchedData, _id: id, _rev: latest._rev });
  };
  window._localFinanceDB = db;
})();
