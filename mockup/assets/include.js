// Tiny include helper. Anchors path resolution to its own <script> tag's URL,
// so it works regardless of how deeply the host serves the project.
(function () {
  // Capture synchronously — document.currentScript is null inside async fn.
  const SCRIPT_EL = document.currentScript || document.querySelector('script[src*="include.js"]');
  const SCRIPT_SRC = SCRIPT_EL ? SCRIPT_EL.src : '';
  // Everything before /assets/include.js is the project root URL.
  const ROOT = SCRIPT_SRC.replace(/assets\/include\.js.*$/, '');

  (async function () {
    const includes = document.querySelectorAll('[data-include]');
    await Promise.all([...includes].map(async (el) => {
      const name = el.getAttribute('data-include');
      try {
        const res = await fetch(`${ROOT}assets/${name}.html`);
        if (!res.ok) throw new Error('not found: ' + res.status);
        let html = await res.text();
        // Rewrite relative hrefs/srcs in the include to absolute root-anchored URLs.
        html = html.replace(/(href|src)="([^"#][^"]*)"/g, (m, attr, p) => {
          if (/^(https?:|mailto:|tel:|data:|#|\/)/.test(p)) return m;
          // Drop any leading ../ that authors might have used (root is now explicit)
          const cleaned = p.replace(/^(\.\.\/)+/, '');
          return `${attr}="${ROOT}${cleaned}"`;
        });
        el.outerHTML = html;
      } catch (err) {
        console.warn('Include failed:', name, err);
      }
    }));

    // Active nav highlight
    const page = document.body.getAttribute('data-page');
    if (page) {
      document.querySelectorAll(`[data-nav="${page}"]`).forEach(a => a.classList.add('active'));
    }

    // Year stamp
    const yr = document.getElementById('year');
    if (yr) yr.textContent = new Date().getFullYear();

    // Burger toggle (mobile)
    document.addEventListener('click', (e) => {
      if (e.target.closest('.burger')) {
        document.body.classList.toggle('menu-open');
      }
    });
  })();
})();
