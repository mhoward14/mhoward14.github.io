/* Shared page script: frame guard, theme, sidebar state, and email links.
   Loaded in <head> without defer so the saved theme applies before
   first paint (no flash). The "theme" key is shared with the cyber
   portfolio on the same origin, so the choice carries between sites. */
(function () {
  var root = document.documentElement;

  /* Clickjacking guard. GitHub Pages can't send X-Frame-Options or a
     frame-ancestors header (browsers ignore frame-ancestors in a <meta>
     CSP), so when another site frames this page it is hidden (see
     html.is-framed in style.css) and we try to take over the top window. */
  var framed;
  try {
    framed = window.self !== window.top;
  } catch (e) {
    framed = true;
  }
  if (framed) {
    root.classList.add('is-framed');
    try {
      window.top.location.href = window.location.href;
    } catch (e) {
      /* blocked by the browser or a sandbox: the page stays hidden */
    }
  }

  /* The contact address is assembled only when a visitor reaches for an
     email link, so it never appears in the page source for harvesters. */
  function emailHref() {
    return 'mailto:' + ['mhoward', '14'].join('') + String.fromCharCode(64) + ['icloud', 'com'].join('.');
  }

  function storedTheme() {
    try {
      return localStorage.getItem('theme');
    } catch (e) {
      return null;
    }
  }

  var saved = storedTheme();
  var prefersLight = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches;
  root.setAttribute('data-theme', saved === 'light' || saved === 'dark' ? saved : prefersLight ? 'light' : 'dark');

  function save(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch (e) {
      /* storage unavailable: the choice lasts for this page only */
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    var links = document.querySelectorAll('a[data-email]');
    function reveal() {
      this.setAttribute('href', emailHref());
    }
    for (var i = 0; i < links.length; i++) {
      ['pointerenter', 'touchstart', 'focus', 'click'].forEach(function (type) {
        links[i].addEventListener(type, reveal, { passive: true });
      });
    }

    var toggle = document.getElementById('themeToggle');
    if (toggle) {
      toggle.addEventListener('click', function () {
        var next = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
        root.setAttribute('data-theme', next);
        save('theme', next);
      });
    }

    var sidebar = document.getElementById('sidebar');
    var collapse = document.getElementById('sidebarCollapse');
    function setCollapsed(collapsed) {
      sidebar.classList.toggle('is-collapsed', collapsed);
      document.body.classList.toggle('sidebar-collapsed', collapsed);
      collapse.setAttribute('aria-expanded', String(!collapsed));
    }
    if (sidebar && collapse) {
      var wasCollapsed = false;
      try {
        wasCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
      } catch (e) {
        /* default expanded */
      }
      setCollapsed(wasCollapsed);
      collapse.addEventListener('click', function () {
        var next = !sidebar.classList.contains('is-collapsed');
        setCollapsed(next);
        save('sidebar-collapsed', String(next));
      });
    }
  });
})();
