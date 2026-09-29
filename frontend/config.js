// Test environment configuration for finance-tracker-test.
// IMPORTANT: never commit CouchDB passwords here.
(function () {
  'use strict';
  const hostname = window.location.hostname || '';
  const isLocalDev = ['localhost', '127.0.0.1', '::1'].includes(hostname);

  window.__API_BASE__ = window.__API_BASE__ || (isLocalDev ? 'http://127.0.0.1:8001' : '');

  window.__CONFIG__ = {
    environment: 'test',
    githubPagesUrl: 'https://amitesh2204.github.io/finance-tracker-test/',
    couchHost: 'commentary-usa-letting-featuring.trycloudflare.com', // Set the current Cloudflare tunnel host here, without https://
    couchDbName: 'finance-test',
    usersDbName: '', // Intentionally local-only; finance-test is the only test DB created so far.
    apiBase: window.__API_BASE__,
    requireLogin: true,
    allowRemoteUserSync: false
  };

  // Credentials are supplied at runtime through the test sync dialog and kept
  // only in sessionStorage. They are never stored in this file.
  window.__USERS_COUCH__ = '';
})();
