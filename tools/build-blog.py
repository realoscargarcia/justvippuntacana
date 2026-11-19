#!/usr/bin/env python3
"""Generate the blog under blog/ (English) and es/blog/ (Spanish).

Articles are written in full in both languages and rendered as static HTML,
so search engines and AI assistants read the text without running JS. The
SVG sprite comes from index.html and the header/footer copy from
assets/js/i18n.js, so the blog never drifts from the rest of the site.

    python3 tools/build-blog.py

To add an article, append an entry to POSTS with both "en" and "es".
"""

import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://justvippuntacana.com"
BRAND = "Just VIP Punta Cana"

# Where each language's blog lives, relative to the site root.
BLOG_DIR = {"en": "blog", "es": "es/blog"}

POSTS = [
    {
        # Provisional: the owner sets this to the real publish day.
        "date": "2026-12-21",
        "image": "assets/img/hero.jpg",
        "image_w": 1500,
        "image_h": 844,
        "en": {
            "slug": "group-trip-punta-cana-transfers",
            "title": "Group Trip to Punta Cana: Plan the Transfers | Just VIP",
            "h1": "Group trip to Punta Cana: how to organise it without losing half a day in transfers",
            "description": "Group trip to Punta Cana? Match people and luggage to vehicles, handle flights landing at different times and keep one list, so the group moves once.",
            "excerpt": "How to match people and luggage to vehicles, handle staggered flights at PUJ, keep one list and plan group evenings so the group moves once.",
            "image_alt": "Aircraft on the apron at Punta Cana airport at sunrise",
            "body": "group-trip-en",
        },
        "es": {
            "slug": "viaje-en-grupo-punta-cana-traslados",
            "title": "Viaje en grupo a Punta Cana: organizar traslados | Just VIP",
            "h1": "Viaje en grupo a Punta Cana: cómo organizarlo sin perder medio día en traslados",
            "description": "¿Viaje en grupo a Punta Cana? Cómo repartir personas y maletas por vehículo, coordinar vuelos a distintas horas y tener una sola lista.",
            "excerpt": "Cómo repartir personas y maletas por vehículo, coordinar vuelos que llegan a PUJ a distintas horas, llevar una sola lista y planificar las salidas del grupo.",
            "image_alt": "Avión en la plataforma del aeropuerto de Punta Cana al amanecer",
            "body": "group-trip-es",
        },
    },
]

# Page chrome that is not in i18n.js.
UI = {
    "en": {
        "blog": "Blog",
        "index_title": "Blog: Punta Cana Travel Planning | Just VIP Punta Cana",
        "index_h1": "Punta Cana travel planning",
        "index_desc": "Practical guides from Just VIP Punta Cana on planning airport transfers, group trips and private travel in Punta Cana.",
        "index_lede": "Practical guides on planning transfers and private travel in Punta Cana.",
        "read": "Read the guide",
        "published": "Published",
        "cta_extra": "For a group, send the dates, every flight, the passenger count, the luggage and the exact hotel name in one message.",
    },
    "es": {
        "blog": "Blog",
        "index_title": "Blog: planificar su viaje a Punta Cana | Just VIP Punta Cana",
        "index_h1": "Planificar su viaje a Punta Cana",
        "index_desc": "Guías prácticas de Just VIP Punta Cana para planificar traslados al aeropuerto, viajes en grupo y viajes privados en Punta Cana.",
        "index_lede": "Guías prácticas para planificar traslados y viajes privados en Punta Cana.",
        "read": "Leer la guía",
        "published": "Publicado",
        "cta_extra": "Para un grupo, envíe en un solo mensaje las fechas, cada vuelo, el número de pasajeros, el equipaje y el nombre exacto del hotel.",
    },
}

MONTHS_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
             "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July",
             "August", "September", "October", "November", "December"]


def human_date(iso: str, lang: str) -> str:
    y, m, d = (int(p) for p in iso.split("-"))
    if lang == "es":
        return f"{d} de {MONTHS_ES[m - 1]} de {y}"
    return f"{d} {MONTHS_EN[m - 1]} {y}"


def dictionary() -> dict:
    """Read the EN/ES copy from assets/js/i18n.js."""
    src = (ROOT / "assets/js/i18n.js").read_text(encoding="utf-8")
    es_at = src.index("\n  es: {")
    pair = re.compile(r'^\s*"([^"]+)":\s*("(?:[^"\\]|\\.)*")', re.M)
    return {
        "en": {k: json.loads(v) for k, v in pair.findall(src[:es_at])},
        "es": {k: json.loads(v) for k, v in pair.findall(src[es_at:])},
    }


