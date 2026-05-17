/* ── NabhaHealth Frontend App ────────────────────────────── */

const API = '';   // same origin — Flask serves both

// ── State ────────────────────────────────────────────────────
let token = localStorage.getItem('nh_token');
let currentUser = JSON.parse(localStorage.getItem('nh_user') || 'null');
let bookDoctorId = null;
let symptoms = [];
let activeMedCat = '';
let medSearchTimer = null;

// ── Init ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  updateNavAuth();
  showPage('home');
  loadDoctors();
  loadSpecialisations();
  loadMedicines();
  loadPharmacies();
});

// ── Page Router ───────────────────────────────────────────────
function showPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const page = document.getElementById('page-' + name);
  if (page) page.classList.add('active');

  if (name === 'appointments') loadAppointments();
  if (name === 'records') {
    if (!token) { showPage('login'); return; }
    loadRecords();
  }
  if (name === 'doctors') loadDoctors();
  if (name === 'medicines') loadMedicines();
  if (name === 'pharmacy') loadPharmacies();
}

// ── API Helper ────────────────────────────────────────────────
async function api(path, opts = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = 'Bearer ' + token;
  const res = await fetch(API + path, { headers, ...opts });
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, status: res.status, data };
}

// ── Auth ──────────────────────────────────────────────────────
async function login() {
  const phone = document.getElementById('loginPhone').value.trim();
  const pass  = document.getElementById('loginPass').value;
  const errEl = document.getElementById('loginError');
  errEl.style.display = 'none';

  if (!phone || !pass) { showErr(errEl, 'Please enter phone and password.'); return; }

  const { ok, data } = await api('/api/auth/login', {
    method: 'POST', body: JSON.stringify({ phone, password: pass })
  });
  if (!ok) { showErr(errEl, data.error || 'Login failed.'); return; }

  token = data.token;
  currentUser = data.user;
  localStorage.setItem('nh_token', token);
  localStorage.setItem('nh_user', JSON.stringify(currentUser));
  updateNavAuth();
  toast('Welcome back, ' + currentUser.name + '!', 'success');
  showPage('home');
}

async function register() {
  const errEl = document.getElementById('regError');
  errEl.style.display = 'none';
  const payload = {
    name:     document.getElementById('regName').value.trim(),
    phone:    document.getElementById('regPhone').value.trim(),
    email:    document.getElementById('regEmail').value.trim() || undefined,
    village:  document.getElementById('regVillage').value.trim(),
    language: document.getElementById('regLang').value,
    password: document.getElementById('regPass').value,
    role: 'patient',
  };
  if (!payload.name || !payload.phone || !payload.password) {
    showErr(errEl, 'Name, phone and password are required.'); return;
  }
  const { ok, data } = await api('/api/auth/register', {
    method: 'POST', body: JSON.stringify(payload)
  });
  if (!ok) { showErr(errEl, data.error || 'Registration failed.'); return; }

  token = data.token;
  currentUser = data.user;
  localStorage.setItem('nh_token', token);
  localStorage.setItem('nh_user', JSON.stringify(currentUser));
  updateNavAuth();
  toast('Account created! Welcome, ' + currentUser.name, 'success');
  showPage('home');
}

function logout() {
  token = null; currentUser = null;
  localStorage.removeItem('nh_token');
  localStorage.removeItem('nh_user');
  updateNavAuth();
  toast('Logged out.', '');
  showPage('home');
}

function updateNavAuth() {
  const authDiv = document.getElementById('navAuth');
  const userDiv = document.getElementById('navUser');
  const recordsNav = document.getElementById('recordsNav');
  if (currentUser) {
    authDiv.style.display = 'none';
    userDiv.style.display = 'flex';
    document.getElementById('navUserName').textContent = '👤 ' + currentUser.name;
    if (recordsNav) recordsNav.style.display = '';
  } else {
    authDiv.style.display = 'flex';
    userDiv.style.display = 'none';
    if (recordsNav) recordsNav.style.display = 'none';
  }
}

