# Coyuntura SGIC

Sistema de monitoreo de eventos viales en Guatemala (bloqueos, manifestaciones, accidentes, etc.), con mapa en tiempo real, matriz institucional de eventos y panel administrativo.

**Stack:** FastAPI + SQLite (backend) · Vue 3 + Vite + Tailwind (frontend) · Leaflet (mapa)

---

## 1. Requisitos previos

Instala esto antes de continuar:

| Herramienta | Versión mínima | Verificar con |
|---|---|---|
| [Python](https://www.python.org/downloads/) | 3.11 | `python --version` |
| [Node.js](https://nodejs.org/) | 18 (recomendado 20+) | `node --version` |
| [Git](https://git-scm.com/downloads) | cualquiera reciente | `git --version` |

No necesitas instalar SQLite aparte: Python ya lo incluye.

---

## 2. Clonar el repositorio

```bash
git clone https://github.com/pc66qwerty/Coyuntura-SGIC-.git
cd Coyuntura-SGIC-
```

El proyecto tiene dos carpetas principales: `backend/` (API) y `frontend/` (interfaz web). Se levantan por separado, en dos terminales distintas.

---

## 3. Backend (API)

Abre una terminal en la carpeta `backend/`:

```bash
cd backend
```

### 3.1. Crear y activar el entorno virtual

```bash
python -m venv .venv
```

Activarlo:

- **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
- **Windows (cmd):** `.venv\Scripts\activate.bat`
- **Mac/Linux:** `source .venv/bin/activate`

Verás `(.venv)` al inicio de la línea de la terminal cuando esté activo.

### 3.2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3.3. Variables de entorno

Copia el archivo de ejemplo:

```bash
cp .env.example .env      # Mac/Linux
copy .env.example .env    # Windows
```

Por defecto no necesitas cambiar nada para desarrollo local. Si quieres, puedes editar `JWT_SECRET` en `.env` (no es obligatorio en local).

### 3.4. Levantar el servidor

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- La primera vez que corre, crea automáticamente la base de datos SQLite en `backend/data/monitorvial.db`, las tablas, los tipos de evento por defecto y un usuario administrador.
- Déjalo corriendo en esta terminal. La API queda disponible en **http://localhost:8000** (documentación interactiva en `http://localhost:8000/docs`).

**Usuario administrador por defecto** (se crea solo, en el primer arranque):

```
correo:      admin@admin.com
contraseña:  12345678
```

Puedes usarlo para entrar al panel y luego crear cuentas reales para el resto del equipo desde la sección "Usuarios".

---

## 4. Frontend (interfaz web)

Abre **otra terminal** (deja la del backend corriendo) en la carpeta `frontend/`:

```bash
cd frontend
```

### 4.1. Instalar dependencias

```bash
npm install
```

### 4.2. Levantar el servidor de desarrollo

```bash
npm run dev
```

Vite mostrará una URL, normalmente **http://localhost:5173**. Ábrela en el navegador.

El frontend ya está configurado (`vite.config.js`) para redirigir automáticamente las peticiones `/api` y `/storage` hacia `http://localhost:8000`, así que **no necesitas tocar ninguna variable de entorno** para que el frontend hable con el backend en local.

---

## 5. Uso

1. Con ambos servidores corriendo, entra a **http://localhost:5173**.
2. Inicia sesión con el usuario administrador (`admin@admin.com` / `12345678`).
3. Acepta los términos y condiciones (solo la primera vez).
4. Desde el botón **"Panel"** llegas al panel de administración para registrar y editar eventos, gestionar usuarios y tipos de evento.

---

## 6. Estructura del proyecto

```
Coyuntura-SGIC-/
├── backend/
│   ├── main.py            # API completa (FastAPI): modelos, rutas, lógica
│   ├── requirements.txt   # Dependencias Python
│   ├── data/               # Base de datos SQLite (se crea sola, no se sube a git)
│   └── storage/            # Fotos subidas de los eventos (no se sube a git)
├── frontend/
│   ├── src/
│   │   ├── views/           # Páginas (Dashboard, Welcome, Users, TiposEvento, etc.)
│   │   ├── components/      # Componentes reutilizables (mapa, formularios, modales)
│   │   ├── stores/          # Estado global (auth) con Pinia
│   │   ├── composables/     # Lógica reutilizable (tipos de evento, tema)
│   │   ├── data/             # Datos estáticos (departamentos/municipios de Guatemala)
│   │   └── router/          # Rutas de la SPA
│   └── package.json
└── docker-compose.yml      # Alternativa para levantar todo con Docker (ver abajo)
```

---

## 7. Alternativa: levantarlo con Docker

Si prefieren no instalar Python/Node localmente, también se puede levantar todo con Docker (requiere tener [Docker](https://www.docker.com/) instalado):

```bash
docker compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000

Con Docker los datos (base de datos y fotos) se guardan en volúmenes de Docker, no en las carpetas `backend/data`/`backend/storage`.

---

## 8. Problemas comunes

- **"Puerto 8000 (u otro) ya está en uso"**: hay otro proceso usándolo. Ciérralo o cambia el puerto en el comando de `uvicorn` (y ajusta el proxy en `vite.config.js` si cambias el del backend).
- **El frontend carga pero no trae datos / error de login**: revisa que la terminal del backend siga corriendo y sin errores.
- **Cambios en `tailwind.config.js` no se ven**: reinicia `npm run dev` (Tailwind a veces no recarga colores nuevos en caliente).
- **Errores raros después de hacer `git pull`**: vuelve a correr `pip install -r requirements.txt` y `npm install`, puede que haya dependencias nuevas.

---

## 9. Flujo de trabajo con Git

- La rama principal es `main`.
- Antes de empezar a trabajar: `git pull` para traer los últimos cambios.
- Hagan sus cambios, prueben en local, y avisen antes de hacer `git push` a `main` si van a tocar archivos que otros también estén editando, para evitar conflictos.