def sprite() -> str:
    text = (ROOT / "index.html").read_text(encoding="utf-8")
    match = re.search(r"(<svg width=\"0\" height=\"0\".*?</svg>)", text, re.S)
    if not match:
        raise SystemExit("sprite not found in index.html")
    return match.group(1)


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def prefix_for(path: str) -> str:
    """Relative prefix from a page to the site root."""
    return "../" * path.count("/")


# --------------------------------------------------------------------------
# Article bodies (static HTML). FAQ entries are kept as data so the visible
# text and the FAQPage JSON-LD are always identical.
# --------------------------------------------------------------------------

ROAVI_EN = ('<p>To pick where to take the group on the first night, on Roavi (roavi.com) you can message '
            '<a href="https://roavi.com/dominican-republic/punta-cana" target="_blank" rel="noopener">a local in Punta Cana</a> '
            'for free; each Local Friend sets their own hourly rate, is paid directly, and Roavi takes no commission.</p>')

ROAVI_ES = ('<p>Para elegir dónde llevar al grupo la primera noche, en Roavi (roavi.com) puede escribirle gratis a '
            '<a href="https://roavi.com/es/punta-cana-guia-local" target="_blank" rel="noopener">un residente de Punta Cana</a>; '
            'cada Local Friend pone su propio precio por hora, se le paga directamente y Roavi no cobra comisión.</p>')


