import pandas as pd
import time
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# ── Configuración ──────────────────────────────────────────────
URL_FORM    = "https://the-paul2002.github.io/Proyecto-IA-/Homework1/"
URL_DATASET = "https://docs.google.com/spreadsheets/d/1EjaoSJKdzdUBNF3XJZuTlxA21D-0vy0wkGaMR8wHVgs/export?format=csv"
WAIT_TIME   = 10
GENEROS_VALIDOS = {"Masculino", "Femenino"}

# ── Setup driver ───────────────────────────────────────────────
def crear_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# ── Setear campo date via JavaScript ──────────────────────────
def fecha_js(driver, element_id, valor_date):
    driver.execute_script(
        f"document.getElementById('{element_id}').value = '{valor_date}';"
    )

# ── Registrar un empleado ──────────────────────────────────────
def registrar_empleado(driver, wait, row):
    try:
        driver.get(URL_FORM)
        time.sleep(1.5)

        def escribir(element_id, valor):
            el = wait.until(EC.presence_of_element_located((By.ID, element_id)))
            driver.execute_script("arguments[0].scrollIntoView(true);", el)
            time.sleep(0.3)
            el.clear()
            el.send_keys(str(valor))

        def dropdown(element_id, valor):
            el = wait.until(EC.presence_of_element_located((By.ID, element_id)))
            driver.execute_script("arguments[0].scrollIntoView(true);", el)
            time.sleep(0.3)
            Select(el).select_by_visible_text(str(valor).strip())

        escribir("nombres", row["apellidos_nombres"])
        escribir("dni", str(row["dni"]))
        fecha_js(driver, "fecha_nacimiento", pd.to_datetime(row["fecha_nacimiento"]).strftime("%Y-%m-%d"))
        dropdown("genero", str(row["genero"]).strip())
        escribir("telefono", str(row["telefono"]))
        escribir("correo", str(row["correo"]))
        dropdown("area",     str(row["area"]))
        dropdown("puesto",   str(row["puesto"]))
        dropdown("contrato", str(row["contrato"]))
        dropdown("sede",     str(row["sede"]))
        fecha_js(driver, "fecha_ingreso", pd.to_datetime(row["fecha_ingreso"]).strftime("%Y-%m-%d"))

        modalidad = str(row["modalidad"]).strip()
        for radio in driver.find_elements(By.NAME, "modalidad"):
            if radio.get_attribute("value") == modalidad:
                driver.execute_script("arguments[0].click();", radio)
                break

        btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'Registrar')]")))
        driver.execute_script("arguments[0].scrollIntoView(true);", btn)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(1.5)

        return True, None

    except Exception as e:
        return False, str(e)

# ── Main ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Cargando dataset...")
    df = pd.read_csv(URL_DATASET)
    print(f"Registros cargados: {len(df)}")

    driver = crear_driver()
    wait   = WebDriverWait(driver, WAIT_TIME)

    exitosos    = 0
    fallidos    = 0
    omitidos    = 0
    errores     = []
    omitidos_log = []

    for i, row in df.iterrows():
        genero = str(row["genero"]).strip()

        # Validar género antes de intentar registrar
        if genero not in GENEROS_VALIDOS:
            omitidos += 1
            omitidos_log.append({
                "registro": i + 1,
                "nombre": row["apellidos_nombres"],
                "razon": f"Género '{genero}' no disponible en el formulario"
            })
            print(f"[{i+1}/50] Omitido: {row['apellidos_nombres']} — género '{genero}' no válido")
            continue

        print(f"[{i+1}/50] Registrando: {row['apellidos_nombres']}...")
        ok, error = registrar_empleado(driver, wait, row)

        if ok:
            exitosos += 1
            print(f"  ✓ OK")
        else:
            fallidos += 1
            errores.append({"registro": i+1, "nombre": row["apellidos_nombres"], "error": error})
            print(f"  ✗ Error: {error}")

    driver.quit()

    print(f"\n── Resumen ──")
    print(f"  Total procesados:  {len(df)}")
    print(f"  Exitosos:          {exitosos}")
    print(f"  Omitidos (género): {omitidos}")
    print(f"  Fallidos (error):  {fallidos}")

    os.makedirs("parte1_peoplesync/output", exist_ok=True)
    with open("parte1_peoplesync/output/log.txt", "w", encoding="utf-8") as f:
        f.write(f"Total: {len(df)}\nExitosos: {exitosos}\nOmitidos: {omitidos}\nFallidos: {fallidos}\n\n")

        if omitidos_log:
            f.write("── Omitidos por inconsistencia de género ──\n")
            for o in omitidos_log:
                f.write(f"  Registro {o['registro']} - {o['nombre']}: {o['razon']}\n")

        if errores:
            f.write("\n── Errores de ejecución ──\n")
            for e in errores:
                f.write(f"  Registro {e['registro']} - {e['nombre']}: {e['error']}\n")

    print("Log guardado en parte1_peoplesync/output/log.txt")