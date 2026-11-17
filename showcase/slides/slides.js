// Deck controller: keyboard/click navigation, hash deep links, stage scaling, section rail.
// Keys: Right/PageDown/Space/Enter = next, Left/PageUp/Backspace = prev,
// Home/End = first/last, F = fullscreen. Slides marked data-skip are removed.
// Each content slide carries data-part="1".."5"; the rail marks that part as current
// and the earlier parts as done. Key slides (.key) slide the rail out of view.
(function () {
  "use strict";
  var stage = document.querySelector(".stage");
  Array.prototype.forEach.call(document.querySelectorAll(".slide[data-skip]"), function (el) {
    el.remove();
  });
  var slides = Array.prototype.slice.call(document.querySelectorAll(".slide"));
  var parts = Array.prototype.slice.call(document.querySelectorAll(".rail li"));
  var counter = document.querySelector("[data-counter]");
  var index = 0;

  function pad(n) {
    return String(n).padStart(2, "0");
  }

  function fit() {
    var scale = Math.min(window.innerWidth / 1600, window.innerHeight / 900);
    stage.style.transform = "scale(" + scale + ")";
  }

  function markRail(slide) {
    var part = parseInt(slide.getAttribute("data-part") || "0", 10);
    parts.forEach(function (li, n) {
      li.classList.toggle("is-current", n + 1 === part);
      li.classList.toggle("is-done", n + 1 < part);
    });
  }

  function show(next) {
    index = Math.max(0, Math.min(slides.length - 1, next));
    slides.forEach(function (el, n) {
      el.classList.toggle("is-active", n === index);
    });
    var slide = slides[index];
    stage.classList.toggle("on-key", slide.classList.contains("key"));
    markRail(slide);
    counter.textContent = pad(index + 1) + " / " + pad(slides.length);
    try {
      history.replaceState(null, "", "#" + (index + 1));
    } catch (err) {
      /* file:// in some browsers refuses replaceState; navigation still works */
    }
  }

  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(function () {});
    } else {
      document.exitFullscreen();
    }
  }

  document.addEventListener("keydown", function (event) {
    var key = event.key;
    if (key === "ArrowRight" || key === "PageDown" || key === " " || key === "Enter") {
      event.preventDefault();
      show(index + 1);
    } else if (key === "ArrowLeft" || key === "PageUp" || key === "Backspace") {
      event.preventDefault();
      show(index - 1);
    } else if (key === "Home") {
      show(0);
    } else if (key === "End") {
      show(slides.length - 1);
    } else if (key === "f" || key === "F") {
      toggleFullscreen();
    }
  });

  stage.addEventListener("click", function (event) {
    var rect = stage.getBoundingClientRect();
    show(event.clientX - rect.left > rect.width / 2 ? index + 1 : index - 1);
  });

  window.addEventListener("resize", fit);
  var start = parseInt((location.hash || "#1").slice(1), 10);
  fit();
  show(isNaN(start) ? 0 : start - 1);
})();