// ── Doctors ───────────────────────────────────────────────────
async function loadDoctors() {
  const spec = document.getElementById('specFilter')?.value || '';
  const avail = document.getElementById('availableOnly')?.checked ? 'true' : 'false';
  let url = `/api/doctors?available=${avail}`;
  if (spec) url += `&specialisation=${encodeURIComponent(spec)}`;

  const el = document.getElementById('doctorsList');
  el.innerHTML = '<div class="loader"><span class="spinner"></span>Loading doctors...</div>';

  const { ok, data } = await api(url);
  if (!ok) { el.innerHTML = '<p class="muted">Failed to load doctors.</p>'; return; }

  if (!data.length) {
    el.innerHTML = '<div class="empty-state"><div class="empty-icon">👨‍⚕️</div><p>No doctors found.</p></div>';
    return;
  }

  el.innerHTML = data.map(d => `
    <div class="card">
      <div class="card-header">
        <div>
          <div class="card-title">Dr. ${d.name.replace('Dr. ', '')}</div>
          <div class="card-subtitle">${d.specialisation}</div>
        </div>
        <span class="badge ${d.is_available ? 'badge-green' : 'badge-red'}">
          ${d.is_available ? '● Available' : '○ Busy'}
        </span>
      </div>
      <div class="card-body">
        <p>🎓 ${d.qualification || 'MBBS'}</p>
        <p>🗣️ ${Array.isArray(d.languages) ? d.languages.join(', ') : d.languages}</p>
        <p>📅 ${Array.isArray(d.available_days) ? d.available_days.join(', ') : d.available_days}</p>
        <p>⏱️ ${d.slot_duration} min slots · Max ${d.max_daily_appts}/day</p>
      </div>
      <div class="card-footer">
        ${d.is_available
          ? `<button class="btn btn-primary btn-sm" onclick="openBookModal(${d.id}, '${escHtml(d.name)}')">Book Appointment</button>`
          : `<button class="btn btn-outline btn-sm" disabled>Not Available</button>`}
      </div>
    </div>
  `).join('');
}

async function loadSpecialisations() {
  const { ok, data } = await api('/api/doctors/specialisations');
  if (!ok) return;
  const sel = document.getElementById('specFilter');
  if (!sel) return;
  data.forEach(s => {
    const opt = document.createElement('option');
    opt.value = s; opt.textContent = s;
    sel.appendChild(opt);
  });
}

// ── Book Appointment ──────────────────────────────────────────
function openBookModal(doctorId, doctorName) {
  if (!token) { toast('Please login to book an appointment.', 'error'); showPage('login'); return; }
  bookDoctorId = doctorId;
  document.getElementById('bookModalTitle').textContent = 'Book with ' + doctorName;
  document.getElementById('bookDate').value = '';
  document.getElementById('bookNotes').value = '';
  document.getElementById('bookSelectedSlot').value = '';
  document.getElementById('slotsGrid').innerHTML = '<p class="muted">Select a date above.</p>';
  document.getElementById('bookError').style.display = 'none';
  // Set min date to today
  const today = new Date().toISOString().split('T')[0];
  document.getElementById('bookDate').min = today;
  document.getElementById('bookModal').style.display = 'flex';
}

function closeBookModal() {
  document.getElementById('bookModal').style.display = 'none';
}

async function loadSlots() {
  const date = document.getElementById('bookDate').value;
  if (!date || !bookDoctorId) return;
  const grid = document.getElementById('slotsGrid');
  grid.innerHTML = '<div class="loader"><span class="spinner"></span>Loading slots...</div>';

  const { ok, data } = await api(`/api/appointments/slots?doctor_id=${bookDoctorId}&date=${date}`);
  if (!ok) { grid.innerHTML = '<p class="muted">Could not load slots.</p>'; return; }

  if (!data.slots || !data.slots.length) {
    grid.innerHTML = '<p class="muted">No slots available on this date.</p>'; return;
  }

  grid.innerHTML = data.slots.map(s => `
    <button class="slot-btn ${s.available ? 'available' : 'booked'}"
      ${!s.available ? 'disabled' : ''}
      onclick="selectSlot('${s.time}', this)">${s.time}</button>
  `).join('');
}

