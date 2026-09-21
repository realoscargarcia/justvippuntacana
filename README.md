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
index.html            markup (English is the inline default)
assets/css/styles.css design system + layout
assets/js/i18n.js     EN/ES dictionary (all copy lives here)
assets/js/main.js     language switch, nav, reveal, quote form
```

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

Vehicle images are inline SVG placeholders; drop real photography into
`assets/img/` and swap the `.card-media` / `.service-media` blocks when it's ready.
