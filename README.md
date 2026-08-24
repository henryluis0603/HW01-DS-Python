# HW01-DS-Python
Proyecto integrador: Automatización, APIs y Análisis de Datos  
Curso: Data Science con Python — Universidad del Pacífico 2026-2  
Autor: Henry Luis Llupton Capuñay

---

## Estructura del proyecto
HW01-DS-Python/
├── parte1_peoplesync/ # RPA con Selenium
├── parte2_sunat/ # Web Scraping SUNAT
├── parte3_lichess/ # API Lichess
│ ├── analisis_partidas.py
│ ├── torneos.py
│ └── output/ # CSVs y gráficos generados
├── .env.example
└── README.md

---

## Requisitos
- Python 3.10+
- Google Chrome + ChromeDriver (partes 1 y 2)

## Instalación
```bash
pip install requests pandas matplotlib selenium python-dotenv
```

## Configuración
1. Copia `.env.example` a `.env`
2. Obtén tu token en lichess.org/account/oauth/token (scope: `tournament:write`)
3. Pega el token en `.env`

---

## Parte 3 — Lichess API

### Análisis de partidas
```bash
python3 parte3_lichess/analisis_partidas.py
```
Configurable: cambia `USERNAME` y `N_GAMES` en las líneas 11-12.

### Automatización de torneos
```bash
python3 parte3_lichess/torneos.py
```
Por defecto corre en modo `DRY_RUN=True` (simulación). Cambia a `False` para crear torneos reales.

---

## Partes 1 y 2
*(en desarrollo)*