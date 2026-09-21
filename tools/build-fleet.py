#!/usr/bin/env python3
"""Generate the vehicle detail pages under fleet/.

The SVG sprite, header and footer are shared with index.html, so the three
pages never drift apart. Edit this file (or the sprite in index.html) and run:

    python3 tools/build-fleet.py
"""

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

VEHICLES = [
    {
        "slug": "executive-sedan",
        "key": "c1",
        "symbol": "i-sedan",
        "cls": "veh.cls.sedan",
        "en": "Executive Sedan",
        "es": "Sedán Ejecutivo",
        "prices": ("75", "180", "260", "380"),
    },
    {
        "slug": "premium-suv",
        "key": "c2",
        "symbol": "i-suv",
        "cls": "veh.cls.suv",
        "en": "Cadillac Escalade 2023",
        "es": "Cadillac Escalade 2023",
        "prices": ("110", "240", "340", "490"),
        "images": [
            ("escalade-1-exterior", "veh.g1", "Cadillac Escalade 2023 exterior"),
            ("escalade-2-interior", "veh.g2", "Cadillac Escalade 2023 front cabin"),
            ("escalade-3-rear", "veh.g4", "Cadillac Escalade 2023 rear cabin"),
            ("escalade-4-cockpit", "veh.g5", "Cadillac Escalade 2023 driver cockpit"),
            ("escalade-5-detail", "veh.g3", "Cadillac Escalade 2023 centre console"),
        ],
    },
    {
        "slug": "vip-van",
        "key": "c3",
        "symbol": "i-van",
        "cls": "veh.cls.van",
        "en": "VIP Van",
        "es": "Van VIP",
        "prices": ("140", "290", "410", "590"),
    },
]


def sprite() -> str:
    """Pull the inline SVG sprite out of index.html so it stays single-source."""
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    match = re.search(r"(<svg width=\"0\" height=\"0\".*?</svg>)", html, re.S)
    if not match:
        raise SystemExit("sprite not found in index.html")
    return match.group(1)


PLACEHOLDER_SLIDES = [
    ("slide--a", "{symbol}", "veh.g1", "Exterior"),
    ("slide--b", "i-seat", "veh.g2", "Interior"),
    ("slide--c", "i-detail", "veh.g3", "Detail"),
]


def gallery(v: dict) -> tuple:
    """Return (slides, thumbs, total) — real photography when the vehicle has it."""
    images = v.get("images")
    if not images:
        slides, thumbs = [], []
        for i, (cls, sym, key, label) in enumerate(PLACEHOLDER_SLIDES):
            sym = sym.format(symbol=v["symbol"])
            active = ' data-active="true"' if i == 0 else ""
            current = ' aria-current="true"' if i == 0 else ""
            slides.append(f"""          <div class="slide {cls}"{active}>
            <svg viewBox="0 0 120 54" aria-hidden="true"><use href="#{sym}"></use></svg>
            <span class="slide-label" data-i18n="{key}">{label}</span>
          </div>""")
            thumbs.append(f"""          <button class="thumb {cls}" type="button" data-gallery-thumb="{i}"{current} aria-label="{label}">
            <svg viewBox="0 0 120 54" aria-hidden="true"><use href="#{sym}"></use></svg>
          </button>""")
        return "\n".join(slides), "\n".join(thumbs), len(PLACEHOLDER_SLIDES)

    slides, thumbs = [], []
    for i, (name, key, alt) in enumerate(images):
        active = ' data-active="true"' if i == 0 else ""
        current = ' aria-current="true"' if i == 0 else ""
        loading = "eager" if i == 0 else "lazy"
        slides.append(f"""          <div class="slide slide--photo"{active}>
            <img src="../assets/img/fleet/{name}.jpg" alt="{alt}" loading="{loading}" decoding="async">
            <span class="slide-label" data-i18n="{key}"></span>
          </div>""")
        thumbs.append(f"""          <button class="thumb thumb--photo" type="button" data-gallery-thumb="{i}"{current} aria-label="{alt}">
            <img src="../assets/img/fleet/{name}-thumb.jpg" alt="" loading="lazy" decoding="async">
          </button>""")
    return "\n".join(slides), "\n".join(thumbs), len(images)