def bodies(r: str) -> dict:
    """r is the relative prefix to the site root."""
    fleet = f"{r}index.html#fleet"
    sprinter = f"{r}fleet/mercedes-benz-sprinter-2026.html"
    suburban = f"{r}fleet/chevrolet-suburban-2018.html"
    return {
        "group-trip-en": {
            "intro": f"""
<p class="post-lede">A group trip to Punta Cana usually goes wrong in the same place: the first afternoon. Twelve people land on three different flights, someone has booked a taxi, someone else is waiting by the exit with no signal, and the suitcases do not fit in the car that turned up. By the time everyone reaches the hotel, half a day has gone.</p>
<p>None of this has much to do with Punta Cana itself. It comes down to a few decisions made before anyone flies: how many vehicles, who waits for whom, and who holds the list. Here they are in order, with our own fleet as the reference.</p>
""",
            "sections": f"""
<h2>Count seats and suitcases, not just people</h2>
<p>The first question is not how many people are coming but how many people plus how many bags. A group of six with carry-ons is a different job from a group of six with golf clubs, a pushchair and a wedding dress in a garment bag.</p>
<p>Our fleet gives a practical scale. The Lincoln Navigator and the Cadillac Escalade seat up to 6 passengers with room for 5 suitcases. The two Chevrolet Suburbans also seat up to 6 but take 6 suitcases, which makes them the better choice when every passenger brings a full-size case. The <a href="{sprinter}">Mercedes-Benz Sprinter</a> seats up to 14 with space for 14 suitcases, so a group that size travels together, luggage included, in one vehicle.</p>
<p>A simple way to plan:</p>
<ul>
  <li><strong>Up to 6 people, light luggage:</strong> one SUV.</li>
  <li><strong>Up to 6 people, a large suitcase each:</strong> a <a href="{suburban}">Suburban</a>, for the sixth case.</li>
  <li><strong>7 to 14 people:</strong> one Sprinter, or two SUVs if the group is splitting up anyway.</li>
  <li><strong>More than 14:</strong> more than one vehicle, arranged together.</li>
</ul>
<p>One van or several cars? One vehicle keeps everyone on the same timetable and makes the arrival simple: one meeting point, one chauffeur, one departure. Two or three SUVs give flexibility when part of the group is staying at a different hotel, or when people land hours apart. Because our rates are per vehicle, not per passenger, the comparison is easy to make: on the current rate table for Punta Cana and Cap Cana, the Sprinter is $85 one way and the least expensive SUV is $65, so one van usually costs less than two SUVs. Uvero Alto and other destinations are quoted separately; every rate is on <a href="{fleet}">the fleet page</a>.</p>
<p>List awkward items separately: golf bags, diving gear, pushchairs, a wheelchair, instruments, boxes for an event. They decide whether a vehicle really fits.</p>

<h2>When flights land at different times</h2>
<p>Groups rarely arrive on one plane. Most visitors to the area land at Punta Cana International Airport (PUJ), so the real question is how to handle the gap between the first landing and the last.</p>
<p><strong>Wait for everyone.</strong> If the flights land close together, the early arrivals wait and the whole group leaves in one vehicle. This works when the gap is short and nobody minds a coffee in the terminal. It works badly when the gap is three or four hours and the first arrivals have small children or a dinner booking.</p>
<p><strong>Split the pickups.</strong> If the landings are far apart, book one pickup per flight, or per cluster of flights, in a vehicle sized for that part of the group. A couple on the morning flight goes in an SUV; the ten who land in the afternoon go in the Sprinter. Nobody spends the first day of the holiday in arrivals.</p>
<p>Whichever you choose, send the flight number for every arrival, not just the first one. We monitor arrivals at PUJ, so the chauffeur works from the real landing time, with free waiting time. When the pickups are split, a delay on one flight then stays with that flight instead of rippling into everyone else's.</p>

<h2>One person holds the list</h2>
<p>The groups that arrive smoothly almost always have one organiser who holds the list and talks to the transfer company. It does not have to be the person paying; it should be the person who answers WhatsApp.</p>
<p>The list that person needs is short:</p>
<ul>
  <li>The name of each traveller, grouped by flight.</li>
  <li>Flight number, date and scheduled landing time for every arrival.</li>
  <li>Number of suitcases and any oversized items on each flight.</li>
  <li>The exact name of the hotel or villa, as it appears on the reservation, plus the address for a private villa.</li>
  <li>One mobile number per flight that will be switched on at landing.</li>
  <li>The return date, flight and time for each person.</li>
</ul>
<p>The hotel name deserves its own line. Punta Cana has many resorts with similar names, several belonging to the same chain, so the chain name alone is not enough. Copy the full name from the booking confirmation. For a villa or an apartment, send the address and a map pin.</p>
<p>Send the whole list in one message rather than in pieces over a week. With one point of contact on each side, changes are easy to track: when someone's flight changes, the organiser updates the list and sends it again. Corporate groups can have the same arrangement for teams and guests, with one point of contact and consolidated billing.</p>

<h2>The first evening and group outings</h2>
<p>Once everyone has arrived, the next pinch point is the first evening. A group of ten deciding where to eat at seven o'clock, then trying to find three taxis, is how a good day ends badly. Decide in advance, and make the group move once.</p>
{ROAVI_EN}
<p>With a plan, the transport is simple. If the restaurant is a single trip there and back, book it as a transfer each way. If the evening has several stops, or you would rather not fix a return time, hourly hire keeps the same car and chauffeur with the group for the evening; it is quoted on request. The same goes for outings during the week: private excursions to Saona, Macao or Altos de Chavón are arranged with waiting time included, so the vehicle that takes the group out is the one that brings it back. For a wedding or a celebration, send the full schedule of the day and we plan the vehicles around it.</p>

<h2>Coming back to the airport</h2>
<p>The return is easier, because the times are known in advance, but groups still trip on it. People often leave on different flights, and hotel check-out times rarely match flight times.</p>
<p>Plan the return from the same list: group the travellers by departure flight, then work back to a collection time from each hotel, leaving enough margin for check-in at PUJ. The collection time is part of the written confirmation, so everyone knows when to be in the lobby. If the whole group flies out within a short window, one vehicle can collect everyone; if not, split the return the same way you split the arrival. Booking the return with the arrival saves the organiser a second round of messages.</p>
""",
            "faq_title": "Frequently asked questions",
            "faq": [
                ("How many people fit in one vehicle?",
                 "Our SUVs (Lincoln Navigator, Cadillac Escalade and both Chevrolet Suburbans) seat up to 6 passengers. The Navigator and the Escalade carry 5 suitcases and the Suburbans 6. The Mercedes-Benz Sprinter seats up to 14, with room for 14 suitcases."),
                ("What if our group is larger than 14?",
                 "No single vehicle in the fleet seats more than 14, so we arrange more than one. Send the passenger count, the flights and the luggage, and we reply with the vehicles assigned and a written price."),
                ("Is the price per person or per vehicle?",
                 "Per vehicle, not per passenger, and the chauffeur is included. Rates for Punta Cana and Cap Cana are shown on each vehicle page; Uvero Alto and other destinations are quoted on request."),
                ("What happens if one of the group's flights is delayed?",
                 "Send the flight number for every arrival. We monitor arrivals at PUJ, so the chauffeur works from the real landing time, with free waiting time. If the group has split pickups, a delay on one flight does not hold up the others."),
            ],
        },
        "group-trip-es": {
            "intro": f"""
<p class="post-lede">Un viaje en grupo a Punta Cana suele torcerse en el mismo momento: la primera tarde. Doce personas aterrizan en tres vuelos distintos, alguien ha reservado un taxi, otro espera en la salida sin señal y las maletas no caben en el coche que llegó. Cuando todos están por fin en el hotel, se ha ido medio día.</p>
<p>Casi nada de esto tiene que ver con Punta Cana. Depende de unas pocas decisiones que se toman antes de volar: cuántos vehículos, quién espera a quién y quién lleva la lista. Aquí van en orden, con nuestra flota como referencia.</p>
""",
            "sections": f"""
<h2>Cuente asientos y maletas, no solo personas</h2>
<p>La primera pregunta no es cuántas personas vienen, sino cuántas personas y cuántas maletas. Seis personas con equipaje de mano no son lo mismo que seis con bolsas de golf, un cochecito y un vestido de novia en su funda.</p>
<p>La Lincoln Navigator y la Cadillac Escalade llevan hasta 6 pasajeros con espacio para 5 maletas. Las dos Chevrolet Suburban también llevan hasta 6, pero caben 6 maletas, así que son la mejor opción cuando cada pasajero trae una maleta grande. La <a href="{sprinter}">Mercedes-Benz Sprinter</a> lleva hasta 14 pasajeros con espacio para 14 maletas, de modo que un grupo de ese tamaño viaja junto, con su equipaje, en un solo vehículo.</p>
<p>En resumen:</p>
<ul>
  <li><strong>Hasta 6 personas, poco equipaje:</strong> una SUV.</li>
  <li><strong>Hasta 6 personas, una maleta grande cada una:</strong> una <a href="{suburban}">Suburban</a>, por la sexta maleta.</li>
  <li><strong>De 7 a 14 personas:</strong> una Sprinter, o dos SUV si el grupo se va a separar de todos modos.</li>
  <li><strong>Más de 14:</strong> más de un vehículo, coordinados entre sí.</li>
</ul>
<p>¿Una van o varios coches? Un solo vehículo mantiene a todos en el mismo horario: un punto de encuentro, un chofer, una salida. Dos o tres SUV dan flexibilidad cuando parte del grupo se aloja en otro hotel o cuando las llegadas están separadas por horas. Como nuestras tarifas son por vehículo, no por pasajero, la comparación es fácil: en la tabla de tarifas actual para Punta Cana y Cap Cana, la Sprinter cuesta $85 una ida y la SUV más económica $65, así que una van suele salir más barata que dos SUV. Uvero Alto y otros destinos se cotizan aparte; todas las tarifas están en <a href="{fleet}">la página de la flota</a>.</p>
<p>Indique aparte los bultos difíciles: bolsas de golf, equipo de buceo, cochecitos, una silla de ruedas, instrumentos, cajas para un evento. Son los que deciden si un vehículo basta.</p>

<h2>Cuando los vuelos llegan a distintas horas</h2>
<p>Los grupos casi nunca llegan en el mismo avión. La mayoría de los visitantes de la zona aterriza en el Aeropuerto Internacional de Punta Cana (PUJ), así que la pregunta es qué hacer entre la primera llegada y la última.</p>
<p><strong>Esperar a todos.</strong> Si los vuelos aterrizan con poca diferencia, los primeros esperan y todo el grupo sale en un solo vehículo. Funciona si la espera es corta. Funciona mal si la diferencia es de tres o cuatro horas y los primeros traen niños pequeños o tienen una cena reservada.</p>
<p><strong>Separar las recogidas.</strong> Si las llegadas están muy separadas, reserve una recogida por vuelo (o por vuelos cercanos), con un vehículo a la medida de esa parte del grupo. Una pareja en el vuelo de la mañana va en una SUV; los diez que aterrizan por la tarde, en la Sprinter. Nadie pasa el primer día de vacaciones en la sala de llegadas.</p>
<p>Elija lo que elija, envíe el número de vuelo de cada llegada, no solo el de la primera. Monitoreamos las llegadas a PUJ, así que el chofer trabaja con la hora real de aterrizaje, con tiempo de espera incluido. Cuando las recogidas van separadas, el retraso de un vuelo se queda en ese vuelo y no arrastra a los demás.</p>

<h2>Una sola persona lleva la lista</h2>
<p>Los grupos que llegan sin problemas casi siempre tienen un organizador que lleva la lista y habla con la empresa de traslados. No tiene que ser quien paga; debe ser quien contesta el WhatsApp.</p>
<p>La lista que necesita esa persona es corta:</p>
<ul>
  <li>El nombre de cada viajero, agrupado por vuelo.</li>
  <li>Número de vuelo, fecha y hora prevista de llegada de cada vuelo.</li>
  <li>Número de maletas y bultos grandes en cada vuelo.</li>
  <li>El nombre exacto del hotel o la villa, tal como aparece en la reserva, y la dirección si es una villa privada.</li>
  <li>Un móvil por vuelo que esté encendido al aterrizar.</li>
  <li>La fecha, el vuelo y la hora de regreso de cada persona.</li>
</ul>
<p>El nombre del hotel merece su propia línea. En Punta Cana hay muchos resorts con nombres parecidos, varios de la misma cadena, así que el nombre de la cadena no basta. Copie el nombre completo de la confirmación de la reserva. Para una villa o un apartamento, envíe la dirección y una ubicación en el mapa.</p>
<p>Envíe la lista completa en un solo mensaje, no a trozos durante una semana. Si cambia el vuelo de alguien, el organizador actualiza la lista y la vuelve a enviar. Los grupos corporativos pueden tener el mismo esquema para equipos e invitados, con un solo contacto y facturación consolidada.</p>

<h2>La primera noche y las salidas en grupo</h2>
<p>Después llega la primera noche. Un grupo de diez decidiendo a las siete dónde cenar y buscando luego tres taxis es como un buen día termina mal. Decídalo con antelación y haga que el grupo se mueva una sola vez.</p>
{ROAVI_ES}
<p>Con un plan, el transporte es sencillo. Si el restaurante es un solo trayecto, resérvelo como traslado de ida y otro de vuelta. Si la noche tiene varias paradas, o prefiere no fijar la hora de regreso, el alquiler por horas mantiene el mismo vehículo y chofer con el grupo toda la noche; se cotiza a solicitud. Lo mismo vale para las salidas durante la semana: las excursiones privadas a Saona, Macao o Altos de Chavón se organizan con tiempo de espera incluido: el vehículo que lleva al grupo es el que lo trae de vuelta. Para una boda o una celebración, envíe el horario completo del día y planificamos los vehículos en torno a él.</p>

<h2>La vuelta al aeropuerto</h2>
<p>El regreso es más fácil, porque las horas se conocen de antemano, pero los grupos también tropiezan aquí. La gente suele irse en vuelos distintos, y la salida del hotel rara vez coincide con la del vuelo.</p>
<p>Planifique el regreso con la misma lista: agrupe a los viajeros por vuelo de salida y calcule la hora de recogida en cada hotel, con margen para el check-in en PUJ. La hora de recogida forma parte de la confirmación por escrito, así que todos saben cuándo estar en el lobby. Si todo el grupo vuela en un intervalo corto, un solo vehículo puede recoger a todos; si no, separe el regreso igual que separó la llegada. Reservar la vuelta junto con la llegada le ahorra al organizador otra ronda de mensajes.</p>
""",
            "faq_title": "Preguntas frecuentes",
            "faq": [
                ("¿Cuántas personas caben en un vehículo?",
                 "Nuestras SUV (Lincoln Navigator, Cadillac Escalade y las dos Chevrolet Suburban) llevan hasta 6 pasajeros. La Navigator y la Escalade llevan 5 maletas y las Suburban 6. La Mercedes-Benz Sprinter lleva hasta 14 pasajeros, con espacio para 14 maletas."),
                ("¿Y si nuestro grupo es de más de 14 personas?",
                 "Ningún vehículo de la flota lleva más de 14 pasajeros, así que coordinamos más de uno. Envíe el número de pasajeros, los vuelos y el equipaje, y le respondemos con los vehículos asignados y un precio por escrito."),
                ("¿El precio es por persona o por vehículo?",
                 "Por vehículo, no por pasajero, y el chofer está incluido. Las tarifas para Punta Cana y Cap Cana aparecen en cada página de vehículo; Uvero Alto y otros destinos se cotizan a solicitud."),
                ("¿Qué pasa si se retrasa uno de los vuelos del grupo?",
                 "Envíe el número de vuelo de cada llegada. Monitoreamos las llegadas a PUJ, así que el chofer trabaja con la hora real de aterrizaje, con tiempo de espera incluido. Si el grupo tiene recogidas separadas, el retraso de un vuelo no detiene a los demás."),
            ],
        },
    }


