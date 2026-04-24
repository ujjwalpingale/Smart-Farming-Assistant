/**
 * api.js — centralised fetch wrapper that handles CSRF tokens automatically.
 * Django sends a csrftoken cookie on first load; we read it and attach it
 * as a header on every mutating request (POST, PUT, PATCH, DELETE).
 */

function getCsrfToken() {
  const name = 'csrftoken';
  for (const cookie of document.cookie.split(';')) {
    const [k, v] = cookie.trim().split('=');
    if (k === name) return decodeURIComponent(v);
  }
  return null;
}

async function request(url, options = {}) {
  const method = (options.method || 'GET').toUpperCase();
  const isFormData = options.body instanceof FormData;

  const headers = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...options.headers,
  };

  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
    const csrf = getCsrfToken();
    if (csrf) headers['X-CSRFToken'] = csrf;
  }

  const res = await fetch(url, {
    ...options,
    method,
    headers,
    credentials: 'include',  // send session cookies
  });

  return res;
}

// ── Auth ──────────────────────────────────────────────────────────────────

/** POST credentials as form-data to Django's login view */
export async function loginUser(username, password) {
  const form = new FormData();
  form.append('username', username);
  form.append('password', password);

  const res = await request('/accounts/login/', {
    method: 'POST',
    body: form,
    headers: {},
    redirect: 'manual',   // we handle redirect ourselves
  });
  return res;
}

/** POST to Django logout then signal success */
export async function logoutUser() {
  const form = new FormData();
  const res = await request('/logout/', { method: 'POST', body: form, headers: {} });
  return res;
}

/** POST registration fields */
export async function registerUser(username, email, password, passwordConfirm) {
  const form = new FormData();
  form.append('username', username);
  form.append('email', email);
  form.append('password', password);
  form.append('password_confirm', passwordConfirm);

  const res = await request('/register/', { method: 'POST', body: form, headers: {} });
  return res;
}

// ── ML Predictions ────────────────────────────────────────────────────────

export async function predictCrop(fields) {
  const form = new FormData();
  Object.entries(fields).forEach(([k, v]) => form.append(k, v));
  return request('/crop/', { method: 'POST', body: form, headers: {} });
}

export async function predictFertilizer(fields) {
  const form = new FormData();
  Object.entries(fields).forEach(([k, v]) => form.append(k, v));
  return request('/fertilizer/', { method: 'POST', body: form, headers: {} });
}

export async function predictDisease(fields, imageFile) {
  const form = new FormData();
  Object.entries(fields).forEach(([k, v]) => form.append(k, v));
  if (imageFile) form.append('image', imageFile);
  return request('/disease/', { method: 'POST', body: form, headers: {} });
}

