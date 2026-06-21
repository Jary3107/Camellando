# Camellando - Conectando Trabajo Local

Plataforma web interactiva desarrollada con **FastAPI** y **SQLAlchemy** diseñada para conectar a trabajadores independientes con clientes locales de forma rápida, sencilla y directa. El proyecto incluye un backend RESTful y un frontend de página única (SPA) moderno y responsivo hecho con HTML5, CSS3 y JavaScript vanilla.

---

## Características del Proyecto

* **Doble Tipo de Rol:** Soporte para registro e inicio de sesión como **Cliente** o **Trabajador**.
* **Gestión de Servicios:** Los trabajadores pueden ofrecer servicios, detallar su descripción, categoría, tarifa y actualizar o eliminar sus publicaciones.
* **Búsqueda Dinámica:** Los clientes pueden buscar y filtrar servicios disponibles por categoría en tiempo real.
* **Flujo de Contratación:** Los clientes pueden enviar propuestas de contratación con un precio y detalles de la solicitud. Los trabajadores pueden revisar, aceptar, rechazar o marcar como completados dichos contratos.
* **Seguridad de Datos:** Las contraseñas se almacenan de forma segura utilizando la técnica de derivación de clave con salt **PBKDF2-SHA256**.
* **Persistencia en la Nube:** Configurado para conectarse a una base de datos PostgreSQL hospedada en **Supabase** mediante variables de entorno.

---

## Estructura del Proyecto

```text
crud-estudiantes-xampp/
│
├── main.py               # Servidor FastAPI, modelos de base de datos, esquemas y endpoints
├── requirements.txt      # Dependencias del proyecto (FastAPI, SQLAlchemy, psycopg2-binary, etc.)
├── Dockerfile            # Configuración de empaquetado Docker
├── docker-compose.yml    # Orquestación de servicios Docker
├── .env.example          # Plantilla de variables de entorno
│
└── static/               # Carpeta del Frontend (SPA)
    ├── index.html        # Estructura visual de la interfaz SPA
    ├── style.css         # Estilos visuales personalizados (badges, grids, glassmorphism)
    └── app.js            # Consumo de la API, manejo de DOM y control de sesión
```

---

## Configuración y Ejecución

### 1. Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto basándote en `.env.example` y rellénalo con tu URL de Supabase y llave secreta:
```env
DATABASE_URL=postgresql://postgres.xxxx:tu_contraseña_supabase@aws-0-us-east-1.pooler.supabase.com:6543/postgres
SECRET_KEY=tu_llave_secreta_para_tokens
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
APP_ENV=development
```

### 2. Ejecución Local

#### Crear entorno virtual e instalar dependencias:
* **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```
* **Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

#### Iniciar el servidor de desarrollo:
```bash
uvicorn main:app --reload
```
Una vez ejecutado, abre [http://127.0.0.1:8000](http://127.0.0.1:8000) en tu navegador para ver la interfaz de Camellando.

---

### 3. Ejecución con Docker Compose

Si prefieres ejecutar el proyecto utilizando contenedores Docker, asegúrate de tener Docker instalado y ejecuta:
```bash
docker-compose up --build
```
El servidor web estará disponible en [http://127.0.0.1:8000](http://127.0.0.1:8000).
