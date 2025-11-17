// Admin actions wiring for Streamlit page.
// Uses WebAuthn utilities (from webauthn.js) and updates the DOM status element.

(function () {
  const statusEl = document.getElementById('status');
  const { ADMIN_ID, BACKEND_URL } = window.__CONFIG__;

  function setStatus(msg) {
    if (statusEl) statusEl.textContent = msg;
  }

  async function register() {
    try {
      setStatus("Préparation de l'enregistrement…");
      const options = await WebAuthn.createPasskeyOptions(ADMIN_ID, BACKEND_URL);
      await WebAuthn.createPasskey(options, ADMIN_ID, BACKEND_URL);
      setStatus("Passkey enregistrée ✅");
    } catch (e) {
      console.error(e);
      setStatus("Erreur enregistrement: " + (e?.message || e));
    }
  }

  async function login() {
    try {
      setStatus("Demande d'authentification…");
      const options = await WebAuthn.getAssertionOptions(ADMIN_ID, BACKEND_URL);
      const assertion = await WebAuthn.getAssertion(options);
      const ok = await WebAuthn.verifyAssertion(ADMIN_ID, BACKEND_URL, assertion);
      setStatus(ok ? "Connexion admin réussie ✅" : "Échec de la connexion ❌");
    } catch (e) {
      console.error(e);
      setStatus("Erreur connexion: " + (e?.message || e));
    }
  }

  // Wire up buttons
  document.getElementById('btn-register')?.addEventListener('click', register);
  document.getElementById('btn-login')?.addEventListener('click', login);

  // Expose for debugging if needed
  window.AdminActions = { register, login };
})();
