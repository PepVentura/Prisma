"""Configuración del núcleo de Prisma. Se puede sobrescribir con ~/.config/prisma/nucleo.json."""
import json, os

CONFIG = {
    "ollama": "http://127.0.0.1:11434",
    "modelo": "qwen3:1.7b",                  # D038
    "searxng": "http://127.0.0.1:8888",
    # Buscadores que consulta SearXNG: pocos y rápidos. Vacío = los que tenga activados.
    "buscadores": "duckduckgo,wikipedia,brave,startpage",
    "busqueda_espera": 1.5,                  # s que SearXNG espera a cada buscador
    "busqueda_resultados": 3,                # resultados que lee el modelo
    "busqueda_caracteres": 200,              # caracteres por resultado (≈50 tokens)
    "max_tokens": 140,                       # longitud máxima de una respuesta hablada
    "temperatura": 0.6,
    "ciudad": "Donostia",                    # para «¿qué tiempo hará mañana?» sin decir dónde
    "equipo": "Real Sociedad",               # para «¿cómo quedó la Real?» o «¿cuándo juega?»
    "futbol_liga": "PD",                     # LaLiga en football-data.org
    "spotify_dispositivo": "Prisma",        # nombre del altavoz de raspotify en Spotify Connect
    "home_assistant": "http://homeassistant.local:8123",   # botón «Casa» de la pantalla
    "futbol_clave": "",                      # clave gratuita de football-data.org (ponla en nucleo.json)
    # Periódicos para «noticias»: el primero es el de por defecto. El RSS se descubre solo
    # (--configurar-noticias); si no lo encuentra, se puede poner a mano con "rss".
    "periodicos": [
        # El Periódico y Deia bloquean los programas (406 WAF): sus titulares se leen de Google Noticias
        {"nombre": "El Periódico", "alias": ["el periodico", "periodico de catalunya"],
         "rss": "https://news.google.com/rss/search?q=site:elperiodico.com+when:1d&hl=es&gl=ES&ceid=ES:es"},
        {"nombre": "La Vanguardia", "alias": ["vanguardia"],
         "web": "https://www.lavanguardia.com/", "paginas_rss": ["https://www.lavanguardia.com/rss"]},
        {"nombre": "Deia", "alias": [],
         "rss": "https://news.google.com/rss/search?q=site:deia.eus+when:1d&hl=es&gl=ES&ceid=ES:es"},
        {"nombre": "EITB", "alias": ["eitb", "teleberri"],
         "web": "https://www.eitb.eus/es/", "paginas_rss": ["https://www.eitb.eus/es/rss/"]},
        {"nombre": "TV3", "alias": ["tv3", "tvs", "3cat", "3catinfo", "tres cat"],
         "web": "https://www.3cat.cat/3catinfo/", "paginas_rss": ["https://www.3cat.cat/rss/"]},
    ],
    "historial": 4,                          # mensajes previos de la charla que se le vuelven a pasar
    "voz_coma_palabras": 4,                  # empieza a hablar en una coma si ya lleva estas palabras
    "voz_max_palabras": 12,                  # o al llegar a estas, aunque no haya pausa
}

_usuario = os.path.expanduser("~/.config/prisma/nucleo.json")
if os.path.exists(_usuario):
    with open(_usuario, encoding="utf-8") as f:
        CONFIG.update(json.load(f))

# Instrucciones fijas durante la sesión, así Ollama reutiliza su lectura entre preguntas.
SISTEMA = (
    "Eres Prisma, un asistente de sobremesa que habla en español de España con un tono cercano. "
    "Tus respuestas se leen en voz alta: contesta en una a tres frases cortas, sin listas, sin formato, "
    "sin emojis y sin URL. Haz directamente lo que te piden: si te piden un chiste, cuéntalo; no preguntes "
    "si quieren que lo hagas ni sobre qué tema. Evita la política y los temas delicados en los chistes. "
    "No prometas cosas que no puedes hacer: tú no guardas recuerdos por tu cuenta; si alguien quiere que "
    "recuerdes algo, dile que te diga «recuerda que…». Si te dan resultados de búsqueda, usa solo esos "
    "datos y cita el dato concreto; si no contienen la respuesta, di que no lo has encontrado en vez de "
    "inventar. Si no sabes algo con seguridad, dilo."
)
