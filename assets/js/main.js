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

    refreshWhatsAppLinks();

    try { localStorage.setItem("jvp-lang", lang); } catch (e) { /* ignore */ }
  }

  /* ---------------- contact links ---------------- */
  function waHref(message) {
    return "https://wa.me/" + CONFIG.whatsapp + "?text=" + encodeURIComponent(message || t("wa.greeting") || "");
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
        t("wa.greeting"),
        "",
        t("form.name") + ": " + name,
        t("form.phone") + ": " + (data.get("code") || "") + " " + phone,
        t("form.date") + ": " + date,
        t("form.package") + ": " + (data.get("package") || "")
      ];
      var pickup = (data.get("pickup") || "").toString().trim();
      var notes = (data.get("notes") || "").toString().trim();
      if (pickup) lines.push(t("form.pickup") + ": " + pickup);
      if (notes) lines.push(t("form.notes") + ": " + notes);

      status.textContent = t("form.sending") || "";
      window.open(waHref(lines.join("\n")), "_blank", "noopener");
    });
  }

  /* ---------------- boot ---------------- */
  document.addEventListener("DOMContentLoaded", function () {
    var yearEl = document.getElementById("year");
    if (yearEl) yearEl.textContent = String(new Date().getFullYear());

    initContacts();
    initNav();
    initReveal();
    initForm();

    applyLang(detectLang());

    document.querySelectorAll(".lang-switch button").forEach(function (btn) {
      btn.addEventListener("click", function () { applyLang(btn.dataset.lang); });
    });
  });
})();
