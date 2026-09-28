/* Shared page script: theme and sidebar state.
   Loaded in <head> without defer so the saved theme applies before
   first paint (no flash). The "theme" key is shared with the cyber
   portfolio on the same origin, so the choice carries between sites. */
(function () {
  var root = document.documentElement;

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
