import requests
import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# ── Configuración ──────────────────────────────────────────────
USERNAME = "lance5500"
N_GAMES  = 100
TOKEN    = os.getenv("LICHESS_TOKEN")

HEADERS  = {
    "Accept": "application/x-ndjson",
    "Authorization": f"Bearer {TOKEN}"
}

# ── 1. Conexión a la API ───────────────────────────────────────
def obtener_partidas(username, n):
    url    = f"https://lichess.org/api/games/user/{username}"
    params = {"max": n}
    response = requests.get(url, headers=HEADERS, params=params, stream=True)
    print(f"Status code: {response.status_code}")
    
    partidas = []
    for line in response.iter_lines():
        if line:
            import json
            partidas.append(json.loads(line))
    print(f"Partidas obtenidas: {len(partidas)}")
    return partidas

# ── 2. Transformar a DataFrame ─────────────────────────────────
def procesar_partidas(partidas, username):
    registros = []
    for g in partidas:
        players = g.get("players", {})
        white   = players.get("white", {})
        black   = players.get("black", {})

        es_blanco = white.get("user", {}).get("name", "").lower() == username.lower()
        mi_lado   = white if es_blanco else black
        rival     = black if es_blanco else white

        resultado_raw = g.get("winner", "draw")
        if resultado_raw == "draw":
            resultado = "draw"
        elif (resultado_raw == "white" and es_blanco) or (resultado_raw == "black" and not es_blanco):
            resultado = "win"
        else:
            resultado = "loss"

        registros.append({
            "id":             g.get("id"),
            "fecha":          pd.to_datetime(g.get("createdAt"), unit="ms"),
            "resultado":      resultado,
            "color":          "white" if es_blanco else "black",
            "modo":           g.get("perf", "unknown"),
            "mi_rating":      mi_lado.get("rating"),
            "rival_rating":   rival.get("rating"),
        })
    return pd.DataFrame(registros)

# ── 3. Estadísticas ────────────────────────────────────────────
def mostrar_estadisticas(df):
    print("\n── Resultados ──")
    print(df["resultado"].value_counts())
    print("\n── Rating promedio ──")
    print(f"  Mi rating promedio:    {df['mi_rating'].mean():.1f}")
    print(f"  Rating rival promedio: {df['rival_rating'].mean():.1f}")
    print("\n── Por color ──")
    print(df.groupby("color")["resultado"].value_counts())
    print("\n── Por modo de juego ──")
    print(df["modo"].value_counts())

# ── 4. Visualizaciones ─────────────────────────────────────────
def generar_graficos(df, carpeta="parte3_lichess/output"):
    os.makedirs(carpeta, exist_ok=True)

    df["resultado"].value_counts().plot(kind="bar", color=["green","red","gray"])
    plt.title("Distribución de resultados")
    plt.xlabel("Resultado"); plt.ylabel("Cantidad")
    plt.tight_layout()
    plt.savefig(f"{carpeta}/resultados.png"); plt.clf()

    df_sorted = df.sort_values("fecha")
    plt.plot(df_sorted["fecha"], df_sorted["mi_rating"], marker="o", markersize=2)
    plt.title("Evolución del rating")
    plt.xlabel("Fecha"); plt.ylabel("Rating")
    plt.tight_layout()
    plt.savefig(f"{carpeta}/rating_tiempo.png"); plt.clf()

    df.groupby("color")["resultado"].value_counts().unstack().plot(kind="bar")
    plt.title("Resultados por color")
    plt.tight_layout()
    plt.savefig(f"{carpeta}/resultados_color.png"); plt.clf()

    print(f"Gráficos guardados en '{carpeta}/'")

# ── 5. Exportar CSV ────────────────────────────────────────────
def exportar_csv(df, carpeta="parte3_lichess/output"):
    os.makedirs(carpeta, exist_ok=True)
    df.to_csv(f"{carpeta}/partidas.csv", index=False)
    stats = df.groupby("resultado").size().reset_index(name="cantidad")
    stats.to_csv(f"{carpeta}/estadisticas.csv", index=False)
    print("CSVs exportados.")

# ── Main ───────────────────────────────────────────────────────
if __name__ == "__main__":
    partidas = obtener_partidas(USERNAME, N_GAMES)
    if not partidas:
        print("No se obtuvieron partidas. Verifica el username o el token.")
    else:
        df = procesar_partidas(partidas, USERNAME)
        mostrar_estadisticas(df)
        generar_graficos(df)
        exportar_csv(df)