function selectSlot(time, btn) {
  document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  const date = document.getElementById('bookDate').value;
  document.getElementById('bookSelectedSlot').value = `${date}T${time}:00`;
}

async function confirmBook() {
  const slot = document.getElementById('bookSelectedSlot').value;
  const errEl = document.getElementById('bookError');
  errEl.style.display = 'none';

  if (!slot) { showErr(errEl, 'Please select a time slot.'); return; }

  const payload = {
    doctor_id: bookDoctorId,
    scheduled_at: slot,
    mode: document.getElementById('bookMode').value,
    notes: document.getElementById('bookNotes').value,
  };

  const { ok, data } = await api('/api/appointments', {
    method: 'POST', body: JSON.stringify(payload)
  });
  if (!ok) { showErr(errEl, data.error || 'Booking failed.'); return; }

  closeBookModal();
  toast('Appointment booked successfully!', 'success');
  showPage('appointments');
}

// ── Appointments ──────────────────────────────────────────────
async function loadAppointments() {
  const authMsg = document.getElementById('apptAuthMsg');
  const list    = document.getElementById('appointmentsList');

  if (!token) {
    authMsg.style.display = 'block';
    list.innerHTML = '';
    return;
  }
  authMsg.style.display = 'none';

  const status = document.getElementById('apptStatusFilter')?.value || '';
  let url = '/api/appointments';
  if (status) url += '?status=' + status;

  list.innerHTML = '<div class="loader"><span class="spinner"></span>Loading appointments...</div>';
  const { ok, data } = await api(url);
  if (!ok) { list.innerHTML = '<p class="muted">Failed to load appointments.</p>'; return; }

  if (!data.length) {
    list.innerHTML = '<div class="empty-state"><div class="empty-icon">📅</div><p>No appointments found.</p></div>';
    return;
  }

  list.innerHTML = data.map(a => {
    const dt = new Date(a.scheduled_at);
    const dateStr = dt.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
    const timeStr = dt.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
    return `
    <div class="appt-card ${a.status}">
      <div class="appt-info">
        <div class="appt-title">${a.doctor.name} — ${a.doctor.specialisation}</div>
        <div class="appt-meta">
          📅 ${dateStr} at ${timeStr} &nbsp;|&nbsp;
          ${a.mode === 'video' ? '📹 Video Call' : '🏥 In Person'} &nbsp;|&nbsp;
          Patient: ${a.patient.name}
        </div>
        ${a.notes ? `<div class="appt-meta" style="margin-top:0.25rem">📋 ${escHtml(a.notes)}</div>` : ''}
        ${a.prescription ? `<div class="appt-meta" style="margin-top:0.25rem">💊 Rx: ${escHtml(a.prescription)}</div>` : ''}
      </div>
      <div>
        <span class="badge ${statusBadge(a.status)}">${a.status}</span>
      </div>
      <div class="appt-actions">
        ${a.status === 'booked' ? `<button class="btn btn-danger btn-sm" onclick="cancelAppt(${a.id})">Cancel</button>` : ''}
      </div>
    </div>`;
  }).join('');
}

async function cancelAppt(id) {
  if (!confirm('Cancel this appointment?')) return;
  const { ok, data } = await api(`/api/appointments/${id}/cancel`, { method: 'PUT' });
  if (ok) { toast('Appointment cancelled.', ''); loadAppointments(); }
  else toast(data.error || 'Failed to cancel.', 'error');
}

function statusBadge(s) {
  return { booked: 'badge-blue', completed: 'badge-green', cancelled: 'badge-red', no_show: 'badge-gray' }[s] || 'badge-gray';
}

