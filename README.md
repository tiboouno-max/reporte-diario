# Reporte Diario de Calidad del Aire - Automatización

Este proyecto automatiza la generación, guardado y envío por correo del reporte diario de calidad del aire de la Secrretaria de Medio Ambiente Desarrollo Sustentable y Ordenamiento Territorial.

El sistema se ejecuta automáticamente mediante GitHub Actions y también puede ejecutarse localmente para pruebas y mantenimiento.

---

# Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Requisitos Previos](#requisitos-previos)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Instalación y Configuración Local](#instalación-y-configuración-local)
5. [Configuración en GitHub Actions](#configuración-en-github-actions)
6. [Uso Manual (Workflow Dispatch)](#uso-manual-workflow-dispatch)
7. [Programación Automática (Cron)](#programación-automática-cron)
8. [Capturas de Pantalla Sugeridas](#capturas-de-pantalla-sugeridas)
9. [Solución de Problemas Comunes](#solución-de-problemas-comunes)
10. [Notas de Seguridad](#notas-de-seguridad)

---

# Descripción General

El script `scraper.py` realiza automáticamente las siguientes acciones:

1. Inicia sesión en el sitio oficial de calidad del aire.
2. Accede al panel de reportes.
3. Selecciona municipios específicos:
   - Atlixco
   - Texmelucan
   - Tehuacán
4. Genera un PDF con el reporte diario.
5. Guarda el PDF dentro de la carpeta `reportes/`.
6. Envía automáticamente el PDF por correo electrónico.
7. Se ejecuta diariamente mediante GitHub Actions.

---

# Requisitos Previos

- Python 3.10 o superior
- Google Chrome instalado
- Git instalado
- Cuenta Gmail con contraseña de aplicación (debido a la transeferencia de este correo electronico se desactivo la verificacion en 2 pasos, lo que provoco que las contraseñas de aplicacion que es necasaria para el envio de correo electronicos se desactivo, se debera reactivar la verificacion en 2 pasos e introducir una nueva contraseña de aplicacion e introducirla en secrets and variables )
- Credenciales del sistema de calidad del aire
- (Opcional) entorno virtual `venv`

---

# Estructura del Proyecto

```text
.
├── .github
│   └── workflows
│       └── daily_report.yaml
├── reportes/
├── requirements.txt
├── scraper.py
└── README.md
```

---

# Instalación y Configuración Local

## 1. Clonar el repositorio

```bash
git clone https://github.com/ManuelRuizJ/reporte-diaria.git
cd reporte-diaria
```

---

## 2. Crear entorno virtual (recomendado)

### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows PowerShell

```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

---

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 4. Crear archivo `.env`

Crear un archivo `.env` en la raíz del proyecto:
```env
USUARIO=usuario
CONTRASENA=contraseña

EMAIL_USER=tiboouno@gmail.com
EMAIL_PASSWORD=xxxx xxxx xxxx xxxx

EMAIL_TO_1=destinatario1@example.com
EMAIL_TO_2=destinatario2@example.com
EMAIL_TO_3=destinatario3@example.com
```

---

## Nota importante

La contraseña de Gmail debe ser una:

- Contraseña de aplicación
- Generada desde:

```text
https://myaccount.google.com/apppasswords
```

Requiere autenticación en dos pasos habilitada.

---

# Ejecutar el Script Localmente

```bash
python scraper.py
```

---

## Salida esperada

```text
Iniciando...
PDF guardado en: reportes/Reporte diario (calidad del aire) 2026052817.pdf
Correo enviado correctamente
Hecho
```

---

# Modo de Prueba Local

Agregar en `.env`:

```env
LOCAL_TEST=true
```

En este modo:

- No se envían correos reales
- No se hace commit automático
- Usa la carpeta `reportes_prueba/`

---

# Configuración en GitHub Actions

Agregar los siguientes secretos en:

```text
GitHub → Settings → Secrets and variables → Actions
```

---

## Secrets requeridos

| Nombre | Descripción |
|---|---|
| `USUARIO` | Usuario de la pagina |
| `CONTRASENA` | Contraseña de la pagina |
| `EMAIL_USER` | Correo Gmail |
| `EMAIL_PASSWORD` | Contraseña de aplicación |
| `EMAIL_TO_1` | Destinatario 1 |
| `EMAIL_TO_2` | Destinatario 2 |
| `EMAIL_TO_3` | Destinatario 3 |

---

# Workflow de GitHub Actions

Archivo:

```text
.github/workflows/daily_report.yaml
```

---

## Ejemplo básico

```yaml
name: Reporte Diario ICA

on:
  schedule:
    - cron: "28 22 * * *"

  workflow_dispatch:

jobs:
  generar-pdf:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"

      - name: Instalar dependencias
        run: pip install -r requirements.txt

      - name: Ejecutar script
        run: python scraper.py
```

---

# Uso Manual (Workflow Dispatch)

1. Abrir pestaña **Actions**
2. Seleccionar workflow:
   - `Reporte Diario ICA`
3. Presionar:
   - `Run workflow`

---

# Programación Automática (Cron)

Cron configurado:

```yaml
- cron: "28 22 * * *"
```

---

## Equivalencia horaria

| UTC | Hora México |
|---|---|
| 22:28 UTC | 4:28 PM |

---

# Capturas de Pantalla Recomendadas

- Estructura del proyecto
- Ejecución local exitosa
- Carpeta `reportes/`
- Secrets de GitHub
- Workflow ejecutándose
- PDF generado
- Correo recibido

---

# Solución de Problemas Comunes

## Error SMTP / Gmail

### Causa

Contraseña de aplicación inválida.

### Solución

Generar nueva contraseña desde Google App Passwords.

---

## No encuentra elementos Selenium

### Causa

Cambios en el HTML del sitio.

### Solución

Actualizar selectores `By.ID`, `By.XPATH`, etc.

---

## No se guarda el PDF

### Causa

Ruta incorrecta o permisos.

### Solución

Verificar carpeta `reportes/`.

---

## El workflow no corre a tiempo

### Causa

Diferencia entre UTC y hora local, de igual forma considerar un posible delay derivado del mismo GitHub Actions

### Solución

Modificar hora en el cronjob en el `daily_report.yaml`

---

# Notas de Seguridad

- Nunca subir `.env`
- Mantener `.env` dentro de `.gitignore`
- No compartir contraseñas reales
- Usar únicamente GitHub Secrets en producción
