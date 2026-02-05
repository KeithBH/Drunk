const state = {
  range: '30',
  from: '',
  to: ''
};

const palette = ['#2563eb', '#7c3aed', '#10b981', '#f59e0b', '#ef4444', '#14b8a6'];

const els = {
  chips: Array.from(document.querySelectorAll('.chip[data-range]')),
  customForm: document.getElementById('customRange'),
  dateFrom: document.getElementById('dateFrom'),
  dateTo: document.getElementById('dateTo'),
  totalVolume: document.getElementById('totalVolume'),
  pureAlcohol: document.getElementById('pureAlcohol'),
  trendChart: document.getElementById('trendChart'),
  categoryPie: document.getElementById('categoryPie'),
  categoryLegend: document.getElementById('categoryLegend'),
  topRank: document.getElementById('topRank'),
  emptyState: document.getElementById('emptyState'),
  dashboardContent: document.getElementById('dashboardContent')
};

function bindEvents() {
  els.chips.forEach((chip) => {
    chip.addEventListener('click', () => {
      activateChip(chip.dataset.range);
      if (chip.dataset.range !== 'custom') {
        state.range = chip.dataset.range;
        state.from = '';
        state.to = '';
        loadDashboard();
      }
    });
  });

  els.customForm.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!els.dateFrom.value || !els.dateTo.value) return;
    state.range = 'custom';
    state.from = els.dateFrom.value;
    state.to = els.dateTo.value;
    loadDashboard();
  });
}

function activateChip(range) {
  els.chips.forEach((chip) => {
    const active = chip.dataset.range === range;
    chip.classList.toggle('active', active);
    chip.setAttribute('aria-selected', String(active));
  });
  els.customForm.hidden = range !== 'custom';
}

async function fetchStatistics() {
  const query = new URLSearchParams();
  query.set('range', state.range);
  if (state.range === 'custom') {
    query.set('from', state.from);
    query.set('to', state.to);
  }

  try {
    const response = await fetch(`/api/statistics?${query.toString()}`);
    if (!response.ok) throw new Error('Bad API response');
    return await response.json();
  } catch {
    return mockData(state.range);
  }
}

function mockData(range) {
  const days = Number(range) || 30;
  const trend = Array.from({ length: Math.min(days, 30) }, (_, index) => ({
    date: index + 1,
    volume: Math.max(0, Math.round(250 + Math.sin(index / 3) * 140 + Math.random() * 90 - 45))
  }));

  if (range === '7') {
    return {
      totalVolume: 0,
      pureAlcohol: 0,
      trend: [],
      categories: [],
      topPreferences: []
    };
  }

  return {
    totalVolume: trend.reduce((sum, point) => sum + point.volume, 0),
    pureAlcohol: Number((trend.reduce((sum, point) => sum + point.volume * 0.05 * 0.789, 0)).toFixed(1)),
    trend,
    categories: [
      { name: '啤酒', volume: 1400 },
      { name: '葡萄酒', volume: 650 },
      { name: '烈酒', volume: 410 },
      { name: '鸡尾酒', volume: 320 }
    ],
    topPreferences: [
      { name: 'IPA 啤酒', count: 8 },
      { name: '赤霞珠', count: 5 },
      { name: '威士忌 Highball', count: 4 }
    ]
  };
}

function render(data) {
  const noData = !data || !data.trend || data.trend.length === 0;
  els.emptyState.hidden = !noData;
  els.dashboardContent.hidden = noData;

  if (noData) return;

  els.totalVolume.textContent = `${data.totalVolume.toLocaleString()} ml`;
  els.pureAlcohol.textContent = `${data.pureAlcohol.toLocaleString()} g`;
  drawTrend(data.trend);
  drawCategories(data.categories || []);
  drawTop(data.topPreferences || []);
}

function drawTrend(points) {
  const width = 320;
  const height = 160;
  const pad = 18;
  const max = Math.max(...points.map((point) => point.volume), 1);
  const stepX = (width - pad * 2) / Math.max(points.length - 1, 1);

  const line = points
    .map((point, index) => {
      const x = pad + stepX * index;
      const y = height - pad - (point.volume / max) * (height - pad * 2);
      return `${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(' ');

  els.trendChart.innerHTML = `
    <polyline fill="none" stroke="#93c5fd" stroke-width="22" stroke-linecap="round" points="${line}" opacity="0.25"></polyline>
    <polyline fill="none" stroke="#2563eb" stroke-width="3" stroke-linecap="round" points="${line}"></polyline>
  `;
}

function drawCategories(categories) {
  const total = categories.reduce((sum, item) => sum + item.volume, 0) || 1;
  let running = 0;

  const gradients = categories
    .map((item, index) => {
      const start = running;
      running += (item.volume / total) * 100;
      return `${palette[index % palette.length]} ${start.toFixed(1)}% ${running.toFixed(1)}%`;
    })
    .join(', ');

  els.categoryPie.style.background = `conic-gradient(${gradients || '#dbeafe 0 100%'})`;
  els.categoryLegend.innerHTML = categories
    .map((item, index) => {
      const ratio = ((item.volume / total) * 100).toFixed(1);
      return `<li><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${palette[index % palette.length]};margin-right:6px;"></span>${item.name} ${ratio}%</li>`;
    })
    .join('');
}

function drawTop(list) {
  els.topRank.innerHTML = list
    .map((item) => `<li>${item.name}（${item.count} 次）</li>`)
    .join('');
}

async function loadDashboard() {
  const data = await fetchStatistics();
  render(data);
}

bindEvents();
activateChip('30');
loadDashboard();