// ── Medicines ─────────────────────────────────────────────────
async function loadMedicines(cat) {
  activeMedCat = cat || '';
  const el = document.getElementById('medicinesList');
  el.innerHTML = '<div class="loader"><span class="spinner"></span>Loading medicines...</div>';

  let url = '/api/medicines';
  if (activeMedCat) url += '?category=' + encodeURIComponent(activeMedCat);

  const { ok, data } = await api(url);
  if (!ok) { el.innerHTML = '<p class="muted">Failed to load.</p>'; return; }

  // populate category tabs (once)
  const catTabsEl = document.getElementById('medCats');
  if (catTabsEl && !catTabsEl.dataset.loaded) {
    catTabsEl.dataset.loaded = '1';
    const cats = [...new Set(data.map(m => m.category).filter(Boolean))].sort();
    catTabsEl.innerHTML = `<span class="cat-tab active" onclick="switchCat('', this)">All</span>` +
      cats.map(c => `<span class="cat-tab" onclick="switchCat('${escHtml(c)}', this)">${c}</span>`).join('');
  }

  renderMedicinesTable(data, el);
}

function switchCat(cat, tabEl) {
  document.querySelectorAll('.cat-tab').forEach(t => t.classList.remove('active'));
  tabEl.classList.add('active');
  document.getElementById('medSearch').value = '';
  loadMedicines(cat);
}

function renderMedicinesTable(data, el) {
  if (!data.length) {
    el.innerHTML = '<div class="empty-state"><div class="empty-icon">💊</div><p>No medicines found.</p></div>'; return;
  }
  el.innerHTML = `
    <div class="table-wrap">
    <table>
      <thead><tr>
        <th>Medicine Name</th>
        <th>Generic / Salt</th>
        <th>Category</th>
        <th>Form</th>
        <th>Rx?</th>
        <th>Available At</th>
        <th>Total Stock</th>
      </tr></thead>
      <tbody>
      ${data.map(m => `
        <tr>
          <td><strong>${escHtml(m.name)}</strong></td>
          <td>${escHtml(m.generic || '—')}</td>
          <td><span class="badge badge-blue">${escHtml(m.category || '')}</span></td>
          <td>${m.form || '—'}</td>
          <td>${m.requires_rx ? '<span class="badge badge-orange">Rx</span>' : '<span class="badge badge-green">OTC</span>'}</td>
          <td>
            ${(m.available_at || []).length
              ? m.available_at.slice(0,3).map(p => `<div style="font-size:0.8rem">${escHtml(p.name||p.pharmacy||'')}</div>`).join('')
              : '<span class="badge badge-red">Out of stock</span>'}
          </td>
          <td>
            <span class="badge ${m.total_available > 0 ? 'badge-green' : 'badge-red'}">
              ${m.total_available !== undefined ? m.total_available : '—'}
            </span>
          </td>
        </tr>`).join('')}
      </tbody>
    </table>
    </div>`;
}

function searchMedicines() {
  clearTimeout(medSearchTimer);
  const q = document.getElementById('medSearch').value.trim();
  if (q.length < 2) {
    if (q.length === 0) loadMedicines(activeMedCat);
    return;
  }
  medSearchTimer = setTimeout(async () => {
    const el = document.getElementById('medicinesList');
    el.innerHTML = '<div class="loader"><span class="spinner"></span>Searching...</div>';
    const { ok, data } = await api('/api/medicines/search?q=' + encodeURIComponent(q));
    if (!ok) { el.innerHTML = '<p class="muted">Search failed.</p>'; return; }
    renderMedicinesTable(data, el);
  }, 350);
}

// ── Symptom Checker ───────────────────────────────────────────
function addSymptomOnEnter(e) {
  if (e.key === 'Enter') {
    const val = document.getElementById('symptomInput').value.trim();
    if (val) { addSymptom(val); document.getElementById('symptomInput').value = ''; }
  }
}

function addSymptom(s) {
  s = s.trim();
  if (!s || symptoms.includes(s)) return;
  symptoms.push(s);
  renderChips();
}

function removeSymptom(s) {
  symptoms = symptoms.filter(x => x !== s);
  renderChips();
}

function clearSymptoms() {
  symptoms = [];
  renderChips();
  document.getElementById('symptomResult').innerHTML = '';
}

function renderChips() {
  const el = document.getElementById('symptomChips');
  el.innerHTML = symptoms.map(s =>
    `<span class="chip">${escHtml(s)}<span class="chip-remove" onclick="removeSymptom('${escHtml(s)}')">&times;</span></span>`
  ).join('');
}

