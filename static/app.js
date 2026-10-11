const API = (path, options = {}) => fetch(path, {
  ...options,
  headers: {
    Authorization: `Bearer ${localStorage.getItem('jal-role') === 'crew' ? 'demo-crew' : 'demo-admin'}`,
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  },
});
const $ = (id) => document.getElementById(id);
const state = { role: localStorage.getItem('jal-role') || 'admin', view: 'command', wards: null, sites: null, tankers: null, kpis: null, map: null, routes: [] };
let toastTimer;
function toast(text) { const el = $('toast'); el.textContent = text; el.classList.add('show'); clearTimeout(toastTimer); toastTimer = setTimeout(() => el.classList.remove('show'), 2800); }
function formatLiters(value) { const n = Number(value || 0); if (n >= 1e9) return `${(n / 1e9).toFixed(2)}B`; if (n >= 1e6) return `${(n / 1e6).toFixed(1)}M`; if (n >= 1e3) return `${(n / 1e3).toFixed(0)}K`; return `${Math.round(n)}`; }
function formatExact(value) { return new Intl.NumberFormat('en-IN').format(Number(value || 0)); }
async function request(path, options) {
  const response = await API(path, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data?.detail?.message || data?.detail || `Request failed (${response.status})`);
  return data;
}
function tickClock() { $('clock').textContent = `${new Intl.DateTimeFormat('en-IN', { timeZone: 'Asia/Kolkata', hour: '2-digit', minute: '2-digit', hour12: false }).format(new Date())} IST`; }
function paintKpis(k) {
  state.kpis = k;
  $('kpi-runoff').textContent = formatLiters(k.runoff_liters);
  $('kpi-risk').textContent = `${k.wards_at_risk} / 20`;
  $('kpi-recharge').textContent = `${formatLiters(k.recharge_liters)} L`;
  $('kpi-tankers').textContent = String(k.active_tankers);
  $('metric-recharge').textContent = `${(Number(k.recharge_liters) / 1e6).toFixed(2)}M L`;
  $('metric-hours').textContent = `${Number(k.flood_hours_avoided).toFixed(1)} h`;
  $('metric-km').textContent = `${Number(k.tanker_km_saved_pct).toFixed(0)}%`;
  $('context-rain').textContent = Number(k.rain_mm).toFixed(0);
  $('rain-slider').value = k.rain_mm;
  $('rain-readout').textContent = Number(k.rain_mm).toFixed(0);
  $('rain-label').textContent = Number(k.rain_mm).toFixed(0);
  renderImpact(k);
}
function renderWards(geojson) {
  state.wards = geojson;
  const top = [...geojson.features].sort((a, b) => b.properties.water_stress - a.properties.water_stress).slice(0, 3);
  $('ward-list').innerHTML = top.map((f, i) => `<div class="ward-row"><span class="ward-rank">${String(i + 1).padStart(2, '0')}</span><div class="ward-copy"><strong>${f.properties.name}</strong><small>${f.properties.water_stress.toFixed(1)}% water stress · ${formatExact(f.properties.runoff_liters)} L runoff</small></div><span class="ward-risk">${Math.round(f.properties.flood_risk * 100)}%</span></div>`).join('');
  if (state.map && state.map.isStyleLoaded() && state.map.getSource('wards')) state.map.getSource('wards').setData(geojson);
  else if (!window.maplibregl) renderFallbackMap();
}
function renderImpact(k) {
  const totalStops = Number(k.total_stops || 0);
  const completion = totalStops ? `${Number(k.delivery_completion_pct).toFixed(0)}%` : '—';
  const completionNote = totalStops ? `${k.delivered_stops}/${totalStops} synthetic stops complete` : 'no synthetic route plan yet';
  $('impact-metrics').innerHTML = [
    ['Recharge allocation', `${formatLiters(k.allocated_liters)} L`, `${formatLiters(k.site_capacity_liters)} L total site capacity · synthetic`],
    ['Flood-hours avoided', `${Number(k.flood_hours_avoided).toFixed(1)} h`, 'estimated proxy'],
    ['Tanker distance saved', `${Number(k.tanker_km_saved_pct).toFixed(0)}%`, `₹${formatExact(k.cost_saved_inr)} est. cost saved`],
    ['Delivery completion', completion, completionNote],
  ].map(([label, value, sub]) => `<article><small>${label.toUpperCase()}</small><strong>${value}</strong><small>${sub}</small></article>`).join('');
}
function colorExpression(property) {
  const stops = property === 'water_stress' ? [0, '#153c32', 55, '#6dc99e', 78, '#e7bd5e', 100, '#e47763']
    : property === 'recharge_potential' ? [0, '#3d4438', .35, '#79985d', .65, '#4dc89d', 1, '#74e3b5']
      : [0, '#16392f', .45, '#60bd91', .65, '#e5b65a', 1, '#e47763'];
  return ['interpolate', ['linear'], ['get', property], ...stops];
}
const LAYER_META = {
  flood_risk: { title: 'FLOOD RISK', scale: ['LOW', 'WATCH', 'HIGH'], gradient: 'linear-gradient(90deg,#55c99a,#edc45d,#e87864)' },
  water_stress: { title: 'WATER STRESS', scale: ['LOW', 'MODERATE', 'HIGH'], gradient: 'linear-gradient(90deg,#153c32,#e7bd5e,#e47763)' },
  recharge_potential: { title: 'RECHARGE POTENTIAL', scale: ['LOW', 'MODERATE', 'HIGH'], gradient: 'linear-gradient(90deg,#3d4438,#4dc89d,#74e3b5)' },
};
function setLayer(property) {
  const meta = LAYER_META[property];
  if (!meta) return;
  $('map-legend-title').textContent = meta.title;
  $('legend-gradient').style.background = meta.gradient;
  $('legend-scale').innerHTML = meta.scale.map((label) => `<span>${label}</span>`).join('');
  if (!state.map || !state.map.getLayer('ward-fill')) return;
  state.map.setPaintProperty('ward-fill', 'fill-color', colorExpression(property));
  state.map.setPaintProperty('ward-fill', 'fill-opacity', .58);
}
function initMap() {
  if (!window.maplibregl) { renderFallbackMap(); return; }
  try {
    state.map = new maplibregl.Map({ container: 'map', style: 'https://tiles.openfreemap.org/styles/positron', center: [77.305, 28.402], zoom: 12.2, pitch: 24, bearing: -7, attributionControl: true });
    state.map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right');
    state.map.on('load', () => {
      $('map').hidden = false; $('map-fallback').hidden = true; $('map-loading').hidden = true;
      state.map.fitBounds([[77.264, 28.376], [77.337, 28.426]], { padding: 34, maxZoom: 11.4, duration: 0 });
      state.map.addSource('wards', { type: 'geojson', data: state.wards || { type: 'FeatureCollection', features: [] } });
      state.map.addLayer({ id: 'ward-fill', type: 'fill', source: 'wards', paint: { 'fill-color': colorExpression($('layer-select').value), 'fill-opacity': .58 } });
      state.map.addLayer({ id: 'ward-line', type: 'line', source: 'wards', paint: { 'line-color': '#16624b', 'line-width': 1.4, 'line-opacity': .9 } });
      state.map.addLayer({ id: 'ward-label', type: 'symbol', source: 'wards', layout: { 'text-field': ['get', 'name'], 'text-size': 9, 'text-font': ['Open Sans Regular'], 'text-allow-overlap': false }, paint: { 'text-color': '#f0fff6', 'text-halo-color': '#0b1c16', 'text-halo-width': 1.3 } });
      setLayer($('layer-select').value);
      state.map.addSource('sites', { type: 'geojson', data: state.sites || { type: 'FeatureCollection', features: [] } });
      state.map.addLayer({ id: 'site-circles', type: 'circle', source: 'sites', paint: { 'circle-radius': 4, 'circle-color': ['match', ['get', 'type'], 'outfall', '#e9b958', '#58e0b1'], 'circle-stroke-color': '#092017', 'circle-stroke-width': 1.2 } });
      state.map.on('click', 'ward-fill', (event) => { const p = event.features?.[0]?.properties; if (p) toast(`${p.name} · ${Number(p.water_stress).toFixed(1)}% stress · synthetic data`); });
      state.map.on('mouseenter', 'ward-fill', () => state.map.getCanvas().style.cursor = 'pointer');
      state.map.on('mouseleave', 'ward-fill', () => state.map.getCanvas().style.cursor = '');
      if (state.wards) state.map.getSource('wards').setData(state.wards);
      if (state.sites) state.map.getSource('sites').setData(state.sites);
    });
    state.map.on('error', (event) => { if (event?.error && !state.map?.isStyleLoaded() && state.wards) renderFallbackMap(); });
    setTimeout(() => { if (!state.map?.loaded() && state.wards) renderFallbackMap(); }, 12_000);
  } catch (_) { renderFallbackMap(); }
}
function renderFallbackMap() {
  $('map').hidden = true;
  $('map-loading').hidden = true;
  const container = $('map-fallback'); container.hidden = false;
  if (!state.wards?.features) { container.textContent = 'Loading synthetic catchment map…'; return; }
  const property = $('layer-select').value;
  const fallbackColor = (feature) => {
    const value = Number(feature.properties[property] || 0);
    if (property === 'water_stress') return value < 55 ? '#55c99a' : value < 78 ? '#e7bd5e' : '#e47763';
    if (property === 'recharge_potential') return value < .35 ? '#88917a' : value < .65 ? '#67b982' : '#29b98a';
    return value < .45 ? '#55c99a' : value < .65 ? '#e7bd5e' : '#e47763';
  };
  container.innerHTML = state.wards.features.map((f, i) => {
    const x = 4 + (i % 5) * 18.5, y = 8 + Math.floor(i / 5) * 21;
    const color = fallbackColor(f);
    return `<span class="fallback-ward" style="left:${x}%;top:${y}%;width:17%;height:19%;border-color:${color};background:${color}55">${f.properties.name}</span>`;
  }).join('');
}
function renderRoutes(result) {
  state.routes = result.routes || [];
  const routes = state.role === 'crew' ? state.routes.filter((r) => r.tanker_id === 'T01') : state.routes;
  if (!routes.length) { $('routes-list').innerHTML = '<span class="muted">No route is available for this role.</span>'; return; }
  $('routes-list').innerHTML = routes.map((r) => `<div class="route-row"><span class="route-id">${r.tanker_id}</span><div><strong>${r.stops.map((s) => s.ward_name).join(' → ')}</strong><small>${r.stops.filter((s) => s.delivered).length}/${r.stops.length} simulated stops complete · ${r.status}</small></div><div class="route-actions"><span class="route-km">${Number(r.distance_km).toFixed(1)} km</span>${state.role === 'crew' ? r.stops.filter((s) => !s.delivered).map((s) => `<button class="button button-primary deliver-button" data-stop="${s.stop_id}">Mark delivered</button>`).join('') : ''}</div></div>`).join('');
  document.querySelectorAll('.deliver-button').forEach((button) => button.addEventListener('click', () => markDelivered(button.dataset.stop)));
}
async function loadBase() {
  try {
    const [wards, sites, kpis, tankers, routes] = await Promise.all([request('/api/wards'), request('/api/recharge/sites'), request('/api/kpis'), request('/api/tankers'), request('/api/dispatch/routes')]);
    state.sites = sites; state.tankers = tankers; renderWards(wards); paintKpis(kpis); populateSites(sites);
    renderRoutes(routes);
    if (state.map?.isStyleLoaded() && state.map.getSource('sites')) state.map.getSource('sites').setData(sites);
  } catch (error) { toast(`Dashboard data unavailable: ${error.message}`); }
}
function populateSites(sites) {
  const select = $('site-select');
  if (!sites?.features) return;
  select.innerHTML = sites.features.map((f) => `<option value="${f.id}">${f.properties.name} · ${Math.round(f.properties.score * 100)} priority</option>`).join('');
}
async function applyScenario() {
  const button = $('apply-scenario'); button.disabled = true;
  try {
    const result = await request('/api/simulate', { method: 'POST', body: JSON.stringify({ rain_mm: Number($('rain-slider').value), duration_hours: Number($('duration-select').value) }) });
    renderWards(result.wards); paintKpis(result.kpis); toast(`Scenario updated · ${result.high_risk_wards} wards elevated · synthetic estimate`);
  } catch (error) { toast(error.message); } finally { button.disabled = false; }
}
async function optimizeRoutes() {
  const button = $('optimize-button'); button.disabled = true;
  try {
    const result = await request('/api/dispatch/solve', { method: 'POST', body: '{}' });
    renderRoutes(result); $('dispatch-panel').hidden = false;
    paintKpis(await request('/api/kpis'));
    toast(`${result.total_routes} synthetic routes · ${Number(result.total_km).toFixed(1)} km`);
  } catch (error) { toast(error.message); } finally { button.disabled = false; }
}
async function markDelivered(stopId) {
  try { await request(`/api/dispatch/stops/${encodeURIComponent(stopId)}/delivered`, { method: 'POST', body: JSON.stringify({ note: 'Demo completion' }) }); const [routes, kpis] = await Promise.all([request('/api/dispatch/routes'), request('/api/kpis')]); renderRoutes(routes); paintKpis(kpis); toast('Stop marked complete · synthetic demo only'); }
  catch (error) { toast(error.message); }
}
async function allocate() {
  const site = $('site-select').value;
  try { const result = await request('/api/recharge/allocate', { method: 'POST', body: JSON.stringify({ site_id: site, liters: Number($('allocation-slider').value) }) }); $('allocation-modal').hidden = true; const [kpis, sites] = await Promise.all([request('/api/kpis'), request('/api/recharge/sites')]); paintKpis(kpis); populateSites(sites); toast(`${formatExact(result.allocated_liters)} L allocated · synthetic demo`); }
  catch (error) { toast(error.message); }
}
function addMessage(text, type) {
  const article = document.createElement('article'); article.className = `chat-bubble ${type}`;
  const label = type === 'user' ? 'YOU' : 'JAL-SETU COPILOT';
  article.innerHTML = `<small>${label}<span>${type === 'user' ? 'JUST NOW' : 'RULE-BASED DEMO'}</span></small><p></p>`;
  article.querySelector('p').textContent = text;
  $('chat-messages').appendChild(article); $('chat-messages').scrollTop = $('chat-messages').scrollHeight;
  return article.querySelector('p');
}
async function sendChat(message) {
  const clean = message.trim(); if (!clean) return;
  addMessage(clean, 'user'); const reply = addMessage('', 'assistant');
  try {
    const response = await API('/api/copilot/chat', { method: 'POST', headers: { Accept: 'text/event-stream' }, body: JSON.stringify({ message: clean, stream: true }) });
    if (!response.ok || !response.body) throw new Error(`Copilot request failed (${response.status})`);
    const reader = response.body.getReader(); const decoder = new TextDecoder(); let buffer = '';
    while (true) {
      const { value, done } = await reader.read(); buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
      const chunks = buffer.split('\n\n'); buffer = chunks.pop() || '';
      for (const chunk of chunks) { const line = chunk.split('\n').find((x) => x.startsWith('data: ')); if (!line) continue; const data = JSON.parse(line.slice(6)); if (data.text) reply.textContent += data.text; }
      if (done) break;
    }
    $('chat-messages').scrollTop = $('chat-messages').scrollHeight;
  } catch (error) { reply.textContent = error.message; }
}
function syncRoleControls() {
  const crew = state.role === 'crew';
  $('allocate-button').hidden = crew; $('optimize-button').hidden = crew; $('apply-scenario').hidden = crew; $('solve-button').hidden = crew;
  $('rain-slider').disabled = crew; $('duration-select').disabled = crew;
}
function setView(view) {
  state.view = view;
  document.querySelectorAll('.nav-item').forEach((button) => button.classList.toggle('active', button.dataset.view === view));
  $('dispatch-panel').hidden = view !== 'dispatch'; $('impact-panel').hidden = view !== 'impact';
  const titles = { command: ['COMMAND', 'Water command centre', 'Urban flood response · Managed recharge · Essential water delivery'], dispatch: ['DISPATCH', 'Tanker dispatch', 'Capacity-aware synthetic routing · Field crew actions'], impact: ['IMPACT', 'Scenario impact', 'Transparent estimates · Synthetic demo metrics'] };
  [$('view-kicker').textContent, $('view-title').textContent, $('view-subtitle').textContent] = titles[view];
  if (view === 'dispatch' && !state.routes.length) $('routes-list').innerHTML = state.role === 'crew'
    ? '<span class="muted">No assigned route yet</span><p>An ICCC Admin must optimize synthetic tanker routes before field work.</p>'
    : '<span class="muted">Dispatch not solved yet</span><p>Run Optimize tankers to compute synthetic routes.</p>';
  setTimeout(() => state.map?.resize(), 50);
}
$('rain-slider').addEventListener('input', (event) => { $('rain-readout').textContent = event.target.value; $('rain-label').textContent = event.target.value; });
 $('layer-select').addEventListener('change', (event) => { setLayer(event.target.value); if (!$('map-fallback').hidden) renderFallbackMap(); });
