# HW01 — Automatización, APIs y Análisis de Datos
**Curso:** Data Science con Python — Universidad del Pacífico (2026-02)  
**Estudiante:** Henry Llupton 
**Issue:** [#181](https://github.com/d2cml-ai/Data-Science-Python/issues/181)  

---

## Estructura del repositorio

```
HW01-DS-Python/
├── parte1_peoplesync/
│   ├── bot_peoplesync.py
│   └── output/
│       └── log.txt
├── parte2_sunat/
│   ├── scraper_sunat.py
│   └── output/
│       └── tipo_cambio_sunat.csv
├── parte3_lichess/
│   ├── analisis_partidas.py
│   ├── torneos.py
│   ├── .env.example
│   └── output/
│       ├── partidas.csv
│       ├── estadisticas.csv
│       ├── resultados.png
│       ├── resultados_color.png
│       └── rating_tiempo.png
├── .gitignore
└── README.md
```
---

## Parte 1 — RPA PeopleSync

Bot de automatización con Selenium que registra empleados en el formulario [PeopleSync HRIS](https://the-paul2002.github.io/Proyecto-IA-/Homework1/) a partir de un dataset de Google Sheets.

### Requisitos
```bash
pip install selenium webdriver-manager pandas
```

### Configuración
En `bot_peoplesync.py` puedes modificar:
- `URL_FORM` — URL del formulario
- `URL_DATASET` — URL del dataset en Google Sheets
- `GENEROS_VALIDOS` — valores de género aceptados por el formulario

### Ejecución
```bash
python parte1_peoplesync/bot_peoplesync.py
```

### Resultados
- **24 registros** cargados exitosamente
- **26 registros** omitidos por género no disponible en el formulario (`No binario`, `Prefiero no indicar`)
- **0 errores** de ejecución
- Log detallado en `parte1_peoplesync/output/log.txt`

### Notas técnicas
- Se usa `execute_script` para clicks y scroll en Mac (evita `element not interactable`)
- Las fechas se setean vía JavaScript para compatibilidad cross-platform
- Los registros con género inválido se omiten y se documentan en el log, sin detener el proceso

---

## Parte 2 — Web Scraping SUNAT

Scraper con Selenium que extrae el tipo de cambio oficial (compra/venta) desde enero 2024 hasta el mes actual desde el portal [SUNAT](https://e-consulta.sunat.gob.pe/cl-at-ittipcam/tcS01Alias).

### Requisitos
```bash
pip install selenium webdriver-manager pandas python-dateutil
```

### Configuración
En `scraper_sunat.py` puedes modificar:
- `FECHA_INICIO` — mes y año de inicio (por defecto `2024-01-01`)
- `FECHA_FIN` — mes y año de fin (por defecto el mes actual)

### Ejecución
```bash
python parte2_sunat/scraper_sunat.py
```

### Resultados
- **960 registros** extraídos
- **Período:** 2024-01-01 → 2026-08-25
- **32 meses** procesados sin errores
- CSV consolidado en `parte2_sunat/output/tipo_cambio_sunat.csv`

### Notas técnicas
- Navegación mes a mes usando botones `js-cal-prev` / `js-cal-next`
- Filtra celdas con clase `calendar-day current` para evitar capturar días de relleno de otros meses
- Los días sin dato (feriados, fines de semana sin publicación) se omiten automáticamente

---

## Parte 3 — Lichess API

### Parte A — Análisis de partidas

Script que conecta a la API de Lichess, descarga partidas de un usuario configurable, genera estadísticas y visualizaciones.

#### Requisitos
```bash
pip install requests pandas matplotlib python-dotenv
```

#### Configuración
Crea un archivo `.env` basado en `.env.example`:LICHESS_TOKEN=tu_token_aqui


#### Ejecución
```bash
python parte3_lichess/analisis_partidas.py
```

Genera:
- Estadísticas de resultados, rating, color y modo de juego
- 3 gráficos matplotlib
- CSVs exportados en `parte3_lichess/output/`

### Parte B — Automatización de torneos

Script que crea torneos semanales automáticamente vía la API de Lichess.

#### Ejecución
```bash
# Modo simulación (no crea torneos reales)
DRY_RUN=True python parte3_lichess/torneos.py

# Modo real
DRY_RUN=False python parte3_lichess/torneos.py
```

---

## Variables de entorno

El archivo `.env.example` está en `parte3_lichess/`. Copia y renómbralo como `.env` en la misma carpeta:

```bash
cp parte3_lichess/.env.example parte3_lichess/.env
```

Luego edita `parte3_lichess/.env` y pon tu token de Lichess: LICHESS_TOKEN=tu_token_aqui

**Nunca subas el archivo `.env` al repositorio.**

---

## Ejecución automática — Windows Task Scheduler

Las partes 1 y 2 están configuradas para ejecutarse automáticamente con Windows Task Scheduler.

**Pasos generales:**
1. Abrir Task Scheduler → Crear tarea básica
2. Configurar el trigger (diario / semanal según el caso)
3. En Acción: `python.exe` con argumento la ruta absoluta al script
4. Verificar que el intérprete de Python sea el correcto

Ver evidencia de configuración en el video de presentación.
LINK: https://drive.google.com/drive/folders/1200g-nzm2lyiC0dFbROkhaLZbd_RQgRA?usp=sharing