async function checkSymptoms() {
  if (!symptoms.length) { toast('Please add at least one symptom.', 'error'); return; }
  const resEl = document.getElementById('symptomResult');
  resEl.innerHTML = '<div class="loader"><span class="spinner"></span>Analysing symptoms...</div>';

  const { ok, data } = await api('/api/symptom-check', {
    method: 'POST', body: JSON.stringify({ symptoms })
  });

  if (!ok) { resEl.innerHTML = '<div class="alert alert-error">Analysis failed. Please try again.</div>'; return; }

  const urgency = (data.urgency || 'LOW').toUpperCase();
  const urgencyClass = { CRITICAL: 'result-critical', HIGH: 'result-high', MEDIUM: 'result-medium', LOW: 'result-low' }[urgency] || 'result-low';
  const urgencyBadge = { CRITICAL: 'badge-critical', HIGH: 'badge-high', MEDIUM: 'badge-medium', LOW: 'badge-low' }[urgency] || 'badge-low';

  const redFlags = data.red_flags || [];
  const matchedSymptoms = data.matched_symptoms || symptoms;

  resEl.innerHTML = `
    <div class="result-card ${urgencyClass}">
      <div class="result-title">
        <span class="badge ${urgencyBadge}" style="font-size:1rem; padding:0.4rem 1rem">${urgency}</span>
        <h3>Triage Result</h3>
      </div>
      <div class="result-section">
        <div class="result-label">Symptoms Detected</div>
        <div class="result-value">${matchedSymptoms.join(', ')}</div>
      </div>
      <div class="result-section">
        <div class="result-label">Recommended Specialist</div>
        <div class="result-value">👨‍⚕️ ${data.specialist || 'General Physician'}</div>
      </div>
      <div class="result-section">
        <div class="result-label">Advice</div>
        <div class="result-value">${data.advice || 'Consult a doctor.'}</div>
      </div>
      ${data.icd10 ? `<div class="result-section"><div class="result-label">ICD-10 Code</div><div class="result-value" style="font-family:monospace">${data.icd10}</div></div>` : ''}
      ${redFlags.length ? `
      <div class="result-section">
        <div class="result-label">Red Flags to Watch</div>
        <div class="red-flags">${redFlags.map(f => `<span class="red-flag-chip">⚠️ ${escHtml(f)}</span>`).join('')}</div>
      </div>` : ''}
      <div style="margin-top:1.25rem">
        <button class="btn btn-primary btn-sm" onclick="showPage('doctors')">Find a Doctor →</button>
      </div>
    </div>`;
}

// ── Pharmacy ──────────────────────────────────────────────────
async function loadPharmacies() {
  const village = document.getElementById('villageFilter')?.value.trim() || '';
  const el = document.getElementById('pharmacyList');
  el.innerHTML = '<div class="loader"><span class="spinner"></span>Loading pharmacies...</div>';

  let url = '/api/pharmacy';
  if (village) url += '?village=' + encodeURIComponent(village);

  const { ok, data } = await api(url);
  if (!ok) { el.innerHTML = '<p class="muted">Failed to load.</p>'; return; }

  if (!data.length) {
    el.innerHTML = '<div class="empty-state"><div class="empty-icon">🏪</div><p>No pharmacies found.</p></div>'; return;
  }

  el.innerHTML = data.map(p => `
    <div class="card">
      <div class="card-header">
        <div>
          <div class="card-title">🏪 ${escHtml(p.name)}</div>
          <div class="card-subtitle">${escHtml(p.village || '')}</div>
        </div>
      </div>
      <div class="card-body">
        <p>📍 ${escHtml(p.address || '')}</p>
        <p>📞 <a href="tel:${p.phone}">${p.phone}</a></p>
        ${p.lat ? `<p>🗺️ <a href="https://maps.google.com/?q=${p.lat},${p.lng}" target="_blank">View on Map</a></p>` : ''}
      </div>
      <div class="card-footer">
        <button class="btn btn-outline btn-sm" onclick="viewStock(${p.id}, '${escHtml(p.name)}')">View Stock</button>
      </div>
    </div>`).join('');
}