def card_media(v: dict, prefix: str = "") -> str:
    """Card thumbnail: a photo when the vehicle has one, else the SVG silhouette."""
    images = v.get("images")
    if images:
        return (f'<img class="veh-photo" src="{prefix}assets/img/fleet/{images[0][0]}-thumb.jpg" '
                f'alt="{images[0][2]}" loading="lazy" decoding="async">')
    return f'<svg class="veh" viewBox="0 0 120 54" aria-hidden="true"><use href="#{v["symbol"]}"></use></svg>'


def other_cards(current: dict) -> str:
    out = []
    for v in VEHICLES:
        if v["slug"] == current["slug"]:
            continue
        out.append(f"""        <article class="card">
          <a href="{v['slug']}.html">
            <div class="card-media">
              {card_media(v, "../")}
            </div>
            <div class="card-body">
              <h3 data-i18n="fleet.{v['key']}.name">{v['en']}</h3>
              <div class="specs">
                <span><svg aria-hidden="true"><use href="#i-users"></use></svg><span data-i18n="fleet.{v['key']}.pax"></span></span>
                <span><svg aria-hidden="true"><use href="#i-case"></use></svg><span data-i18n="fleet.{v['key']}.bags"></span></span>
              </div>
              <p data-i18n="fleet.{v['key']}.text"></p>
              <div class="card-foot">
                <span class="price">${v['prices'][0]} <small data-i18n="fleet.from"></small></span>
                <span class="link-arrow"><span data-i18n="cta.view"></span><svg aria-hidden="true" width="12" height="12"><use href="#i-arrow"></use></svg></span>
              </div>
            </div>
          </a>
        </article>""")
    return "\n".join(out)


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{en_name} with Chauffeur in Punta Cana | Just VIP Punta Cana</title>
<meta name="description" content="Book the {en_name} with a professional chauffeur in Punta Cana. Airport transfers from ${p1} USD, hourly packages, written terms and 24/7 dispatch.">
<link rel="canonical" href="https://justvippuntacana.com/fleet/{slug}.html">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@0,400;0,500;1,400;1,500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/css/styles.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' fill='%230d0d0e'/><text x='50' y='68' font-size='54' font-family='Georgia' font-style='italic' fill='%23c8a86b' text-anchor='middle'>V</text></svg>">
</head>
<body data-veh-key="fleet.{key}.name">

{sprite}

<header class="site-header">
  <div class="wrap">
    <a class="brand" href="../index.html">
      <strong>JUST VIP</strong>
      <span data-i18n="brand.tagline">Punta Cana · Luxury Chauffeur</span>
    </a>

    <nav class="nav" id="nav">
      <a href="../index.html#services" data-i18n="nav.services">Services</a>
      <a href="../index.html#fleet" data-i18n="nav.fleet">Fleet</a>
      <a href="../index.html#how" data-i18n="nav.how">How it works</a>
      <a href="../index.html#why" data-i18n="nav.why">About</a>
      <a href="#quote" data-i18n="nav.contact">Contact</a>
    </nav>

    <div class="header-actions">
      <div class="lang-switch" role="group" aria-label="Language / Idioma">
        <button type="button" data-lang="en" aria-pressed="true">EN</button>
        <button type="button" data-lang="es" aria-pressed="false">ES</button>
      </div>
      <a class="btn btn--gold" data-wa href="#quote">
        <svg aria-hidden="true"><use href="#i-wa"></use></svg>
        <span data-i18n="cta.book">Book driver</span>
      </a>
      <button class="nav-toggle" type="button" aria-label="Menu" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
</header>

