"""El asistente completo: recibe un texto y devuelve eventos (estado, trozos de respuesta, fin).
Lo usan tanto prisma_texto.py (terminal) como servidor.py (pantalla)."""
import threading, time
from . import enrutador, memoria
from .cerebro import Cerebro
from .fuentes import web, video, musica


class Asistente:
    def __init__(self):
        self.cerebro = Cerebro()
        self._cerrojo = threading.Lock()          # una petición cada vez: hay un solo modelo

    def calienta(self):
        return self.cerebro.calienta()

    def procesa(self, texto):
        """Generador de eventos:
        {"tipo": "estado", "estado": "pensando" | "buscando" | "hablando"}
        {"tipo": "trozo", "texto": ...}            trozo de respuesta listo para la voz
        {"tipo": "fin", "accion": ..., "detalle": ..., "primera": s, "total": s}"""
        with self._cerrojo:
            yield from self._procesa(texto)

    def _procesa(self, texto):
        t0 = time.perf_counter()
        r = memoria.intenta(texto)                # «me llamo…», «¿cómo me llamo?», «recuerda que…»
        if r:
            respuesta, cambio = r
            if cambio:
                self.cerebro.actualiza_sistema()
                self.cerebro.historial.clear()
            yield {"tipo": "estado", "estado": "hablando"}
            yield {"tipo": "trozo", "texto": respuesta}
            yield self._fin("memoria", "", t0, t0)
            return

        accion, datos = enrutador.decide(texto)
        if accion == "video":
            yield from self._video(*datos, t0=t0)
            return
        if accion != "charla":
            detalle = ""
            if accion == "web":
                yield {"tipo": "estado", "estado": "buscando"}
                yield {"tipo": "trozo", "texto": "Lo busco…"}
            else:
                yield {"tipo": "estado", "estado": "pensando"}
            try:
                if accion == "reloj":
                    respuesta = datos
                elif accion == "web":
                    respuesta, tb, d = web.responde(datos)
                    detalle = f"búsqueda {tb:.1f} s · {d}"
                else:
                    respuesta = enrutador.responde_fuente(accion, datos)
            except Exception as e:                # sin red, clave errónea, servicio caído…
                respuesta = "No he podido consultarlo ahora mismo."
                detalle = f"error: {e}"
            primera = time.perf_counter()
            yield {"tipo": "estado", "estado": "hablando"}
            yield {"tipo": "trozo", "texto": respuesta}
            yield self._fin(accion, detalle, t0, primera)
            return

        yield {"tipo": "estado", "estado": "pensando"}
        primera = None
        for trozo in self.cerebro.responde(texto):
            if primera is None:
                primera = time.perf_counter()
                yield {"tipo": "estado", "estado": "hablando"}
            yield {"tipo": "trozo", "texto": trozo}
        u = self.cerebro.ultimo
        detalle = (f"lectura {u.get('tokens_leidos', 0)} tokens en {u.get('lectura_s', 0):.1f} s · "
                   f"generación {u.get('tok_s', 0):.1f} tok/s")
        yield self._fin("charla", detalle, t0, primera or time.perf_counter())

    def _video(self, orden, consulta, t0):
        """YouTube: la pantalla recibe la lista de resultados y los reproduce (evento «video»)."""
        if orden == "cerrar":
            yield {"tipo": "video", "cerrar": True}
            yield {"tipo": "estado", "estado": "hablando"}
            yield {"tipo": "trozo", "texto": "Cerrado."}
            yield self._fin("video", "cerrar", t0, time.perf_counter())
            return
        yield {"tipo": "estado", "estado": "buscando"}
        lista = video.busca(consulta)
        primera = time.perf_counter()
        yield {"tipo": "estado", "estado": "hablando"}
        if not lista:
            yield {"tipo": "trozo", "texto": f"No encuentro vídeos de «{consulta}»."}
            yield self._fin("video", "sin resultados", t0, primera)
            return
        try:                                       # que la música no tape el vídeo
            if musica.configurado() and musica.estado().get("estado") == "sonando":
                musica.accion("pause")
        except Exception:
            pass
        video.prepara(lista[0]["id"])            # yt-dlp tarda unos segundos: que empiece ya
        yield {"tipo": "video", "lista": lista}
        canal = f", de {lista[0]['canal']}" if lista[0].get("canal") else ""
        yield {"tipo": "trozo", "texto": f"Pongo «{lista[0]['titulo']}»{canal}."}
        yield self._fin("video", f"{len(lista)} resultados", t0, primera)

    @staticmethod
    def _fin(accion, detalle, t0, primera):
        ahora = time.perf_counter()
        return {"tipo": "fin", "accion": accion, "detalle": detalle,
                "primera": round(primera - t0, 2), "total": round(ahora - t0, 2)}
