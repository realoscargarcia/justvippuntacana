# Just VIP Punta Cana

Bilingual (English / Spanish) one-page site for a luxury chauffeur and VIP transfer
service in Punta Cana, Dominican Republic.

## Stack

Static HTML, CSS and vanilla JS — no build step. Open `index.html` or serve the
folder:

```bash
python3 -m http.server 8000
```

## Structure

```
index.html               home page (English is the inline default)
fleet/*.html             vehicle detail pages — GENERATED, do not edit by hand
tools/build-fleet.py     generates fleet/ from one template + the vehicle table
assets/css/styles.css    design system + layout
assets/js/i18n.js        EN/ES dictionary (all copy lives here)
assets/js/main.js        language switch, nav, reveal, gallery, quote form
```

## Vehicle pages

`fleet/executive-sedan.html`, `fleet/premium-suv.html` and `fleet/vip-van.html`
are generated so they never drift apart. Edit the template, the vehicle table
(names, prices, icons) or the shared SVG sprite in `index.html`, then rebuild:

```bash
python3 tools/build-fleet.py
```

Each page has a breadcrumb, gallery with thumbnails, a sticky booking card with
the starting price and quote form, an "at a glance" spec grid, the package
price table, a trust band and the other two vehicles. The WhatsApp message is
pre-filled with the vehicle name in the visitor's language.

## Language

- Switch with the EN / ES toggle in the header.
- The choice is stored in `localStorage`; `?lang=es` forces a language, and
  first-time visitors with a Spanish browser get Spanish automatically.
- To edit or add copy, change the matching key in **both** `en` and `es` in
  `assets/js/i18n.js`.

## Before going live

Update `CONFIG` at the top of `assets/js/main.js`:

```js
var CONFIG = {
  phoneDisplay: "+1 809 000 0000",  // shown on the page
  phoneDial:    "+18090000000",     // tel: link
  whatsapp:     "18090000000"       // wa.me number, digits only
};
```

Also replace the placeholder email (`info@justvippuntacana.com`), the indicative
"from" prices in the fleet cards, and the canonical URL in `index.html`.

The quote form has no backend — it composes the request and opens WhatsApp with
the message pre-filled. Point it at a form endpoint if you'd rather collect
leads by email.

The hero photograph lives in `assets/img/` (`hero.jpg` for desktop, the taller
`hero-mobile.jpg` served below 700px via `<picture>`). Swap both if you change
it, and keep them cropped to roughly the same framing so the overlay still
keeps the headline readable.

## Fleet photography

Real photos live in `assets/img/fleet/` as `<name>.jpg` (1200x900) plus a
`<name>-thumb.jpg` (400x300), all cropped to 4:3. A vehicle gets them by listing
them in its `images` entry in `tools/build-fleet.py`:

```python
"images": [("escalade-1-exterior", "veh.g1", "alt text"), ...]
```

The second value is the i18n key for the slide label (`veh.g1`-`veh.g5`:
exterior, interior, detail, rear cabin, cockpit). The gallery, its counter and
the card thumbnail all follow the list, so the count is whatever you supply.
The Cadillac Escalade has real photography; the sedan and van still fall back
to inline SVG silhouettes until you add theirs.
