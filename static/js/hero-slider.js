// Hero slider strony głównej. Vanilla, bez zależności. Aktywuje się tylko gdy na stronie jest #heroSlider.
(function () {
  "use strict";
  var root = document.getElementById("heroSlider");
  if (!root) return;

  var slides = root.querySelectorAll(".slide");
  var dots = document.querySelectorAll(".dot");
  var counter = document.getElementById("curSlide");
  var progress = document.querySelector(".slide-progress-bar");
  var pauseBtn = document.getElementById("pauseBtn");
  if (!slides.length) return;

  var idx = 0, timer = null, paused = false;
  var DURATION = 6000;

  function go(n, manual) {
    idx = (n + slides.length) % slides.length;
    slides.forEach(function (s, i) { s.classList.toggle("is-active", i === idx); });
    dots.forEach(function (d, i) { d.classList.toggle("is-active", i === idx); });
    if (counter) counter.textContent = String(idx + 1).padStart(2, "0");
    if (progress) {
      progress.style.animation = "none";
      void progress.offsetHeight; // reflow
      if (!paused) progress.style.animation = "slideProgress " + DURATION + "ms linear forwards";
    }
    if (manual) restart();
  }
  function tick() { go(idx + 1); }
  function start() { timer = setInterval(tick, DURATION); }
  function stop() { clearInterval(timer); }
  function restart() { stop(); if (!paused) start(); }

  document.querySelectorAll("[data-dir]").forEach(function (b) {
    b.addEventListener("click", function () { go(idx + parseInt(b.dataset.dir, 10), true); });
  });
  dots.forEach(function (d) {
    d.addEventListener("click", function () { go(parseInt(d.dataset.go, 10), true); });
  });
  if (pauseBtn) {
    pauseBtn.addEventListener("click", function () {
      paused = !paused;
      pauseBtn.classList.toggle("is-paused", paused);
      pauseBtn.innerHTML = paused
        ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="6 4 20 12 6 20"></polygon></svg>'
        : '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>';
      if (paused) { stop(); if (progress) progress.style.animationPlayState = "paused"; }
      else { restart(); if (progress) progress.style.animationPlayState = "running"; }
    });
  }

  go(0);
  start();
})();
