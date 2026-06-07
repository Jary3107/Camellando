# Camellando 

API básica e intuitiva en FastAPI para conectar trabajadores independientes con usuarios que buscan servicios. Diseñada específicamente como un primer avance realizado en 3 días de desarrollo para facilitar su sustentación universitaria.

---

## Integrantes del Grupo

* Emanuel González Henao
* Luis Miguel Osorio Marín
* Jary Alejandra Preston Oliveros
* Julián Zuluaga Castillo

---

## Estructura del Proyecto

```
crud-estudiantes-xampp/
│
├── main.py               # Base de datos, tablas, esquemas y endpoints
├── Dockerfile            # Configuración Docker básica
├── docker-compose.yml    # Orquestación de Docker
├── requirements.txt      # Solo 3 Dependencias (FastAPI, Uvicorn, SQLAlchemy)
└── README.md             # Guía del proyecto
```

## Configuración y Ejecución

### 1. Crear entorno e instalar dependencias
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


## Cuentas Semilla Iniciales

* Trabajador:`juan@example.com` | Clave:`123`
* Cliente:`carlos@example.com` | Clave:`123`
