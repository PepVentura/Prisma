"""Titulares de los periódicos elegidos, leídos tal cual desde su RSS.
Los RSS se descubren solos desde la portada y se guardan en ~/.config/prisma/noticias.json."""
import html, json, os, re, time
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urljoin
from ..config import CONFIG
from ..texto import normaliza, pide

RUTA = os.path.expanduser("~/.config/prisma/noticias.json")
_PIDE = re.compile(r"\b(noticias|titulares|que pasa hoy|que ha pasado hoy|actualidad|ultima hora|portada)\b")
_cache = {}


class _Enlaces(HTMLParser):
    def __init__(self):
        super().__init__()
        self.feeds = []

    def handle_starttag(self, tag, a):
        a = dict(a)
        href = a.get("href") or ""
        tipo = (a.get("type") or "").lower()
        if tag == "link" and "rss" in tipo or tag == "link" and "atom" in tipo:
            self.feeds.append(href)
        elif tag == "a" and re.search(r"(rss|feed|\.xml)", href, re.I):
            self.feeds.append(href)


def descubre(periodico):
    """Busca el RSS principal en la portada y, si no hay, en su página de RSS."""
    for pagina in [periodico["web"]] + periodico.get("paginas_rss", []):
        try:
            p = _Enlaces()
            p.feed(pide(pagina, espera=8).decode("utf-8", "replace"))
        except Exception:
            continue
        for f in p.feeds:
            url = urljoin(pagina, f)
            try:
                if _titulares_de(url, 1):
                    return url
            except Exception:
                continue
    return None


def _fecha(it):
    try:
        return parsedate_to_datetime(it.findtext("pubDate") or "").timestamp()
    except (TypeError, ValueError):
        return 0


def _titulares_de(url, n, nombre=None):
    raiz = ET.fromstring(pide(url, espera=6))
    items = raiz.findall(".//item") or raiz.findall(".//{http://www.w3.org/2005/Atom}entry")
    if "news.google." in url:                     # Google Noticias no ordena por fecha
        items = sorted(items, key=_fecha, reverse=True)
    titulos = []
    for it in items:
        t = it.findtext("title") or it.findtext("{http://www.w3.org/2005/Atom}title") or ""
        t = html.unescape(re.sub(r"<[^>]+>", "", t)).strip()
        t = re.sub(r"\s+[-–|]\s+[^-–|]{2,40}$", "", t) if "news.google." in url else t   # quita « - El Periódico»
        if t and t not in titulos:
            titulos.append(t)
        if len(titulos) >= n:
            break
    return titulos


def guardados():
    try:
        with open(RUTA, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def configura():
    """Descubre y guarda los RSS de todos los periódicos (se ejecuta una vez en la Pi)."""
    feeds = guardados()
    for p in CONFIG["periodicos"]:
        if p.get("rss"):
            feeds[p["nombre"]] = p["rss"]
            continue
        url = descubre(p)
        if url:
            feeds[p["nombre"]] = url
        print(f"  {p['nombre']}: {url or 'NO ENCONTRADO (pon su RSS a mano en nucleo.json)'}")
    os.makedirs(os.path.dirname(RUTA), exist_ok=True)
    with open(RUTA, "w", encoding="utf-8") as f:
        json.dump(feeds, f, ensure_ascii=False, indent=1)
    return feeds


def entiende(texto):
    n = normaliza(texto)
    if not _PIDE.search(n):
        return None
    for p in CONFIG["periodicos"]:
        for alias in [p["nombre"]] + p.get("alias", []):
            if normaliza(alias) in n:
                return p["nombre"]
    return CONFIG["periodicos"][0]["nombre"]


def responde(nombre, n=3):
    feeds = guardados()
    url = feeds.get(nombre)
    if not url:
        return (f"No tengo configuradas las noticias de {nombre}. Ejecuta: "
                "python3 ~/prisma/software/prisma_texto.py --configurar-noticias")
    if url not in _cache or time.time() - _cache[url][0] > 600:
        _cache[url] = (time.time(), _titulares_de(url, n, nombre))
    titulos = _cache[url][1][:n]
    if not titulos:
        return f"No he podido leer los titulares de {nombre}."
    return f"Titulares de {nombre}. " + " ".join(f"{t.rstrip('.')}." for t in titulos)