# --------------------------------------------------------------------------
# Page template
# --------------------------------------------------------------------------

def page(*, lang, path, title, description, alt_paths, body_html, jsonld, d, og_type="article"):
    """path: output path relative to root, e.g. 'blog/x.html' or 'es/blog/index.html'."""
    r = prefix_for(path)

    def url(p):
        return SITE + "/" + (p[:-len("index.html")] if p.endswith("index.html") else p)

    other = "es" if lang == "en" else "en"
    hreflang = "\n".join(
        f'<link rel="alternate" hreflang="{l}" href="{url(alt_paths[l])}">' for l in ("en", "es")
    ) + f'\n<link rel="alternate" hreflang="x-default" href="{url(alt_paths["en"])}">'
    switch_href = {l: r + (alt_paths[l][:-len("index.html")] if alt_paths[l].endswith("index.html")
                           else alt_paths[l]) for l in ("en", "es")}
    ld = "\n".join(
        '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=2) + "\n</script>"
        for obj in jsonld
    )
    t = d[lang]
    blog_home = r + BLOG_DIR[lang] + "/"

    return f"""<!DOCTYPE html>
<html lang="{lang}" data-lang-lock="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{url(path)}">
{hreflang}
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{url(path)}">
<meta property="og:image" content="{SITE}/assets/img/hero.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@0,400;0,500;1,400;1,500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}assets/css/styles.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' fill='%230d0d0e'/><text x='50' y='68' font-size='54' font-family='Georgia' font-style='italic' fill='%23c8a86b' text-anchor='middle'>V</text></svg>">
{ld}
</head>
<body>

{sprite()}

<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{r}index.html">
      <strong>JUST VIP</strong>
      <span data-i18n="brand.tagline">{esc(t["brand.tagline"])}</span>
    </a>

    <nav class="nav" id="nav">
      <a href="{r}index.html#services" data-i18n="nav.services">{esc(t["nav.services"])}</a>
      <a href="{r}index.html#fleet" data-i18n="nav.fleet">{esc(t["nav.fleet"])}</a>
      <a href="{r}index.html#how" data-i18n="nav.how">{esc(t["nav.how"])}</a>
      <a href="{r}index.html#why" data-i18n="nav.why">{esc(t["nav.why"])}</a>
      <a href="#contact" data-i18n="nav.contact">{esc(t["nav.contact"])}</a>
    </nav>

    <div class="header-actions">
      <div class="lang-switch" role="group" aria-label="Language / Idioma">
        <button type="button" data-lang="en" data-href="{switch_href['en']}" aria-pressed="{str(lang == 'en').lower()}">EN</button>
        <button type="button" data-lang="es" data-href="{switch_href['es']}" aria-pressed="{str(lang == 'es').lower()}">ES</button>
      </div>
      <a class="btn btn--gold" data-wa href="#contact">
        <svg aria-hidden="true"><use href="#i-wa"></use></svg>
        <span data-i18n="cta.book">{esc(t["cta.book"])}</span>
      </a>
      <button class="nav-toggle" type="button" aria-label="Menu" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
</header>

<main class="page">
{body_html}

  <section class="section quote-section" id="contact">
    <div class="wrap quote-layout">
      <div>
        <p class="eyebrow" data-i18n="contact.eyebrow">{esc(t["contact.eyebrow"])}</p>
        <h2 data-i18n="contact.title">{esc(t["contact.title"])}</h2>
        <p class="lede" style="margin-top:1.5rem" data-i18n="contact.lede">{esc(t["contact.lede"])}</p>
        <p class="lede">{esc(UI[lang]["cta_extra"])}</p>
        <div class="hero-cta" style="margin-top:2rem">
          <a class="btn btn--gold" data-wa href="#contact">
            <svg aria-hidden="true"><use href="#i-wa"></use></svg>
            <span data-i18n="cta.check">{esc(t["cta.check"])}</span>
          </a>
          <a class="btn btn--ghost" data-tel href="#contact">
            <svg aria-hidden="true"><use href="#i-phone"></use></svg>
            <span data-phone>+1 809 000 0000</span>
          </a>
        </div>
      </div>

      <ul class="contact-list">
        <li>
          <svg aria-hidden="true"><use href="#i-wa"></use></svg>
          <div><b data-i18n="contact.wa">{esc(t["contact.wa"])}</b><a data-wa href="#" data-phone>+1 809 000 0000</a></div>
        </li>
        <li>
          <svg aria-hidden="true"><use href="#i-phone"></use></svg>
          <div><b data-i18n="contact.phone">{esc(t["contact.phone"])}</b><a data-tel href="#" data-phone>+1 809 000 0000</a></div>
        </li>
        <li>
          <svg aria-hidden="true"><use href="#i-mail"></use></svg>
          <div><b data-i18n="contact.email">{esc(t["contact.email"])}</b><a href="mailto:info@justvippuntacana.com">info@justvippuntacana.com</a></div>
        </li>
        <li>
          <svg aria-hidden="true"><use href="#i-pin"></use></svg>
          <div><b data-i18n="contact.area">{esc(t["contact.area"])}</b><span data-i18n="contact.areaText">{esc(t["contact.areaText"])}</span></div>
        </li>
      </ul>
    </div>
  </section>
</main>

<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <div class="brand">
          <strong>JUST VIP</strong>
          <span data-i18n="brand.tagline">{esc(t["brand.tagline"])}</span>
        </div>
        <p data-i18n="footer.blurb">{esc(t["footer.blurb"])}</p>
      </div>
      <div>
        <h4 data-i18n="footer.services">{esc(t["footer.services"])}</h4>
        <ul>
          <li><a href="{r}index.html#services" data-i18n="services.s1.title">{esc(t["services.s1.title"])}</a></li>
          <li><a href="{r}index.html#services" data-i18n="services.s2.title">{esc(t["services.s2.title"])}</a></li>
          <li><a href="{r}index.html#services" data-i18n="services.s3.title">{esc(t["services.s3.title"])}</a></li>
          <li><a href="{r}index.html#services" data-i18n="services.s4.title">{esc(t["services.s4.title"])}</a></li>
          <li><a href="{blog_home}" data-i18n="footer.blog">{esc(t["footer.blog"])}</a></li>
        </ul>
      </div>
      <div>
        <h4 data-i18n="footer.areas">{esc(t["footer.areas"])}</h4>
        <ul>
          <li>Punta Cana · PUJ</li>
          <li>Bávaro</li>
          <li>Cap Cana</li>
          <li>Uvero Alto</li>
          <li>La Romana · Santo Domingo</li>
        </ul>
      </div>
      <div>
        <h4 data-i18n="footer.contact">{esc(t["footer.contact"])}</h4>
        <ul>
          <li><a data-wa href="#" data-phone>+1 809 000 0000</a></li>
          <li><a href="mailto:info@justvippuntacana.com">info@justvippuntacana.com</a></li>
          <li data-i18n="footer.hours">{esc(t["footer.hours"])}</li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© <span id="year">2026</span> Just VIP Punta Cana</span>
      <span data-i18n="footer.rights">{esc(t["footer.rights"])}</span>
    </div>
  </div>
</footer>

<div class="floats">
  <a class="float float--call" data-tel href="#contact" aria-label="Call"><svg aria-hidden="true"><use href="#i-phone"></use></svg></a>
  <a class="float float--wa" data-wa href="#contact" aria-label="WhatsApp"><svg aria-hidden="true"><use href="#i-wa"></use></svg></a>
</div>

<script src="{r}assets/js/i18n.js"></script>
<script src="{r}assets/js/main.js"></script>
</body>
</html>
"""


