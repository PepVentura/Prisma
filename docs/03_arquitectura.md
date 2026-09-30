# 03 — Arquitectura
```text
Waveshare 7"
     │
     ▼
Raspberry Pi 5
 ├── STT / LLM / TTS
 ├── Avatar
 ├── Micrófonos
 ├── LEDs
 └── DAC ──► KABD-250 ──► DMA105-4

DMA105-PR = parte trasera de la cámara acústica
```

Alimentación:
```text
24 V externo
 ├── KABD-250
 └── Buck 24→5 V ──► Pi / pantalla / periféricos
```
