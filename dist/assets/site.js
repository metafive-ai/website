// Metafive.ai — commitment chain calculator + click-to-load YouTube
(function () {
  "use strict";
  var root = document.documentElement;
  root.classList.add("js");
  var lang = root.lang === "en" ? "en" : "fr";
  var MONTH_MIN = 30 * 24 * 60;   // 43 200
  var YEAR_MIN = 365 * 24 * 60;   // 525 600

  function pct(x) {
    var digits = x >= 99.995 ? 4 : 3;
    var s = x.toFixed(digits).replace(/0+$/, "").replace(/\.$/, "");
    if (lang === "fr") s = s.replace(".", ",");
    return s + (lang === "fr" ? " %" : "%");
  }
  // a required level is rounded up, never down
  function pctUp(x) {
    var digits = x >= 99.995 ? 4 : 3, f = Math.pow(10, digits);
    return pct(Math.ceil(x * f - 1e-9) / f);
  }
  function dur(min) {
    if (min < 60) {
      var m = min < 10 ? min.toFixed(1) : Math.round(min).toString();
      if (lang === "fr") m = m.replace(".", ",");
      return m + " min";
    }
    var h = Math.floor(min / 60), r = Math.round(min - h * 60);
    if (r === 60) { h += 1; r = 0; }
    return h + " h " + (r < 10 ? "0" : "") + r;
  }
  function compute(sla) {
    var budgetSla = 1 - sla / 100;          // e.g. 0.001
    var slo = 100 - budgetSla * 50;          // keep 50 % margin of the error budget
    var budgetSlo = 1 - slo / 100;
    var link = pctUp(Math.pow(slo / 100, 1 / 4) * 100);  // 3 OLA + 1 UC in series
    return {
      sla: pct(sla),
      slo: pct(slo),
      budget: dur(budgetSlo * MONTH_MIN),
      budgetYear: dur(budgetSlo * YEAR_MIN),
      budgetSla: dur(budgetSla * MONTH_MIN),
      link: link
    };
  }

  var panel = document.querySelector("[data-panel]");
  if (panel) {
    var t = panel.dataset;
    function set(k, html) {
      var els = document.querySelectorAll('[data-v="' + k + '"]');
      for (var i = 0; i < els.length; i++) {
        var el = els[i];
        if (el.innerHTML !== html) { el.innerHTML = html; el.classList.remove("flash"); void el.offsetWidth; el.classList.add("flash"); }
      }
    }
    function render(sla) {
      var r = compute(sla);
      set("sla", r.sla);
      set("slo", r.slo);
      set("budget", r.budget + "<small>" + t.perMonth + "</small>");
      set("budget_plain", r.budget);
      set("budget_sla", r.budgetSla);
      set("ola", r.link);
      set("uc", r.link);
      set("link", r.link);
      set("sli", "≥ " + r.slo);
      set("cap", "&gt; " + r.slo);
      var y = panel.querySelector("[data-budget-year]");
      if (y) y.textContent = r.budgetYear + " " + t.perYear;
    }
    panel.addEventListener("change", function (e) {
      if (e.target && e.target.name === "sla") render(parseFloat(e.target.value));
    });
    var checked = panel.querySelector('input[name="sla"]:checked');
    if (checked) render(parseFloat(checked.value));
  }

  // YouTube facade: nothing is loaded from YouTube until the visitor clicks.
  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest("[data-yt]");
    if (!b) return;
    var id = b.getAttribute("data-yt");
    var f = document.createElement("iframe");
    f.src = "https://www.youtube-nocookie.com/embed/" + encodeURIComponent(id) + "?autoplay=1&rel=0";
    f.title = b.getAttribute("data-title") || "YouTube";
    f.allow = "accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture";
    f.allowFullscreen = true;
    b.parentNode.replaceChild(f, b);
  });
})();
