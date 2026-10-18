"""Configuración del núcleo de Prisma. Se puede sobrescribir con ~/.config/prisma/nucleo.json."""
import json, os

CONFIG = {
    "ollama": "http://127.0.0.1:11434",
    "modelo": "qwen3:1.7b",                  # D038
    "searxng": "http://127.0.0.1:8888",
    # Buscadores que consulta SearXNG: pocos y rápidos. Vacío = los que tenga activados.
    "buscadores": "duckduckgo,wikipedia,brave,startpage",
    "busqueda_espera": 1.5,                  # s que SearXNG espera a cada buscador
    "busqueda_resultados": 2,                # resultados que lee el modelo
    "busqueda_caracteres": 280,              # caracteres por resultado (≈70 tokens)
    "max_tokens": 140,                       # longitud máxima de una respuesta hablada
    "temperatura": 0.6,
    "historial": 6,                          # mensajes previos que recuerda en la charla
}

_usuario = os.path.expanduser("~/.config/prisma/nucleo.json")
if os.path.exists(_usuario):
    with open(_usuario, encoding="utf-8") as f:
        CONFIG.update(json.load(f))

# Instrucciones fijas: no cambian nunca, así Ollama reutiliza su lectura entre preguntas.
SISTEMA = (
    "Eres Prisma, un asistente de sobremesa que habla en español de España con un tono cercano. "
    "Tus respuestas se leen en voz alta: contesta en una a tres frases cortas, sin listas, sin "
    "formato, sin emojis y sin URL. Si te dan resultados de búsqueda, usa solo esos datos; si no "
    "contienen la respuesta, dilo con sencillez en vez de inventar."
)