<main class="page">
  <div class="wrap">
    <nav class="breadcrumb" aria-label="Breadcrumb">
      <a href="../index.html" data-i18n="veh.home">Home</a>
      <span class="sep">/</span>
      <a href="../index.html#fleet" data-i18n="veh.fleet">Fleet</a>
      <span class="sep">/</span>
      <span aria-current="page" data-i18n="fleet.{key}.name">{en_name}</span>
    </nav>

    <div class="veh-head">
      <h1><span data-i18n="fleet.{key}.name">{en_name}</span> <span class="muted" data-i18n="veh.h1suffix">with Chauffeur in Punta Cana</span></h1>
      <div class="veh-facts">
        <span class="ok"><svg aria-hidden="true"><use href="#i-check"></use></svg><span data-i18n="veh.included">Professional chauffeur included</span></span>
        <span class="sep"></span>
        <span data-i18n="{cls}"></span>
        <span class="sep"></span>
        <span><span data-i18n="fleet.{key}.pax"></span> <span data-i18n="veh.paxSuffix">passengers</span></span>
      </div>
    </div>

    <div class="veh-layout">
      <!-- gallery -->
      <div class="gallery" id="gallery">
        <div class="gallery-stage">
          <span class="gallery-count"><b data-gallery-current>1</b> / {gallery_total}</span>
          <button class="gallery-nav gallery-nav--prev" type="button" data-gallery-prev aria-label="Previous image">
            <svg aria-hidden="true"><use href="#i-chev"></use></svg>
          </button>
          <button class="gallery-nav gallery-nav--next" type="button" data-gallery-next aria-label="Next image">
            <svg aria-hidden="true"><use href="#i-chev"></use></svg>
          </button>
{gallery_slides}
        </div>
        <div class="thumbs">
{gallery_thumbs}
        </div>
      </div>

      <!-- booking card -->
      <div class="booking-card" id="quote">
        <div class="booking-price">
          <span class="label" data-i18n="veh.startingFrom">Starting from</span>
          <span><span class="amount">${p1}</span> <span class="unit" data-i18n="veh.perTransfer">USD / one way in Punta Cana</span></span>
          <a class="link-arrow" data-wa href="#quote-form"><span data-i18n="cta.check">Check availability</span></a>
        </div>

        <form class="form-card" id="quote-form" novalidate>
          <h3 data-i18n="form.title">Request a quote</h3>
          <p data-i18n="form.sub">Tell us your trip details — we reply in minutes.</p>

          <div class="field">
            <label for="f-name"><span data-i18n="form.name">Name</span> <span class="req">*</span></label>
            <input id="f-name" name="name" type="text" required data-i18n-placeholder="form.namePh" placeholder="Your name">
          </div>

          <div class="field">
            <label for="f-phone"><span data-i18n="form.phone">Phone / WhatsApp</span> <span class="req">*</span></label>
            <div class="phone-row">
              <input id="f-code" name="code" type="text" value="+1" aria-label="Country code">
              <input id="f-phone" name="phone" type="tel" required placeholder="809 123 4567">
            </div>
          </div>

          <div class="field field-row">
            <div>
              <label for="f-date"><span data-i18n="form.date">Date</span> <span class="req">*</span></label>
              <input id="f-date" name="date" type="date" required>
            </div>
            <div>
              <label for="f-package" data-i18n="form.package">Service</label>
              <select id="f-package" name="package">
                <option data-i18n="form.pkg1">Airport transfer (PUJ)</option>
                <option data-i18n="form.pkg2">Hourly hire (3 / 5 / 8 h)</option>
                <option data-i18n="form.pkg3">Corporate travel</option>
                <option data-i18n="form.pkg4">Private tour or event</option>
              </select>
            </div>
          </div>

          <div class="field">
            <label for="f-pickup"><span data-i18n="form.pickup">Pickup location</span> <span data-i18n="form.optional">(optional)</span></label>
            <input id="f-pickup" name="pickup" type="text" data-i18n-placeholder="form.pickupPh" placeholder="Hotel, airport or area">
          </div>

          <button class="btn btn--dark" type="submit" data-i18n="form.submit">Request my quote</button>
          <p class="form-note" data-i18n="form.disclaimer">Price and booking terms confirmed before travel</p>
          <p class="form-status" id="form-status" role="status" aria-live="polite"></p>
        </form>
      </div>
    </div>
  </div>

  <!-- at a glance + packages -->
  <section class="section" style="padding-top:0">
    <div class="wrap">
      <h2 style="font-size:clamp(1.5rem,2.4vw,2rem);margin-bottom:1.4rem" data-i18n="veh.glance">At a glance</h2>
      <div class="glance-grid">
        <div><svg aria-hidden="true"><use href="#i-car"></use></svg><span data-i18n="{cls}"></span></div>
        <div><svg aria-hidden="true"><use href="#i-users"></use></svg><span><span data-i18n="fleet.{key}.pax"></span> <span data-i18n="veh.paxSuffix">passengers</span></span></div>
        <div><svg aria-hidden="true"><use href="#i-case"></use></svg><span data-i18n="fleet.{key}.bags"></span></div>
        <div><svg aria-hidden="true"><use href="#i-user"></use></svg><span data-i18n="veh.gl.chauffeur">Chauffeur included</span></div>
        <div><svg aria-hidden="true"><use href="#i-snow"></use></svg><span data-i18n="veh.gl.climate">Climate control</span></div>
        <div><svg aria-hidden="true"><use href="#i-drink"></use></svg><span data-i18n="veh.gl.water">Complimentary water</span></div>
      </div>

      <div style="margin-top:3.2rem">
        <div class="pkg-head">
          <h2 style="font-size:clamp(1.5rem,2.4vw,2rem)" data-i18n="veh.packages">Chauffeur packages</h2>
          <span data-i18n="veh.pricesIn">Prices in USD</span>
        </div>
        <div class="pkg-grid">
          <div class="pkg">
            <b data-i18n="veh.pk1">One way</b>
            <span class="amount">{p1}</span>
            <small data-i18n="veh.pk1sub">Within Punta Cana</small>
          </div>
          <div class="pkg">
            <b data-i18n="veh.pk2">3 hours</b>
            <span class="amount">{p2}</span>
            <small data-i18n="veh.pk2sub">Short errands</small>
          </div>
          <div class="pkg pkg--popular">
            <span class="tag" data-i18n="veh.popular">Popular</span>
            <b data-i18n="veh.pk3">5 hours</b>
            <span class="amount">{p3}</span>
            <small data-i18n="veh.pk3sub">Half day</small>
          </div>
          <div class="pkg">
            <b data-i18n="veh.pk4">8 hours</b>
            <span class="amount">{p4}</span>
            <small data-i18n="veh.pk4sub">Full day</small>
          </div>
        </div>
        <p class="pkg-note" data-i18n="veh.pkgNote">Starting rates — the final price varies with route, date and add-ons.</p>

        <div class="chips">
          <span class="chip"><svg aria-hidden="true"><use href="#i-check"></use></svg><span data-i18n="veh.chip1">Chauffeur included</span></span>
          <span class="chip"><svg aria-hidden="true"><use href="#i-check"></use></svg><span data-i18n="veh.chip2">Upfront quote</span></span>
          <span class="chip"><svg aria-hidden="true"><use href="#i-check"></use></svg><span data-i18n="veh.chip3">Written terms</span></span>
          <span class="chip"><svg aria-hidden="true"><use href="#i-check"></use></svg><span data-i18n="veh.chip4">Door-to-door</span></span>
          <span class="chip"><svg aria-hidden="true"><use href="#i-check"></use></svg><span data-i18n="veh.chip5">Meet &amp; greet</span></span>
        </div>
      </div>
    </div>
  </section>

  <!-- trust band -->
  <section class="trust">
    <div class="wrap">
      <div class="trust-grid">
        <div><svg aria-hidden="true"><use href="#i-award"></use></svg><b>USD</b><span data-i18n="veh.t1">Prices displayed</span></div>
        <div><svg aria-hidden="true"><use href="#i-car"></use></svg><b data-i18n="veh.t2v">3</b><span data-i18n="veh.t2">Fleet options</span></div>
        <div><svg aria-hidden="true"><use href="#i-shield"></use></svg><b data-i18n="veh.t3v">Written</b><span data-i18n="veh.t3">Booking terms</span></div>
        <div><svg aria-hidden="true"><use href="#i-headset"></use></svg><b>24/7</b><span data-i18n="veh.t4">Concierge</span></div>
      </div>
    </div>
  </section>

  <!-- other vehicles -->
  <section class="section section--tint">
    <div class="wrap">
      <p class="eyebrow" data-i18n="fleet.eyebrow">Choose early</p>
      <h2 style="font-size:clamp(1.7rem,3vw,2.4rem);margin-bottom:2.4rem" data-i18n="veh.otherTitle">Other vehicles</h2>
      <div class="fleet-grid fleet-grid--two">
{other_cards}
      </div>
      <p style="margin-top:2.4rem">
        <a class="link-arrow" href="../index.html#fleet"><span data-i18n="veh.back">Back to the full fleet</span><svg aria-hidden="true" width="12" height="12"><use href="#i-arrow"></use></svg></a>
      </p>
    </div>
  </section>