async function viewStock(pharmacyId, name) {
  document.getElementById('stockModalTitle').textContent = name + ' — Stock';
  document.getElementById('stockContent').innerHTML = '<div class="loader"><span class="spinner"></span>Loading...</div>';
  document.getElementById('stockModal').style.display = 'flex';

  const { ok, data } = await api(`/api/pharmacy/${pharmacyId}/stock`);
  if (!ok) { document.getElementById('stockContent').innerHTML = '<p class="muted">Failed to load stock.</p>'; return; }

  const { stock, low_stock, out_of_stock } = data;

  let html = '';
  if (low_stock && low_stock.length) {
    html += `<div class="alert alert-warning">⚠️ ${low_stock.length} medicine(s) low on stock (&le;10 units).</div>`;
  }
  if (out_of_stock && out_of_stock.length) {
    html += `<div class="alert alert-error">❌ ${out_of_stock.length} medicine(s) out of stock.</div>`;
  }
  if (!stock || !stock.length) {
    html += '<p class="muted">No stock data available.</p>';
  } else {
    html += `<div class="table-wrap"><table>
      <thead><tr><th>Medicine</th><th>Generic</th><th>Quantity</th><th>Price (₹)</th><th>Status</th></tr></thead>
      <tbody>
      ${stock.map(s => `
        <tr>
          <td><strong>${escHtml(s.medicine_name)}</strong></td>
          <td>${escHtml(s.generic || '—')}</td>
          <td>${s.quantity}</td>
          <td>₹${s.unit_price.toFixed(2)}</td>
          <td><span class="badge ${s.quantity > 10 ? 'badge-green' : s.quantity > 0 ? 'badge-orange' : 'badge-red'}">
            ${s.quantity > 10 ? 'In Stock' : s.quantity > 0 ? 'Low Stock' : 'Out of Stock'}
          </span></td>
        </tr>`).join('')}
      </tbody></table></div>`;
  }
  document.getElementById('stockContent').innerHTML = html;
}

function closeStockModal() {
  document.getElementById('stockModal').style.display = 'none';
}

// ── Health Records ────────────────────────────────────────────
async function loadRecords() {
  if (!token || !currentUser) return;
  const el = document.getElementById('recordsList');
  el.innerHTML = '<div class="loader"><span class="spinner"></span>Loading records...</div>';

  const rtype = document.getElementById('recordTypeFilter')?.value || '';
  let url = `/api/records/${currentUser.id}`;
  if (rtype) url += '?type=' + rtype;

  const { ok, data } = await api(url);
  if (!ok) { el.innerHTML = '<p class="muted">Failed to load records.</p>'; return; }

  if (!data.length) {
    el.innerHTML = '<div class="empty-state"><div class="empty-icon">📋</div><p>No health records found.</p></div>'; return;
  }

  el.innerHTML = data.map(r => {
    const dt = new Date(r.recorded_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
    return `
    <div class="record-card">
      <div class="record-header">
        <div>
          <div class="record-title">${escHtml(r.title)}</div>
          <div class="record-body">${dt} ${r.doctor_name ? '· Dr. ' + escHtml(r.doctor_name) : ''}</div>
        </div>
        <span class="badge badge-blue">${r.record_type}</span>
      </div>
      ${r.description ? `<p style="font-size:0.88rem;margin-top:0.5rem;color:var(--text-muted)">${escHtml(r.description)}</p>` : ''}
      ${r.diagnosis ? `<p style="font-size:0.88rem;margin-top:0.25rem"><strong>Diagnosis:</strong> ${escHtml(r.diagnosis)}</p>` : ''}
      ${r.medications && r.medications !== '[]' ? `<p style="font-size:0.88rem;margin-top:0.25rem"><strong>Medications:</strong> ${escHtml(r.medications)}</p>` : ''}
    </div>`;
  }).join('');
}

// ── Utilities ─────────────────────────────────────────────────
function escHtml(s) {
  if (!s) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function showErr(el, msg) {
  el.textContent = msg;
  el.style.display = 'block';
}

let toastTimer;
function toast(msg, type) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = 'toast show' + (type ? ' ' + type : '');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.classList.remove('show'); }, 3000);
}
