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

  function createTable(frontGear, outerDiameter, rearGears) {
    const cadences = [70,80,90,100,110];
    let html = '<table><thead><tr><th>#</th><th>T</th><th>Ratio</th><th>\u0394R</th>';
    cadences.forEach(c => html += `<th>${c}</th>`);
    html += '</tr></thead><tbody>';
    rearGears.sort((a,b)=>a-b);
    let prevRatio = null;
    rearGears.forEach((t,i) => {
      const ratio = frontGear / t;
      const dr = prevRatio !== null ? Math.abs(ratio - prevRatio) : '';
      html += `<tr><td>${i+1}</td><td>${t}</td><td>${ratio.toFixed(2)}</td><td>${dr?dr.toFixed(2):''}</td>`;
      cadences.forEach(c => {
        const speed = Math.PI * outerDiameter * c * 60 * ratio / 1e6;
        html += `<td>${speed.toFixed(1)}</td>`;
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