def organization():
    return {"@type": "Organization", "name": BRAND, "url": SITE + "/"}


def build_article(post, lang, d):
    meta = post[lang]
    path = f"{BLOG_DIR[lang]}/{meta['slug']}.html"
    r = prefix_for(path)
    body = bodies(r)[meta["body"]]
    ui = UI[lang]
    canonical = f"{SITE}/{path}"

    faq_html = "\n".join(
        f'<div class="faq-item">\n  <h3>{esc(q)}</h3>\n  <p>{esc(a)}</p>\n</div>' for q, a in body["faq"]
    )
    home_label = d[lang]["veh.home"]
    body_html = f"""  <article class="post">
    <div class="wrap post-wrap">
      <nav class="breadcrumb" aria-label="Breadcrumb">
        <a href="{r}index.html">{esc(home_label)}</a>
        <span class="sep">/</span>
        <a href="{r}{BLOG_DIR[lang]}/">{esc(ui["blog"])}</a>
        <span class="sep">/</span>
        <span aria-current="page">{esc(meta["h1"])}</span>
      </nav>
      <header class="post-head">
        <h1>{esc(meta["h1"])}</h1>
        <p class="post-meta">{esc(ui["published"])} <time datetime="{post["date"]}">{human_date(post["date"], lang)}</time> · {BRAND}</p>
      </header>
      <figure class="post-figure">
        <img src="{r}{post["image"]}" alt="{esc(meta["image_alt"])}" width="{post["image_w"]}" height="{post["image_h"]}" decoding="async">
      </figure>
      <div class="post-body">
{body["intro"].strip()}
{body["sections"].strip()}

<h2>{esc(body["faq_title"])}</h2>
<div class="faq">
{faq_html}
</div>
      </div>
    </div>
  </article>"""

    jsonld = [
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": meta["h1"],
            "description": meta["description"],
            "datePublished": post["date"],
            "dateModified": post.get("updated", post["date"]),
            "inLanguage": lang,
            "image": f"{SITE}/{post['image']}",
            "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
            "author": organization(),
            "publisher": organization(),
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "inLanguage": lang,
            "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in body["faq"]
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": home_label, "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": ui["blog"], "item": f"{SITE}/{BLOG_DIR[lang]}/"},
                {"@type": "ListItem", "position": 3, "name": meta["h1"], "item": canonical},
            ],
        },
    ]
    alt_paths = {l: f"{BLOG_DIR[l]}/{post[l]['slug']}.html" for l in ("en", "es")}
    return path, page(lang=lang, path=path, title=meta["title"], description=meta["description"],
                      alt_paths=alt_paths, body_html=body_html, jsonld=jsonld, d=d)


