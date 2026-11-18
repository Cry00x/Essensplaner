/* Gerichte-Bilder: Es werden keine externen Fotos geladen (App muss offline laufen). Stattdessen erzeugt
 * dieses Modul pro Rezept eine appetitliche SVG-Illustration (Teller, Zutatenfarben, Dampf, Emoji).
 * Eigene Rezepte können ein eigenes Foto (als Data-URL, lokal gespeichert) bekommen. */
(function (g) {
  'use strict';
  const PALETTE = {
    haehnchen: ['#f6c177', '#e8a04c'], hack: ['#d98a63', '#b8603c'], schwein: ['#e7b08b', '#c9855c'], rind: ['#c97b63', '#9c4c3a'],
    kartoffel: ['#f3d98a', '#d9b24e'], ei: ['#fbe38a', '#f2b84b'], gemuese: ['#9fd08a', '#5fa354'], huelsen: ['#e0a86d', '#b9763a'],
    pizza: ['#f4b183', '#d4743f'], kuerbis: ['#f7b267', '#e0872c']
  };
  const CARB = { reis: '#fffdf4', nudel: '#f6dca0', kartoffel: '#f0d37a', brot: '#e9c88f', couscous: '#f1d9a4', huelsen: '#c98a52', keine: null };
  function hash(s) { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
  function rnd(seed) { let a = seed; return () => { a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

  function svg(r) {
    const seed = hash(r.id), R = rnd(seed);
    const [c1, c2] = PALETTE[r.main] || PALETTE.gemuese;
    const carb = CARB[r.carb];
    const bgA = r.veg ? '#e8f4e1' : '#fbeee0', bgB = r.veg ? '#cfe6c4' : '#f4d9bd';
    let blobs = '';
    // Beilage
    if (carb) for (let i = 0; i < 14; i++) {
      const a = R() * 6.28, d = 10 + R() * 40; blobs += `<ellipse cx="${(130 + Math.cos(a) * d - 22).toFixed(1)}" cy="${(88 + Math.sin(a) * d * .7 + 6).toFixed(1)}" rx="${6 + R() * 7}" ry="${4 + R() * 5}" fill="${carb}" stroke="rgba(0,0,0,.08)" stroke-width="1"/>`;
    }
    // Hauptzutat
    for (let i = 0; i < 9; i++) {
      const a = R() * 6.28, d = 6 + R() * 36; blobs += `<circle cx="${(138 + Math.cos(a) * d).toFixed(1)}" cy="${(88 + Math.sin(a) * d * .7).toFixed(1)}" r="${6 + R() * 8}" fill="${R() > .5 ? c1 : c2}" stroke="rgba(0,0,0,.1)" stroke-width="1"/>`;
    }
    // Gemüse-Farbtupfer (Paprika, Möhren, Mais, Grün)
    const veg = ['#e4572e', '#f4a259', '#f6d55c', '#6bbf59', '#d9362b'];
    for (let i = 0; i < 12; i++) {
      const a = R() * 6.28, d = 8 + R() * 48; blobs += `<rect x="${(130 + Math.cos(a) * d).toFixed(1)}" y="${(84 + Math.sin(a) * d * .66).toFixed(1)}" width="${4 + R() * 5}" height="${4 + R() * 5}" rx="2" fill="${veg[Math.floor(R() * veg.length)]}" opacity=".92" transform="rotate(${(R() * 90).toFixed(0)} 130 84)"/>`;
    }
    const steam = [0, 1, 2].map(i => `<path d="M${112 + i * 22} 36 q-6 -10 0 -18 t0 -16" fill="none" stroke="#fff" stroke-opacity=".75" stroke-width="3" stroke-linecap="round"/>`).join('');
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 260 170" role="img" aria-label="${r.name.replace(/"/g, '')}" preserveAspectRatio="xMidYMid slice">
<defs><linearGradient id="b${seed}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${bgA}"/><stop offset="1" stop-color="${bgB}"/></linearGradient>
<radialGradient id="p${seed}" cx=".4" cy=".35"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#e9e4dc"/></radialGradient></defs>
<rect width="260" height="170" fill="url(#b${seed})"/>
<ellipse cx="132" cy="150" rx="82" ry="9" fill="rgba(0,0,0,.14)"/>
<ellipse cx="130" cy="92" rx="84" ry="62" fill="url(#p${seed})" stroke="rgba(0,0,0,.1)"/>
<ellipse cx="130" cy="92" rx="62" ry="44" fill="none" stroke="rgba(0,0,0,.07)" stroke-width="2"/>
${blobs}${steam}</svg>`;
  }

  const cache = {};
  g.Images = {
    /** Gibt eine data:-URL zurück (oder das eigene Foto). */
    src(r) {
      if (r.photo) return r.photo;
      if (!cache[r.id]) cache[r.id] = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg(r));
      return cache[r.id];
    },
    /** Verkleinert ein Foto auf max. 640 px und liefert eine JPEG-Data-URL. */
    async fromFile(file) {
      const bmp = await new Promise((res, rej) => { const u = URL.createObjectURL(file); const im = new Image(); im.onload = () => { URL.revokeObjectURL(u); res(im); }; im.onerror = rej; im.src = u; });
      const k = Math.min(1, 640 / Math.max(bmp.width, bmp.height));
      const c = document.createElement('canvas'); c.width = Math.round(bmp.width * k); c.height = Math.round(bmp.height * k);
      c.getContext('2d').drawImage(bmp, 0, 0, c.width, c.height);
      return c.toDataURL('image/jpeg', .78);
    }
  };
})(typeof globalThis !== 'undefined' ? globalThis : self);