</main>

<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <div class="brand">
          <strong>JUST VIP</strong>
          <span data-i18n="brand.tagline">Punta Cana · Luxury Chauffeur</span>
        </div>
        <p data-i18n="footer.blurb"></p>
      </div>
      <div>
        <h4 data-i18n="footer.services">Services</h4>
        <ul>
          <li><a href="../index.html#services" data-i18n="services.s1.title"></a></li>
          <li><a href="../index.html#services" data-i18n="services.s2.title"></a></li>
          <li><a href="../index.html#services" data-i18n="services.s3.title"></a></li>
          <li><a href="../index.html#services" data-i18n="services.s4.title"></a></li>
        </ul>
      </div>
      <div>
        <h4 data-i18n="footer.areas">Areas</h4>
        <ul>
          <li>Punta Cana · PUJ</li>
          <li>Bávaro</li>
          <li>Cap Cana</li>
          <li>Uvero Alto</li>
          <li>La Romana · Santo Domingo</li>
        </ul>
      </div>
      <div>
        <h4 data-i18n="footer.contact">Contact</h4>
        <ul>
          <li><a data-wa href="#" data-phone>+1 809 000 0000</a></li>
          <li><a href="mailto:info@justvippuntacana.com">info@justvippuntacana.com</a></li>
          <li data-i18n="footer.hours">Dispatch available 24/7</li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© <span id="year">2026</span> Just VIP Punta Cana</span>
      <span data-i18n="footer.rights">All rights reserved.</span>
    </div>
  </div>