def build_index(lang, d):
    path = f"{BLOG_DIR[lang]}/index.html"
    r = prefix_for(path)
    ui = UI[lang]
    cards = []
    for post in sorted(POSTS, key=lambda p: p["date"], reverse=True):
        meta = post[lang]
        cards.append(f"""        <article class="post-card">
          <p class="post-meta"><time datetime="{post["date"]}">{human_date(post["date"], lang)}</time></p>
          <h2><a href="{meta["slug"]}.html">{esc(meta["h1"])}</a></h2>
          <p>{esc(meta["excerpt"])}</p>
          <a class="link-arrow" href="{meta["slug"]}.html"><span>{esc(ui["read"])}</span><svg aria-hidden="true" width="12" height="12"><use href="#i-arrow"></use></svg></a>
        </article>""")
    body_html = f"""  <section class="post">
    <div class="wrap post-wrap">
      <nav class="breadcrumb" aria-label="Breadcrumb">
        <a href="{r}index.html">{esc(d[lang]["veh.home"])}</a>
        <span class="sep">/</span>
        <span aria-current="page">{esc(ui["blog"])}</span>
      </nav>
      <header class="post-head">
        <h1>{esc(ui["index_h1"])}</h1>
        <p class="lede">{esc(ui["index_lede"])}</p>
      </header>
      <div class="post-list">
{chr(10).join(cards)}
      </div>
    </div>
  </section>"""
    jsonld = [{
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": ui["index_h1"],
        "inLanguage": lang,
        "url": f"{SITE}/{BLOG_DIR[lang]}/",
        "publisher": organization(),
    }]
    alt_paths = {l: f"{BLOG_DIR[l]}/index.html" for l in ("en", "es")}
    return path, page(lang=lang, path=path, title=ui["index_title"], description=ui["index_desc"],
                      alt_paths=alt_paths, body_html=body_html, jsonld=jsonld, d=d, og_type="website")


def main() -> None:
    d = dictionary()
    pages = []
    for lang in ("en", "es"):
        pages.append(build_index(lang, d))
        for post in POSTS:
            pages.append(build_article(post, lang, d))

    written = set()
    for path, text in pages:
        out = ROOT / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        written.add(out)
        print("wrote", path)

    # drop articles that are no longer in POSTS
    for lang in ("en", "es"):
        for stale in (ROOT / BLOG_DIR[lang]).glob("*.html"):
            if stale not in written:
                stale.unlink()
                print("removed stale", stale.relative_to(ROOT))


if __name__ == "__main__":
    main()
