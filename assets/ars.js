/* Quick Web Studio: цены в песо по официальному курсу продажи BNA (dolarapi.com).
   DOM не меняет: ставит data-ars на элементы цены, текст выводит CSS ::after. */
(function () {
  var KEY = 'qwArs', TTL = 12 * 3600 * 1000;
  var lang = (document.documentElement.lang || 'es').slice(0, 2);
  var LOC = { es: 'es-AR', ru: 'ru-RU', en: 'en-US' }[lang] || 'es-AR';
  var NOTE = { es: 'tipo de cambio BNA', ru: 'по курсу BNA', en: 'BNA rate' }[lang] || 'BNA';
  var rate = 0;

  function css() {
    var s = document.createElement('style');
    s.textContent =
      '[data-ars]::after{content:attr(data-ars);display:block;font-size:13px;font-weight:400;line-height:1.3;letter-spacing:0;color:#6B7280;margin-top:4px;white-space:nowrap}' +
      '.qw-spp[data-ars]{flex-wrap:wrap}.qw-spp[data-ars]::after{flex-basis:100%;margin-top:6px}' +
      'html[data-ars-on] .qw-spm{height:40px}.qw-spm[data-ars]::after{content:attr(data-ars-s);font-size:12px;margin-top:2px}' +
      '.qw-spa b[data-ars]{text-align:right}.qw-spa b[data-ars]::after{font-size:12px;margin-top:2px}' +
      '@media (max-width:760px){[data-ars-grid]{grid-template-columns:minmax(0,1fr)!important}.qw-spa b[data-ars]::after{content:attr(data-ars-s)}}';
    document.head.appendChild(s);
  }
  function fmt(n) {
    var r = Math.round(n / 1000) * 1000;
    try { return r.toLocaleString(LOC); } catch (e) { return String(r); }
  }
  function usd(t) {
    if (!t || t.indexOf('%') >= 0) return 0;
    var m = t.match(/\d[\d.,\s  ]*/);
    return m ? parseInt(m[0].replace(/\D/g, ''), 10) || 0 : 0;
  }
  function tick() {
    if (!rate) return;
    var els = document.querySelectorAll('.qw-spp, .qw-spm, .qw-spa b');
    for (var i = 0; i < els.length; i++) {
      var e = els[i];
      var src = e.classList.contains('qw-spp') ? (e.querySelector('span') || e).textContent : e.textContent;
      var v = usd(src), want = v > 0 ? '≈ ' + fmt(v * rate) + ' ARS · ' + NOTE : '';
      if ((e.getAttribute('data-ars') || '') !== want) {
        if (want) e.setAttribute('data-ars', want); else e.removeAttribute('data-ars');
      }
      if (want && (e.tagName === 'B' || e.classList.contains('qw-spm'))) {
        var sh = '\u2248 ' + fmt(v * rate) + ' ARS';
        if (e.getAttribute('data-ars-s') !== sh) e.setAttribute('data-ars-s', sh);
        var g = e.tagName === 'B' && e.parentElement && e.parentElement.parentElement;
        if (g && !g.hasAttribute('data-ars-grid')) g.setAttribute('data-ars-grid', '');
      }
    }
  }
  function start(r) { rate = r; document.documentElement.setAttribute('data-ars-on', ''); css(); tick(); setInterval(tick, 1000); }

  try {
    var c = JSON.parse(localStorage.getItem(KEY) || 'null');
    if (c && c.v > 0 && Date.now() - c.t < TTL) { start(c.v); return; }
  } catch (e) {}
  fetch('https://dolarapi.com/v1/dolares/oficial')
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (j) {
      var v = j && +j.venta;
      if (!(v > 0)) return;
      try { localStorage.setItem(KEY, JSON.stringify({ v: v, t: Date.now() })); } catch (e) {}
      start(v);
    })
    .catch(function () {});
})();
