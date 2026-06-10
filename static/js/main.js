// Nawigacja mobilna + zgoda na cookies + warunkowy GA4. Vanilla, bez zależności.
(function () {
  "use strict";

  // --- Burger (menu mobilne) ---
  document.addEventListener("click", function (e) {
    if (e.target.closest(".burger")) {
      document.body.classList.toggle("menu-open");
    }
  });

  // --- Cookie consent + GA4 ---
  var STORAGE_KEY = "kg_cookie_consent"; // "accepted" | "rejected"
  var banner = document.getElementById("cookieBanner");

  function loadGA(gaId) {
    if (!gaId || window.__gaLoaded) return;
    window.__gaLoaded = true;
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + gaId;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("js", new Date());
    window.gtag("config", gaId);
  }

  if (banner) {
    var gaId = banner.getAttribute("data-ga-id");
    var consent = localStorage.getItem(STORAGE_KEY);
    if (consent === "accepted") {
      loadGA(gaId);
    } else if (consent !== "rejected") {
      banner.hidden = false;
    }
    banner.addEventListener("click", function (e) {
      var action = e.target.getAttribute("data-cookie");
      if (!action) return;
      if (action === "accept") {
        localStorage.setItem(STORAGE_KEY, "accepted");
        loadGA(gaId);
      } else {
        localStorage.setItem(STORAGE_KEY, "rejected");
      }
      banner.hidden = true;
    });
  }
})();
