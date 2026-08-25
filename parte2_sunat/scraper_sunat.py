import pandas as pd
import time
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ── Configuración ──────────────────────────────────────────────
URL_SUNAT    = "https://e-consulta.sunat.gob.pe/cl-at-ittipcam/tcS01Alias"
FECHA_INICIO = datetime(2024, 1, 1)   # Configurable
FECHA_FIN    = datetime.today()        # Hasta el mes actual
WAIT_TIME    = 15

# ── Setup driver ───────────────────────────────────────────────
def crear_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# ── Extraer datos del mes visible ──────────────────────────────
def extraer_mes(driver):
    registros = []
    # Solo celdas del mes actual, ignorando outside
    celdas = driver.find_elements(By.CSS_SELECTOR, "td.calendar-day.current[data-date]")
    for celda in celdas:
        fecha_raw = celda.get_attribute("data-date")
        if not fecha_raw:
            continue
        fecha = fecha_raw[:10]
        eventos = celda.find_elements(By.CSS_SELECTOR, ".event")
        if len(eventos) >= 2:
            compra = eventos[0].text.replace("Compra", "").strip()
            venta  = eventos[1].text.replace("Venta", "").strip()
            try:
                registros.append({
                    "fecha":  fecha,
                    "compra": float(compra),
                    "venta":  float(venta)
                })
            except ValueError:
                pass
    return registros

# ── Obtener mes/año actual del calendario ──────────────────────
def mes_actual_calendario(driver):
    # Solo celdas del mes actual, ignorando las de relleno (outside)
    celdas = driver.find_elements(By.CSS_SELECTOR, "td.calendar-day.current[data-date]")
    for celda in celdas:
        fecha_raw = celda.get_attribute("data-date")
        if fecha_raw:
            return fecha_raw[:7]  # YYYY-MM
    return None

# ── Navegar al mes objetivo ────────────────────────────────────
def ir_a_mes(driver, wait, año_objetivo, mes_objetivo):
    objetivo = datetime(año_objetivo, mes_objetivo, 1)

    for _ in range(100):
        mes_str = mes_actual_calendario(driver)
        if not mes_str:
            time.sleep(1.5)
            continue

        año_actual, mes_actual = map(int, mes_str.split("-"))
        actual = datetime(año_actual, mes_actual, 1)

        if actual == objetivo:
            # Esperar a que las celdas del mes objetivo estén cargadas
            time.sleep(2)
            return

        if actual > objetivo:
            btn = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.js-cal-prev")))
        else:
            btn = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.js-cal-next")))

        driver.execute_script("arguments[0].click();", btn)
        time.sleep(1.5)

    raise Exception(f"No se pudo navegar a {mes_objetivo:02d}/{año_objetivo}")

# ── Main ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Iniciando scraper SUNAT...")
    print(f"Rango: {FECHA_INICIO.strftime('%b %Y')} → {FECHA_FIN.strftime('%b %Y')}")

    driver = crear_driver()
    wait   = WebDriverWait(driver, WAIT_TIME)

    driver.get(URL_SUNAT)
    time.sleep(3)

    # Generar lista de meses a scrapear (del más antiguo al más reciente)
    meses = []
    cursor = FECHA_INICIO.replace(day=1)
    fin    = FECHA_FIN.replace(day=1)
    while cursor <= fin:
        meses.append((cursor.year, cursor.month))
        cursor += relativedelta(months=1)

    print(f"Total de meses a procesar: {len(meses)}")

    todos_los_registros = []

    for año, mes in meses:
        print(f"Procesando {mes:02d}/{año}...")
        try:
            ir_a_mes(driver, wait, año, mes)
            time.sleep(1.5)
            registros = extraer_mes(driver)
            todos_los_registros.extend(registros)
            print(f"  → {len(registros)} días con dato")
        except Exception as e:
            print(f"  ✗ Error en {mes:02d}/{año}: {e}")

    driver.quit()

    # Consolidar y exportar
    df = pd.DataFrame(todos_los_registros)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.sort_values("fecha").drop_duplicates("fecha").reset_index(drop=True)

    os.makedirs("parte2_sunat/output", exist_ok=True)
    ruta_csv = "parte2_sunat/output/tipo_cambio_sunat.csv"
    df.to_csv(ruta_csv, index=False, encoding="utf-8")

    print(f"\n── Resumen ──")
    print(f"  Total días extraídos: {len(df)}")
    print(f"  Período: {df['fecha'].min().date()} → {df['fecha'].max().date()}")
    print(f"  CSV guardado en: {ruta_csv}")
    print(df.head(10).to_string(index=False))