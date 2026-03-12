/* simple gear speed calculator for PWA */

document.addEventListener('DOMContentLoaded', () => {
  const front = document.getElementById('front');
  const wheel = document.getElementById('wheel');
  const tire = document.getElementById('tire');
  const mode = document.getElementById('mode');
  const customSection = document.getElementById('custom-gears');
  const rearInput = document.getElementById('rear');
  const generateBtn = document.getElementById('generate');
  const clearBtn = document.getElementById('clear');
  const copyBtn = document.getElementById('copy');
  const tableDiv = document.getElementById('table');

  mode.addEventListener('change', () => {
    customSection.style.display = mode.value === 'custom' ? 'block' : 'none';
  });

  // settings and presets
  let cachedSettings = null;
  function fetchSettings() {
    return fetch('bike_speed_settings.json', {cache: 'no-store'})
      .then(r => r.json())
      .then(json => {
        const str = JSON.stringify(json);
        const prev = localStorage.getItem('cachedSettings');
        if (prev !== str) {
          localStorage.setItem('cachedSettings', str);
          console.log('Settings updated');
        }
        cachedSettings = json;
        populatePresetList();
      }).catch(e => console.warn('could not load settings', e));
  }

  function populatePresetList() {
    if (!cachedSettings || !cachedSettings.cassette_presets) return;
    const catFilter = document.getElementById('filter-category').value;
    const manFilter = document.getElementById('filter-manufacturer').value;
    const speedsFilter = document.getElementById('filter-speeds').value;
    const sel = document.getElementById('preset');
    sel.innerHTML = '<option value="">-- select --</option>';
    // also refresh manufacturer options
    const manSet = new Set();
    cachedSettings.cassette_presets.forEach((p,i) => {
      if (p.manufacturer) manSet.add(p.manufacturer);
    });
    const manSel = document.getElementById('filter-manufacturer');
    manSel.innerHTML = '<option value="">All</option>';
    Array.from(manSet).sort().forEach(m => {
      const o = document.createElement('option'); o.value=m; o.textContent=m; manSel.appendChild(o);
    });

    cachedSettings.cassette_presets.forEach((p,i) => {
      if (catFilter && p.category !== catFilter) return;
      if (manFilter && p.manufacturer !== manFilter) return;
      if (speedsFilter && String(p.speeds) !== speedsFilter) return;
      const opt = document.createElement('option');
      opt.value = i;
      opt.textContent = p.model + (p.manufacturer?" ("+p.manufacturer+")":"");
      sel.appendChild(opt);
    });
  }

  document.getElementById('preset').addEventListener('change', e => {
    const idx = e.target.value;
    if (idx === '') return;
    const p = cachedSettings.cassette_presets[idx];
    rearInput.value = p.gears.join(',');
    mode.value = 'custom';
    customSection.style.display = 'block';
  });

  document.getElementById('filter-category').addEventListener('change', populatePresetList);
  document.getElementById('filter-manufacturer').addEventListener('change', populatePresetList);
  document.getElementById('filter-speeds').addEventListener('change', populatePresetList);

  document.getElementById('download-presets').addEventListener('click', () => {
    if (!cachedSettings) return;
    const blob = new Blob([JSON.stringify(cachedSettings, null, 2)], {type:'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'bike_speed_settings.json';
    a.click();
    URL.revokeObjectURL(url);
  });

  // custom gear sets stored separately in localStorage
  function loadCustomSets() {
    const list = JSON.parse(localStorage.getItem('customGears')||'[]');
    const sel = document.getElementById('custom-list');
    sel.innerHTML = '';
    list.forEach((item,i) => {
      const opt = document.createElement('option');
      opt.value = i;
      opt.textContent = item.name;
      sel.appendChild(opt);
    });
  }
  loadCustomSets();

  document.getElementById('save-custom').addEventListener('click', () => {
    const text = rearInput.value.trim();
    if (!text) { alert('Enter numbers first'); return; }
    const gears = text.split(/[^0-9]+/).filter(s=>s).map(n=>parseInt(n,10));
    if (gears.length===0) { alert('No valid gears'); return; }
    const name = prompt('Name this set');
    if (!name) return;
    const list = JSON.parse(localStorage.getItem('customGears')||'[]');
    list.push({name, gears});
    localStorage.setItem('customGears', JSON.stringify(list));
    loadCustomSets();
  });

  document.getElementById('custom-list').addEventListener('change', e => {
    const idx = e.target.value;
    if (idx === '') return;
    const list = JSON.parse(localStorage.getItem('customGears')||'[]');
    const item = list[idx];
    if (item) {
      rearInput.value = item.gears.join(',');
    }
  });

  document.getElementById('export-custom').addEventListener('click', () => {
    const list = JSON.parse(localStorage.getItem('customGears')||'[]');
    const blob = new Blob([JSON.stringify(list, null,2)], {type:'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'custom_gear_sets.json';
    a.click();
    URL.revokeObjectURL(url);
  });

  // state persistence
  function saveState() {
    const state = {
      front: front.value,
      wheel: wheel.value,
      tire: tire.value,
      mode: mode.value,
      rear: rearInput.value
    };
    localStorage.setItem('formState', JSON.stringify(state));
  }

  function loadState() {
    try {
      const state = JSON.parse(localStorage.getItem('formState')||'{}');
      if (state.front) front.value = state.front;
      if (state.wheel) wheel.value = state.wheel;
      if (state.tire) tire.value = state.tire;
      if (state.mode) {
        mode.value = state.mode;
        customSection.style.display = state.mode === 'custom' ? 'block' : 'none';
      }
      if (state.rear) rearInput.value = state.rear;
    } catch(e) {
      console.warn('failed to load state', e);
    }
  }

  // attach listeners for form inputs
  [front, wheel, tire, mode, rearInput].forEach(el => {
    el.addEventListener('change', saveState);
  });

  // load stored inputs before anything else
  loadState();

  // fetch settings on start
  fetchSettings();

  generateBtn.addEventListener('click', () => {
    const f = parseFloat(front.value);
    if (isNaN(f) || f < 20 || f > 60) {
      alert('Front gear must be 20–60');
      return;
    }
    const w = parseFloat(wheel.value);
    const t = parseFloat(tire.value);
    const diameter = w + 2 * t + 5; // mm
    let gears = [];
    if (mode.value === 'all') {
      for (let i = 9; i <= 51; i++) gears.push(i);
    } else {
      const parts = rearInput.value.split(/[^0-9]+/).filter(s => s);
      gears = parts.map(s => parseInt(s,10)).filter(n => !isNaN(n));
      if (gears.length === 0) { alert('Enter rear gear numbers'); return; }
    }
    createTable(f, diameter, gears);
  });

  clearBtn.addEventListener('click', () => {
    tableDiv.innerHTML = '';
  });

  copyBtn.addEventListener('click', () => {
    const text = tableDiv.innerText;
    if (!text) return;
    navigator.clipboard.writeText(text).then(() => {
      alert('Copied to clipboard');
    });
  });

// helper: speed color grading (mimics Python version)
    function getSpeedColor(speed) {
      let s = Math.max(0, Math.min(speed, 60));
      const ratio = s / 60.0;
      let r,g,b;
      if (ratio <= 0.25) {
        r = Math.floor(52 + (100 - 52) * (ratio / 0.25));
        g = Math.floor(152 + (180 - 152) * (ratio / 0.25));
        b = Math.floor(219 + (255 - 219) * (ratio / 0.25));
      } else if (ratio <= 0.5) {
        const local = (ratio - 0.25) / 0.25;
        r = Math.floor(100 + (76 - 100) * local);
        g = Math.floor(180 + (205 - 180) * local);
        b = Math.floor(255 + (92 - 255) * local);
      } else if (ratio <= 0.75) {
        const local = (ratio - 0.5) / 0.25;
        r = Math.floor(76 + (255 - 76) * local);
        g = Math.floor(205 + (235 - 205) * local);
        b = Math.floor(92 + (59 - 92) * local);
      } else {
        const local = (ratio - 0.75) / 0.25;
        r = 255;
        g = Math.floor(235 + (99 - 235) * local);
        b = Math.floor(59 + (71 - 59) * local);
      }
      return `#${r.toString(16).padStart(2,'0')}${g.toString(16).padStart(2,'0')}${b.toString(16).padStart(2,'0')}`;
    }

    function getRatioDiffColor(rd) {
      let d = Math.abs(rd);
      d = Math.max(0.05, Math.min(d, 0.50));
      let r,g,b;
      if (d <= 0.15) {
        const local = (d - 0.05) / 0.10;
        r = Math.floor(76 - (76 - 46) * local);
        g = Math.floor(175 + (205 - 175) * local);
        b = Math.floor(80 - (80 - 92) * local);
      } else if (d <= 0.30) {
        const local = (d - 0.15) / 0.15;
        r = Math.floor(46 + (255 - 46) * local);
        g = Math.floor(205 + (235 - 205) * local);
        b = Math.floor(92 - (92 - 59) * local);
      } else {
        const local = Math.min((d - 0.30) / 0.20, 1.0);
        r = 255;
        g = Math.floor(235 - (235 - 140) * local);
        b = Math.floor(59 - (59 - 50) * local);
      }
      return `#${r.toString(16).padStart(2,'0')}${g.toString(16).padStart(2,'0')}${b.toString(16).padStart(2,'0')}`;
    }

    function createTable(frontGear, outerDiameter, rearGears) {
      const cadences = [70,80,90,100,110];
      const isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      const numBg = isDark ? '#0a84ff' : '#007aff';
      const gearBg = isDark ? '#1c1c1e' : '#f2f2f7';
      const gearText = isDark ? '#ffffff' : '#3c3c43';
      const headerBg = isDark ? '#1c1c1e' : '#007aff';
      const headerText = isDark ? '#ffffff' : '#ffffff';

      let html = `<table><thead><tr style="background:${headerBg};color:${headerText};"><th>#</th><th>T</th><th>Ratio</th><th>\u0394R</th>`;
      cadences.forEach(c => html += `<th>${c}</th>`);
      html += '</tr></thead><tbody>';
      rearGears.sort((a,b)=>a-b);
      let prevRatio = null;
      rearGears.forEach((t,i) => {
        const ratio = frontGear / t;
        const dr = prevRatio !== null ? Math.abs(ratio - prevRatio) : '';
        html += '<tr>';
        // number column
        html += `<td style="background:${numBg};color:white;font-weight:bold;">${i+1}</td>`;
        // gear column
        html += `<td style="background:${gearBg};color:${gearText};font-weight:bold;">${t}</td>`;
        html += `<td>${ratio.toFixed(2)}</td>`;
        html += `<td style="background:${dr?getRatioDiffColor(dr):'transparent'};color:#333;">${dr?dr.toFixed(2):''}</td>`;
        cadences.forEach(c => {
          const speed = Math.PI * outerDiameter * c * 60 * ratio / 1e6;
          const color = getSpeedColor(speed);
          const textcol = speed > 45 ? 'white' : '#333';
          html += `<td style="background:${color};color:${textcol};">${speed.toFixed(1)}</td>`;
        });
        html += '</tr>';
        prevRatio = ratio;
      });
      html += '</tbody></table>';
      tableDiv.innerHTML = html;
    }

  // register service worker
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('service-worker.js')
      .catch(err => console.warn('SW registration failed', err));
  }
});
