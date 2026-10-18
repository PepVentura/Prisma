"""Conversación con el modelo local (Ollama) en streaming, troceada para la voz."""
import json, re, time, urllib.request
from .config import CONFIG, SISTEMA

_FIN = re.compile(r"[.!?…]$")
_PAUSA = re.compile(r"[,;:]$")


def trozos_para_voz(fragmentos, min_palabras_coma=6, max_palabras=18):
    """Agrupa el texto que va llegando en trozos que Piper puede empezar a leer ya:
    al final de cada frase, en una coma si ya hay unas cuantas palabras, o si se alarga mucho."""
    buf = ""
    for f in fragmentos:
        buf += f
        while True:
            palabras = buf.split(" ")
            corte = None
            acum = 0
            for i, p in enumerate(palabras[:-1]):          # la última palabra puede estar a medias
                acum += 1
                if _FIN.search(p) or (_PAUSA.search(p) and acum >= min_palabras_coma) or acum >= max_palabras:
                    corte = i + 1
                    break
            if corte is None:
                break
            trozo = " ".join(palabras[:corte]).strip()
            buf = " ".join(palabras[corte:])
            if trozo:
                yield trozo
    if buf.strip():
        yield buf.strip()


class Cerebro:
    def __init__(self):
        self.historial = []
        self.ultimo = {}

    def calienta(self):
        """Carga el modelo y lee las instrucciones fijas, para que la primera pregunta vaya rápida."""
        t0 = time.perf_counter()
        for _ in self._stream([{"role": "system", "content": SISTEMA}, {"role": "user", "content": "Hola"}], 1):
            pass
        return time.perf_counter() - t0

    def responde(self, texto, contexto=None):
        """Generador de trozos de respuesta listos para la voz. Las métricas quedan en self.ultimo."""
        usuario = texto if not contexto else f"Resultados de búsqueda:\n{contexto}\n\nPregunta: {texto}"
        mensajes = [{"role": "system", "content": SISTEMA}] + self.historial[-CONFIG["historial"]:] + \
                   [{"role": "user", "content": usuario}]
        t0 = time.perf_counter()
        completo = []
        primera = None
        for trozo in trozos_para_voz(self._stream(mensajes, CONFIG["max_tokens"])):
            if primera is None:
                primera = time.perf_counter() - t0
            completo.append(trozo)
            yield trozo
        respuesta = " ".join(completo)
        # en el historial se guarda la pregunta sin los resultados, para no alargar las siguientes
        self.historial += [{"role": "user", "content": texto}, {"role": "assistant", "content": respuesta}]
        self.ultimo.update(primera_voz=primera, total=time.perf_counter() - t0)

    def _stream(self, mensajes, max_tokens):
        datos = json.dumps({"model": CONFIG["modelo"], "messages": mensajes, "stream": True, "think": False,
                            "keep_alive": -1,
                            "options": {"num_predict": max_tokens, "temperature": CONFIG["temperatura"]}}).encode()
        req = urllib.request.Request(CONFIG["ollama"] + "/api/chat", data=datos,
                                     headers={"Content-Type": "application/json"})
        self.ultimo = {}
        with urllib.request.urlopen(req) as r:
            for linea in r:
                d = json.loads(linea)
                c = d.get("message", {}).get("content", "")
                if c:
                    yield c
                if d.get("done"):
                    pd = d.get("prompt_eval_duration", 0) / 1e9
                    self.ultimo.update(tokens_leidos=d.get("prompt_eval_count", 0), lectura_s=pd,
                                       tok_s=d.get("eval_count", 0) / max(d.get("eval_duration", 1) / 1e9, 1e-9))
