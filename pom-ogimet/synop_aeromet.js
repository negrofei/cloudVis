/**
 * SYNOP (FM-12) → AEROMET decoder for Argentina SMN-style reports.
 * Cloud base: hh × 50 m (national convention), height in AEROMET rounded up to 100 ft.
 */

const CLOUD_TYPE_C = {
  0: 'Ci', 1: 'Cc', 2: 'Cs', 3: 'Ac', 4: 'As', 5: 'Ns', 6: 'Sc', 7: 'St', 8: 'Cu', 9: 'Cb',
};

function visibilityKm(vv) {
  const code = Number(vv);
  if (Number.isNaN(code)) return null;
  if (code <= 49) return Math.max(0.1, (code * 100) / 1000);
  if (code >= 50 && code <= 80) return code - 50;
  if (code === 81) return 30;
  if (code === 82) return 40;
  if (code === 83) return 50;
  if (code === 84) return 60;
  if (code === 85) return 70;
  if (code === 86) return 80;
  if (code === 87) return 90;
  if (code >= 88) return 100;
  return null;
}

function cloudBaseFeet(hh) {
  const code = Number(hh);
  if (Number.isNaN(code)) return null;
  if (code === 0) return 0;
  const meters = code * 50;
  const feet = meters * 3.280839895;
  return Math.ceil(feet / 100) * 100;
}

function signedTemp(sn, ttt) {
  const sign = Number(sn) === 1 ? -1 : 1;
  return sign * Number(ttt) / 10;
}

function parseGroups(report) {
  const tokens = report.replace(/=/g, ' ').trim().split(/\s+/).filter(Boolean);
  const idx333 = tokens.indexOf('333');
  const idx555 = tokens.indexOf('555');
  const section1End = idx333 >= 0 ? idx333 : tokens.length;
  const section3End = idx555 >= 0 ? idx555 : tokens.length;

  return {
    tokens,
    section1: tokens.slice(0, section1End),
    section3: idx333 >= 0 ? tokens.slice(idx333 + 1, section3End) : [],
    section555: idx555 >= 0 ? tokens.slice(idx555 + 1) : [],
  };
}

function isFiveDigitGroup(token) {
  return token.length === 5 && /^\d+$/.test(token);
}

function headerEndIndex(section1) {
  const aaxx = section1.indexOf('AAXX');
  if (aaxx >= 0 && aaxx + 3 < section1.length) return aaxx + 3;
  return Math.min(3, section1.length);
}

function isTemperatureGroup(g) {
  return g[0] === '1' && (g[1] === '0' || g[1] === '1');
}

function isIrixhvvGroup(g) {
  return g[0] === '1' && !isTemperatureGroup(g);
}

function isNddffGroup(g) {
  const n = Number(g[0]);
  return n >= 0 && n <= 4 && Number(g.slice(1, 3)) <= 36;
}

function extractSection1Fields(section1) {
  const fields = {
    irixhvv: null,
    nddff: null,
    tempC: null,
    dewpointC: null,
    stationPressureHpa: null,
    seaLevelPressureHpa: null,
    cloudLayers8: [],
  };

  const body = section1.slice(headerEndIndex(section1));
  let seenIrixhvv = false;

  for (const token of body) {
    if (!isFiveDigitGroup(token)) continue;
    const g = token;
    const ind = g[0];

    if (!seenIrixhvv && isIrixhvvGroup(g)) {
      fields.irixhvv = {
        ir: Number(g[1]),
        ix: Number(g[2]),
        h: Number(g[3]),
        vv: Number(g.slice(3, 5)),
      };
      seenIrixhvv = true;
      continue;
    }

    if (seenIrixhvv && fields.nddff === null && isNddffGroup(g)) {
      fields.nddff = { n: Number(g[0]), dd: Number(g.slice(1, 3)), ff: Number(g.slice(3)) };
      continue;
    }

    if (ind === '1' && isTemperatureGroup(g)) {
      fields.tempC = signedTemp(g[1], g.slice(2));
      continue;
    }

    if (ind === '2' && (g[1] === '0' || g[1] === '1')) {
      fields.dewpointC = signedTemp(g[1], g.slice(2));
      continue;
    }

    if (ind === '3') {
      fields.stationPressureHpa = 1000 + Number(g.slice(1)) / 10;
      continue;
    }

    if (ind === '4') {
      fields.seaLevelPressureHpa = 1000 + Number(g.slice(1)) / 10;
      continue;
    }

    if (ind === '8' && g[3] !== '/' && g[4] !== '/') {
      const amount = Number(g[1]);
      const typeCode = Number(g[2]);
      const hh = Number(g.slice(3));
      if (amount > 0) fields.cloudLayers8.push({ amount, typeCode, hh, section: 1 });
    }
  }

  return fields;
}

