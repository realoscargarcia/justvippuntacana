/* Just VIP Punta Cana — site behaviour */
(function () {
  "use strict";

  /* ---------------------------------------------------------------
     CONFIG — replace with the real business contact details
     --------------------------------------------------------------- */
  var CONFIG = {
    phoneDisplay: "+1 809 000 0000",
    phoneDial: "+18090000000",      // tel: link
    whatsapp: "18090000000"         // wa.me number, digits only
  };

  var DICT = window.JVP_I18N || { en: {}, es: {} };
  var lang = "en";

  /* ---------------- language ---------------- */
  function detectLang() {
    /* Blog articles exist once per language: the page fixes its own. */
    var lock = document.documentElement.getAttribute("data-lang-lock");
    if (lock && DICT[lock]) return lock;
    var q = new URLSearchParams(location.search).get("lang");
    if (q && DICT[q]) return q;
    try {
      var saved = localStorage.getItem("jvp-lang");
      if (saved && DICT[saved]) return saved;
    } catch (e) { /* storage unavailable */ }
    return (navigator.language || "en").toLowerCase().indexOf("es") === 0 ? "es" : "en";
  }

  function t(key) {
    var d = DICT[lang] || {};
    return Object.prototype.hasOwnProperty.call(d, key) ? d[key] : null;
  }

  function applyLang(next) {
    lang = DICT[next] ? next : "en";
    document.documentElement.lang = lang;

    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var value = t(el.getAttribute("data-i18n"));
      if (value === null) return;
      if (el.tagName === "META") el.setAttribute("content", value);
      else if (el.tagName === "TITLE") document.title = value;
      else el.textContent = value;
    });

    document.querySelectorAll("[data-i18n-placeholder]").forEach(function (el) {
      var value = t(el.getAttribute("data-i18n-placeholder"));
      if (value !== null) el.setAttribute("placeholder", value);
    });

    document.querySelectorAll(".lang-switch button").forEach(function (btn) {
      btn.setAttribute("aria-pressed", String(btn.dataset.lang === lang));
    });

    /* Links with a Spanish counterpart (the blog) follow the language. */
    document.querySelectorAll("[data-href-es]").forEach(function (el) {
      if (!el.hasAttribute("data-href-en")) el.setAttribute("data-href-en", el.getAttribute("href"));
      el.setAttribute("href", el.getAttribute(lang === "es" ? "data-href-es" : "data-href-en"));
    });

    refreshWhatsAppLinks();
    if (document.getElementById("fleet-title")) fleetHeading(tripActive());

    try { localStorage.setItem("jvp-lang", lang); } catch (e) { /* ignore */ }
  }

  /* ---------------- contact links ---------------- */
  /* Vehicle pages carry data-veh-key so the greeting names the car. */
  function greeting() {
    var key = document.body.getAttribute("data-veh-key");
    var name = key ? t(key) : null;
    if (name) return (t("wa.vehicle") || "") + " " + name + ".";
    return t("wa.greeting") || "";
  }

  function waHref(message) {
    return "https://wa.me/" + CONFIG.whatsapp + "?text=" + encodeURIComponent(message || greeting());
  }

  function refreshWhatsAppLinks() {
    document.querySelectorAll("[data-wa]").forEach(function (el) {
      el.href = waHref();
      el.target = "_blank";
      el.rel = "noopener";
    });
  }

  function initContacts() {
    document.querySelectorAll("[data-tel]").forEach(function (el) {
      el.href = "tel:" + CONFIG.phoneDial;
    });
    document.querySelectorAll("[data-phone]").forEach(function (el) {
      el.textContent = CONFIG.phoneDisplay;
    });
    refreshWhatsAppLinks();
  }

  /* ---------------- nav ---------------- */
  function initNav() {
    var toggle = document.querySelector(".nav-toggle");
    if (!toggle) return;
    toggle.addEventListener("click", function () {
      var open = document.body.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    document.querySelectorAll("#nav a").forEach(function (a) {
      a.addEventListener("click", function () {
        document.body.classList.remove("nav-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* ---------------- reveal on scroll ---------------- */
  function initReveal() {
    var items = document.querySelectorAll(".reveal");
    if (!("IntersectionObserver" in window)) {
      items.forEach(function (el) { el.classList.add("is-visible"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        io.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -10% 0px", threshold: 0.08 });
    items.forEach(function (el) { io.observe(el); });
  }

  /* ---------------- quote form -> WhatsApp ---------------- */
  function initForm() {
    var form = document.getElementById("quote-form");
    if (!form) return;
    var status = document.getElementById("form-status");

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var data = new FormData(form);
      var name = (data.get("name") || "").toString().trim();
      var phone = (data.get("phone") || "").toString().trim();
      var date = (data.get("date") || "").toString().trim();

      if (!name || !phone || !date) {
        status.textContent = t("form.error") || "";
        return;
      }

      var lines = [
        greeting(),
        "",
        t("form.name") + ": " + name,
        t("form.phone") + ": " + (data.get("code") || "") + " " + phone,
        t("form.date") + ": " + date,
        t("form.package") + ": " + (data.get("package") || "")
      ];
      var trip = window.JVP_TRIP;
      if (trip && trip.to) lines.push(t("book.dropoff") + ": " + trip.to);
      if (trip && trip.time) lines.push(t("book.time") + ": " + trip.time);
      if (trip && trip.pax) lines.push(t("book.pax") + ": " + trip.pax);

      var pickup = (data.get("pickup") || "").toString().trim();
      var notes = (data.get("notes") || "").toString().trim();
      if (pickup) lines.push(t("form.pickup") + ": " + pickup);
      if (notes) lines.push(t("form.notes") + ": " + notes);

      status.textContent = t("form.sending") || "";
      window.open(waHref(lines.join("\n")), "_blank", "noopener");
    });
  }

  /* ---------------- vehicle gallery ---------------- */
  function initGallery() {
    var gallery = document.getElementById("gallery");
    if (!gallery) return;

    var slides = gallery.querySelectorAll(".slide");
    var thumbs = gallery.querySelectorAll("[data-gallery-thumb]");
    var counter = gallery.querySelector("[data-gallery-current]");
    var index = 0;

    function show(next) {
      index = (next + slides.length) % slides.length;
      slides.forEach(function (slide, i) {
        slide.setAttribute("data-active", String(i === index));
      });
      thumbs.forEach(function (thumb, i) {
        if (i === index) thumb.setAttribute("aria-current", "true");
        else thumb.removeAttribute("aria-current");
      });
      if (counter) counter.textContent = String(index + 1);
    }

    gallery.querySelector("[data-gallery-prev]").addEventListener("click", function () { show(index - 1); });
    gallery.querySelector("[data-gallery-next]").addEventListener("click", function () { show(index + 1); });
    thumbs.forEach(function (thumb, i) {
      thumb.addEventListener("click", function () { show(i); });
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "ArrowLeft") show(index - 1);
      if (event.key === "ArrowRight") show(index + 1);
    });
  }

  /* ---------------- trip search ---------------- */
  var TRIP_KEY = "jvp-trip";

  function readTrip() {
    try {
      return JSON.parse(sessionStorage.getItem(TRIP_KEY) || "null");
    } catch (e) { return null; }
  }

  function saveTrip(trip) {
    try { sessionStorage.setItem(TRIP_KEY, JSON.stringify(trip)); } catch (e) { /* ignore */ }
  }

  function formatTrip(trip) {
    var parts = [];
    if (trip.date) parts.push(trip.date);
    if (trip.time) parts.push(trip.time);
    parts.push(trip.pax + " " + (t("book.paxLabel") || ""));
    return parts.join(" · ");
  }

  /* The fleet heading becomes a results heading while a search is active. */
  function fleetHeading(active) {
    var title = document.getElementById("fleet-title");
    var lede = document.getElementById("fleet-lede");
    if (!title || !lede) return;
    title.textContent = t(active ? "book.results" : "fleet.title") || title.textContent;
    lede.textContent = t(active ? "book.resultsLede" : "fleet.lede") || lede.textContent;
  }

  function tripActive() {
    var bar = document.getElementById("trip-bar");
    return !!(bar && !bar.hidden);
  }

  /* Show only the vehicles that seat the party, and summarise the trip. */
  function applyTrip(trip) {
    var bar = document.getElementById("trip-bar");
    if (!bar) return;

    document.getElementById("trip-from").textContent = trip.from;
    document.getElementById("trip-to").textContent = trip.to;
    document.getElementById("trip-meta").textContent = formatTrip(trip);
    bar.hidden = false;

    var fits = 0;
    document.querySelectorAll(".fleet-grid .card").forEach(function (card) {
      var seats = parseInt(card.getAttribute("data-seats"), 10) || 0;
      var ok = seats >= trip.pax;
      card.hidden = !ok;
      if (ok) fits++;
    });

    var empty = document.getElementById("trip-empty");
    if (empty) empty.hidden = fits > 0;

    fleetHeading(true);
  }

  function clearTrip() {
    var bar = document.getElementById("trip-bar");
    if (bar) bar.hidden = true;
    var empty = document.getElementById("trip-empty");
    if (empty) empty.hidden = true;
    document.querySelectorAll(".fleet-grid .card").forEach(function (card) { card.hidden = false; });
    fleetHeading(false);
    try { sessionStorage.removeItem(TRIP_KEY); } catch (e) { /* ignore */ }
  }

  function initBooking() {
    var form = document.getElementById("booking");
    if (!form) return;

    var dateField = document.getElementById("bk-date");
    if (dateField && !dateField.value) {
      dateField.value = new Date().toISOString().slice(0, 10);
      dateField.min = dateField.value;
    }

    var error = document.getElementById("bk-error");

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var trip = {
        from: document.getElementById("bk-from").value.trim(),
        to: document.getElementById("bk-to").value.trim(),
        date: document.getElementById("bk-date").value,
        time: document.getElementById("bk-time").value,
        pax: parseInt(document.getElementById("bk-pax").value, 10) || 1
      };

      if (!trip.from || !trip.to || !trip.date) {
        error.textContent = t("book.error") || "";
        return;
      }
      error.textContent = "";

      saveTrip(trip);
      applyTrip(trip);
      document.getElementById("fleet").scrollIntoView({ behavior: "smooth", block: "start" });
    });

    var edit = document.getElementById("trip-edit");
    if (edit) {
      edit.addEventListener("click", function () {
        clearTrip();
        window.scrollTo({ top: 0, behavior: "smooth" });
        document.getElementById("bk-from").focus({ preventScroll: true });
      });
    }

    var stored = readTrip();
    if (stored) {
      document.getElementById("bk-from").value = stored.from;
      document.getElementById("bk-to").value = stored.to;
      if (stored.date) document.getElementById("bk-date").value = stored.date;
      if (stored.time) document.getElementById("bk-time").value = stored.time;
      document.getElementById("bk-pax").value = String(stored.pax);
      applyTrip(stored);
    }
  }

  /* Carry the trip into the quote form on a vehicle page. */
  function prefillFromTrip() {
    var trip = readTrip();
    if (!trip) return;
    var pickup = document.getElementById("f-pickup");
    var date = document.getElementById("f-date");
    if (pickup && !pickup.value) pickup.value = trip.from;
    if (date && !date.value) date.value = trip.date;
    window.JVP_TRIP = trip;
  }

  /* ---------------- boot ---------------- */
  document.addEventListener("DOMContentLoaded", function () {
    var yearEl = document.getElementById("year");
    if (yearEl) yearEl.textContent = String(new Date().getFullYear());

    initContacts();
    initNav();
    initReveal();
    initGallery();
    initForm();
    initBooking();
    prefillFromTrip();

    applyLang(detectLang());

    document.querySelectorAll(".lang-switch button").forEach(function (btn) {
      btn.addEventListener("click", function () {
        /* On a blog article the other language is a separate page. */
        if (btn.dataset.href && btn.dataset.lang !== lang) {
          try { localStorage.setItem("jvp-lang", btn.dataset.lang); } catch (e) { /* ignore */ }
          location.href = btn.dataset.href;
          return;
        }
        applyLang(btn.dataset.lang);
      });
    });
  });
})();
