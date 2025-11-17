// WebAuthn utilities
function b64ToBuf(b64) {
  const bin = atob(b64.replace(/-/g, '+').replace(/_/g, '/'));
  const buf = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
  return buf.buffer;
}
function bufToB64(buf) {
  const bytes = new Uint8Array(buf);
  let bin = '';
  for (let i = 0; i < bytes.byteLength; i++) bin += String.fromCharCode(bytes[i]);
  return btoa(bin);
}
async function createPasskeyOptions(adminId, baseUrl) {
  const resp = await fetch(`${baseUrl}/webauthn/register/options`, {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ adminId })
  });
  const options = await resp.json();
  options.challenge = b64ToBuf(options.challenge);
  options.user.id = b64ToBuf(options.user.id);
  options.authenticatorSelection = { authenticatorAttachment: 'platform' };
  options.userVerification = 'required';
  return options;
}
async function createPasskey(options, adminId, baseUrl) {
  const credential = await navigator.credentials.create({ publicKey: options });
  const attestation = {
    id: credential.id,
    rawId: bufToB64(credential.rawId),
    type: credential.type,
    response: {
      clientDataJSON: bufToB64(credential.response.clientDataJSON),
      attestationObject: bufToB64(credential.response.attestationObject)
    }
  };
  await fetch(`${baseUrl}/webauthn/register/verify`, {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ adminId, attestation })
  });
}
async function getAssertionOptions(adminId, baseUrl) {
  const resp = await fetch(`${baseUrl}/webauthn/login/options`, {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ adminId })
  });
  const options = await resp.json();
  options.challenge = b64ToBuf(options.challenge);
  if (options.allowCredentials) {
    options.allowCredentials = options.allowCredentials.map(c => ({ ...c, id: b64ToBuf(c.id) }));
  }
  options.userVerification = 'required';
  return options;
}
async function getAssertion(options) {
  const assertion = await navigator.credentials.get({ publicKey: options });
  return {
    id: assertion.id,
    rawId: bufToB64(assertion.rawId),
    type: assertion.type,
    response: {
      clientDataJSON: bufToB64(assertion.response.clientDataJSON),
      authenticatorData: bufToB64(assertion.response.authenticatorData),
      signature: bufToB64(assertion.response.signature),
      userHandle: assertion.response.userHandle ? bufToB64(assertion.response.userHandle) : null
    }
  };
}
async function verifyAssertion(adminId, baseUrl, assertionPayload) {
  const verify = await fetch(`${baseUrl}/webauthn/login/verify`, {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ adminId, assertion: assertionPayload })
  });
  return verify.ok;
}
window.WebAuthn = { createPasskeyOptions, createPasskey, getAssertionOptions, getAssertion, verifyAssertion };