function extractCloudLayers(groups, section) {
  const layers = [];
  for (const token of groups) {
    if (!isFiveDigitGroup(token) || token[0] !== '8') continue;
    if (token[3] === '/' || token[4] === '/') continue;
    const amount = Number(token[1]);
    const typeCode = Number(token[2]);
    const hh = Number(token.slice(3));
    if (amount > 0 && !Number.isNaN(typeCode) && !Number.isNaN(hh)) {
      layers.push({ amount, typeCode, hh, section });
    }
  }
  return layers;
}

function pickAerometCloud(layers) {
  if (!layers.length) return null;
  const sorted = [...layers].sort((a, b) => {
    const ha = cloudBaseFeet(a.hh) ?? 99999;
    const hb = cloudBaseFeet(b.hh) ?? 99999;
    return ha - hb;
  });
  const layer = sorted[0];
  const type = CLOUD_TYPE_C[layer.typeCode] || 'XX';
  const heightFt = cloudBaseFeet(layer.hh);
  if (heightFt === null) return null;
  return { amount: layer.amount, type, heightFt, text: `${layer.amount}${type}${heightFt}FT` };
}

function formatTemp(value) {
  if (value === null || Number.isNaN(value)) return '//';
  const rounded = Math.round(value);
  const sign = rounded < 0 ? 'M' : '';
  const abs = Math.abs(rounded).toString().padStart(2, '0');
  return `${sign}${abs}`;
}

function formatWind(nddff) {
  if (!nddff) return '///KT';
  if (nddff.ff === 0) return '00000KT';
  const dir = (nddff.dd * 10).toString().padStart(3, '0');
  const spd = nddff.ff.toString().padStart(2, '0');
  return `${dir}/${spd}KT`;
}

function formatVisibilityKm(irixhvv) {
  if (!irixhvv) return '////';
  const km = visibilityKm(irixhvv.vv);
  if (km === null) return '////';
  if (km >= 10) return `${Math.round(km)}KM`;
  return `${km.toFixed(1)}KM`;
}

function formatQnh(seaLevelPressureHpa) {
  if (seaLevelPressureHpa === null || Number.isNaN(seaLevelPressureHpa)) return 'Q////';
  return `Q${seaLevelPressureHpa.toFixed(1)}`;
}

function synopToAeromet(report, stationName = 'ESTACION', stationAltM = 0) {
  const { section1, section3, section555 } = parseGroups(report);
  const s1 = extractSection1Fields(section1);
  const layers = [
    ...extractCloudLayers(section3, 3),
    ...extractCloudLayers(section555, 555),
    ...s1.cloudLayers8,
  ];
  const cloud = pickAerometCloud(layers);

  const parts = [
    stationName.toUpperCase(),
    formatWind(s1.nddff),
    formatVisibilityKm(s1.irixhvv),
    cloud ? cloud.text : 'SKC',
    `${formatTemp(s1.tempC)}/${formatTemp(s1.dewpointC)}`,
    formatQnh(s1.seaLevelPressureHpa),
  ];

  return {
    aeromet: parts.join(' '),
    fields: { ...s1, cloud, layers },
    raw: report.trim(),
    stationAltM,
  };
}

function parseOgimetCsv(csvText) {
  const lines = csvText.trim().split(/\r?\n/);
  if (lines.length < 2) return [];
  const rows = [];
  for (let i = 1; i < lines.length; i += 1) {
    const line = lines[i];
    const commaIdx = [];
    for (let j = 0; j < line.length; j += 1) {
      if (line[j] === ',') commaIdx.push(j);
    }
    if (commaIdx.length < 6) continue;
    const sixth = commaIdx[5];
    const meta = line.slice(0, sixth).split(',');
    const report = line.slice(sixth + 1);
    if (!report || report.includes('NIL')) continue;
    const wmoId = meta[0];
    rows.push({
      wmoId,
      year: Number(meta[1]),
      month: Number(meta[2]),
      day: Number(meta[3]),
      hour: Number(meta[4]),
      minute: Number(meta[5]),
      report,
      datetimeUtc: new Date(Date.UTC(Number(meta[1]), Number(meta[2]) - 1, Number(meta[3]), Number(meta[4]), Number(meta[5]))),
    });
  }
  return rows.sort((a, b) => b.datetimeUtc - a.datetimeUtc);
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { synopToAeromet, parseOgimetCsv, cloudBaseFeet, visibilityKm };
}
