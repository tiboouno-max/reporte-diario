import os
import time
import datetime
import shutil
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver(download_dir):
    options = Options()
    if os.environ.get('GITHUB_ACTIONS'):
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--window-size=1280,1024")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def enviar_correo(ruta_pdf):
    """Envía el PDF por correo usando SMTP de Gmail"""
    email_user = os.environ.get("EMAIL_USER")
    email_password = os.environ.get("EMAIL_PASSWORD")
    destinatarios = []
    for i in range(1, 4):
        dest = os.environ.get(f"EMAIL_TO_{i}")
        if dest:
            destinatarios.append(dest)
    if not destinatarios:
        print("⚠️ No hay destinatarios configurados, se omite envío")
        return
    if not email_user or not email_password:
        print("⚠️ Credenciales de correo no configuradas, se omite envío")
        return

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = ", ".join(destinatarios)
    msg['Subject'] = f"Reporte diario de calidad del aire - {datetime.datetime.now().strftime('%d/%m/%Y')}"

    cuerpo = f"""Se adjunta el reporte diario de calidad del aire correspondiente al día de hoy.

Reporte generado automáticamente el {datetime.datetime.now().strftime('%d/%m/%Y')}
"""
    msg.attach(MIMEText(cuerpo, 'plain'))

    with open(ruta_pdf, "rb") as adjunto:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(adjunto.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename={os.path.basename(ruta_pdf)}")
        msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_password)
        server.send_message(msg)
        server.quit()
        print(f"✅ Correo enviado a {', '.join(destinatarios)}")
    except Exception as e:
        print(f"❌ Error al enviar correo: {e}")

def generar_reporte():
    fecha = datetime.datetime.now().strftime("%Y%m%d")
    hora = datetime.datetime.now().strftime("%H")
    download_dir = os.path.abspath(f"descargas_{fecha}")
    os.makedirs(download_dir, exist_ok=True)
    driver = setup_driver(download_dir)
    wait = WebDriverWait(driver, 15)

    driver.get("https://calidaddelaire.puebla.gob.mx/views/login.php")
    wait.until(EC.presence_of_element_located((By.ID, "form_iniciar_sesion")))
    driver.find_element(By.NAME, "user").send_keys(os.environ["USUARIO"])
    driver.find_element(By.NAME, "pass").send_keys(os.environ["CONTRASENA"])
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    wait.until(EC.url_contains("administrator.php"))

    reporte_link = wait.until(EC.element_to_be_clickable((By.ID, "sidebar_generar_reporteICA")))
    driver.execute_script("arguments[0].click();", reporte_link)
    modal = wait.until(EC.visibility_of_element_located((By.ID, "modal_generar_reporteICA")))

    for chk_id in ["gricaha_habilitarATL2", "gricaha_habilitarTEX2", "gricaha_habilitarTEH2"]:
        chk = wait.until(EC.element_to_be_clickable((By.ID, chk_id)))
        if not chk.is_selected():
            driver.execute_script("arguments[0].click();", chk)

    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
    time.sleep(1)
    form = driver.find_element(By.ID, "form_generar_reporteica_horasacumuladas2")
    btn = form.find_element(By.XPATH, ".//button[contains(text(), 'Exportar a PDF')]")
    driver.execute_script("arguments[0].click();", btn)

    archivo = None
    for _ in range(20):
        archivos = [f for f in os.listdir(download_dir) if not f.endswith('.crdownload')]
        if archivos:
            archivo = archivos[0]
            break
        time.sleep(1)
    if not archivo:
        raise Exception("No se descargó el PDF")

    # Nombre del PDF definitivo
    nombre_pdf = f"Reporte diario (calidad del aire) {fecha}17.pdf"
    ruta_temporal = os.path.join(download_dir, archivo)
    ruta_destino_base = os.path.join("reportes", nombre_pdf)

    # Asegurar que la carpeta reportes existe
    os.makedirs("reportes", exist_ok=True)

    # Si ya existe, añadir contador
    contador = 1
    ruta_destino = ruta_destino_base
    while os.path.exists(ruta_destino):
        nombre_base = f"Reporte diario (calidad del aire) {fecha}17"
        nombre_pdf = f"{nombre_base}_{contador}.pdf"
        ruta_destino = os.path.join("reportes", nombre_pdf)
        contador += 1

    # Mover el archivo a reportes/
    shutil.move(ruta_temporal, ruta_destino)
    print(f"✅ PDF guardado en: {ruta_destino}")

    # Limpiar la carpeta de descarga temporal (opcional)
    try:
        shutil.rmtree(download_dir)
    except OSError:
        pass

    driver.quit()

    # Enviar correo con el PDF
    enviar_correo(ruta_destino)

    return ruta_destino

if __name__ == "__main__":
    print("🚀 Iniciando...")
    generar_reporte()
    print("✅ Hecho")