</footer>

<div class="floats">
  <a class="float float--call" data-tel href="#quote" aria-label="Call"><svg aria-hidden="true"><use href="#i-phone"></use></svg></a>
  <a class="float float--wa" data-wa href="#quote" aria-label="WhatsApp"><svg aria-hidden="true"><use href="#i-wa"></use></svg></a>
</div>

<script src="../assets/js/i18n.js"></script>
<script src="../assets/js/main.js"></script>
</body>
</html>
"""


def main() -> None:
    sprite_markup = sprite()
    out_dir = ROOT / "fleet"
    out_dir.mkdir(exist_ok=True)

    for v in VEHICLES:
        p1, p2, p3, p4 = v["prices"]
        slides, thumbs, total = gallery(v)
        page = TEMPLATE.format(
            slug=v["slug"],
            key=v["key"],
            cls=v["cls"],
            symbol=v["symbol"],
            en_name=v["en"],
            p1=p1, p2=p2, p3=p3, p4=p4,
            sprite=sprite_markup,
            gallery_slides=slides,
            gallery_thumbs=thumbs,
            gallery_total=total,
            other_cards=other_cards(v),
        )
        (out_dir / f"{v['slug']}.html").write_text(page, encoding="utf-8")
        print("wrote fleet/%s.html" % v["slug"])


if __name__ == "__main__":
    main()
