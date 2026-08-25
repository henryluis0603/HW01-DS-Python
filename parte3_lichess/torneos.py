import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")

# ── Configuración ──────────────────────────────────────────────
TOKEN   = os.getenv("LICHESS_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type":  "application/x-www-form-urlencoded"
}

DRY_RUN = True  # Cambiar a False para crear torneos reales

# ── Cronograma semanal ─────────────────────────────────────────
# Cada torneo: (dia_semana, hora, minuto, nombre, modo, minutos_partida, incremento, duracion_torneo)
# dia_semana: 0=lunes, 6=domingo
TORNEOS = [
    (0, 20, 0, "Lunes Blitz",    "blitz",   5, 0, 45),
    (2, 20, 0, "Miércoles Rapid","rapid",  10, 5, 60),
    (4, 20, 0, "Viernes Bullet", "bullet",  1, 0, 30),
    (6, 18, 0, "Domingo Chess960","chess960",5, 3, 45),
]

# ── Calcular próxima fecha para cada torneo ────────────────────
def proxima_fecha(dia_semana, hora, minuto):
    hoy = datetime.now()
    dias_hasta = (dia_semana - hoy.weekday()) % 7
    fecha = hoy + timedelta(days=dias_hasta)
    fecha = fecha.replace(hour=hora, minute=minuto, second=0, microsecond=0)
    if fecha <= hoy:
        fecha += timedelta(weeks=1)
    return fecha

# ── Crear torneo via API ───────────────────────────────────────
def crear_torneo(nombre, modo, clock_time, clock_increment, duracion, fecha_inicio):
    start_ts = int(fecha_inicio.timestamp() * 1000)

    payload = {
        "name":           nombre,
        "clockTime":      clock_time,
        "clockIncrement": clock_increment,
        "minutes":        duracion,
        "startDate":      start_ts,
        "variant":        modo if modo != "rapid" and modo != "blitz" and modo != "bullet" else "standard",
        "rated":          "true",
    }

    if DRY_RUN:
        print(f"[DRY-RUN] Torneo: {nombre} | Modo: {modo} | "
              f"Reloj: {clock_time}+{clock_increment} | "
              f"Duración: {duracion} min | Inicio: {fecha_inicio.strftime('%Y-%m-%d %H:%M')}")
        return None

    try:
        r = requests.post(
            "https://lichess.org/api/tournament",
            headers=HEADERS,
            data=payload
        )
        if r.status_code == 200:
            data = r.json()
            print(f"✓ Torneo creado: {nombre} → https://lichess.org/tournament/{data['id']}")
            return data
        else:
            print(f"✗ Error al crear '{nombre}': {r.status_code} - {r.text}")
            return None
    except Exception as e:
        print(f"✗ Excepción en '{nombre}': {e}")
        return None

# ── Main ───────────────────────────────────────────────────────
if __name__ == "__main__":
    modo_str = "DRY-RUN (simulación)" if DRY_RUN else "REAL"
    print(f"\n── Creando torneos semanales [{modo_str}] ──\n")

    creados  = 0
    omitidos = 0

    for dia, hora, minuto, nombre, modo, clock_t, clock_i, duracion in TORNEOS:
        fecha = proxima_fecha(dia, hora, minuto)

        if fecha <= datetime.now():
            print(f"⚠ Omitido '{nombre}' — la fecha ya pasó ({fecha.strftime('%Y-%m-%d %H:%M')})")
            omitidos += 1
            continue

        resultado = crear_torneo(nombre, modo, clock_t, clock_i, duracion, fecha)
        if resultado is not None or DRY_RUN:
            creados += 1

    print(f"\n── Resumen ──")
    print(f"  Torneos procesados: {creados}")
    print(f"  Torneos omitidos:   {omitidos}")