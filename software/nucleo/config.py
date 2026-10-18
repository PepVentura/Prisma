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