$('apply-scenario').addEventListener('click', applyScenario);
$('optimize-button').addEventListener('click', optimizeRoutes);
$('solve-button').addEventListener('click', optimizeRoutes);
$('allocate-button').addEventListener('click', () => { $('allocation-modal').hidden = false; });
$('modal-close').addEventListener('click', () => $('allocation-modal').hidden = true);
$('allocation-modal').addEventListener('click', (event) => { if (event.target === $('allocation-modal')) $('allocation-modal').hidden = true; });
$('allocation-slider').addEventListener('input', (event) => $('allocation-value').textContent = `${formatExact(event.target.value)} L`);
$('confirm-allocation').addEventListener('click', allocate);
document.querySelectorAll('.nav-item').forEach((button) => button.addEventListener('click', () => setView(button.dataset.view)));
document.querySelectorAll('[data-prompt]').forEach((button) => button.addEventListener('click', () => sendChat(button.dataset.prompt)));
$('chat-form').addEventListener('submit', (event) => { event.preventDefault(); const input = $('chat-input'); const value = input.value; input.value = ''; sendChat(value); });
$('chat-input').addEventListener('keydown', (event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); $('chat-form').requestSubmit(); } });
$('copilot-info').addEventListener('click', () => toast('Rule-based assistant · synthetic metrics only · verify all field conditions'));
$('role-select').value = state.role;
syncRoleControls();
$('role-select').addEventListener('change', async (event) => { state.role = event.target.value; localStorage.setItem('jal-role', state.role); $('role-select').value = state.role; syncRoleControls(); toast(state.role === 'crew' ? 'Field crew view · route scope limited to T01' : 'ICCC administrator view · simulated controls enabled'); await loadBase(); if (state.routes.length) renderRoutes({ routes: state.routes }); });
tickClock(); setInterval(tickClock, 30_000); initMap(); loadBase();
