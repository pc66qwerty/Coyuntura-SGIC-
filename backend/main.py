import os
import shutil
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

import bcrypt
import jwt
from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    inspect,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////app/data/monitovial.db")
JWT_SECRET = os.getenv("JWT_SECRET", "change_me_in_production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24 * 7  # 7 days
STORAGE_PATH = os.getenv("STORAGE_PATH", "/app/storage")

os.makedirs(STORAGE_PATH, exist_ok=True)
os.makedirs("/app/data", exist_ok=True)

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), default="lector")
    terms_accepted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Bloqueo(Base):
    __tablename__ = "bloqueos"
    id = Column(Integer, primary_key=True, index=True)
    direccion = Column(String(255), nullable=False)
    municipio = Column(String(255), nullable=False)
    departamento = Column(String(255), nullable=False)
    tipo_evento = Column(String(255), nullable=False)
    estado = Column(String(50), default="Activo")
    manifestantes_aproximados = Column(Integer, nullable=True)
    observaciones = Column(Text, nullable=True)
    foto_path = Column(String(512), nullable=True)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)

    # ── Inicio del evento (matriz institucional) ──────────────────────
    fecha_hora_inicio = Column(DateTime, nullable=True)
    referencia_inicio = Column(String(512), nullable=True)
    zona_inicio = Column(String(20), nullable=True)
    comisaria_inicio = Column(String(100), nullable=True)
    instrumentos = Column(Text, nullable=True)
    nivel_conflicto = Column(String(20), nullable=True)
    presencia_policial = Column(Text, nullable=True)
    cantidad_vehiculos = Column(String(100), nullable=True)
    demandas = Column(Text, nullable=True)
    actores = Column(String(255), nullable=True)
    lideres_vulnerables = Column(Text, nullable=True)

    # ── Finalización del evento ────────────────────────────────────────
    fecha_hora_fin = Column(DateTime, nullable=True)
    direccion_fin = Column(String(255), nullable=True)
    latitud_fin = Column(Float, nullable=True)
    longitud_fin = Column(Float, nullable=True)
    referencia_fin = Column(String(512), nullable=True)
    departamento_fin = Column(String(255), nullable=True)
    municipio_fin = Column(String(255), nullable=True)
    zona_fin = Column(String(20), nullable=True)
    comisaria_fin = Column(String(100), nullable=True)
    personas_fin = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class BloqueoFoto(Base):
    __tablename__ = "bloqueo_fotos"
    id = Column(Integer, primary_key=True, index=True)
    bloqueo_id = Column(Integer, ForeignKey("bloqueos.id"), nullable=False, index=True)
    path = Column(String(512), nullable=False)
    orden = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)


class TipoEvento(Base):
    __tablename__ = "tipos_evento"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    color = Column(String(7), nullable=False)
    color_light = Column(String(7), nullable=False)
    color_border = Column(String(7), nullable=False)
    icon_path = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


Base.metadata.create_all(bind=engine)


def _migrar_columnas_faltantes():
    """SQLite no agrega columnas nuevas a tablas existentes con create_all();
    aquí se revisan y agregan las que falten al modelo actual."""
    inspector = inspect(engine)
    with engine.begin() as conn:
        for tabla in Base.metadata.tables.values():
            columnas_existentes = {c["name"] for c in inspector.get_columns(tabla.name)}
            for columna in tabla.columns:
                if columna.name not in columnas_existentes:
                    tipo_sql = columna.type.compile(engine.dialect)
                    conn.execute(text(f"ALTER TABLE {tabla.name} ADD COLUMN {columna.name} {tipo_sql}"))


_migrar_columnas_faltantes()

# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

TIPOS_EVENTO_SEED = [
    {
        "nombre": "Emergencia",
        "color": "#dc2626",
        "color_light": "#fef2f2",
        "color_border": "#fca5a5",
        "icon_path": '<path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"/>',
    },
    {
        "nombre": "Accidente vial",
        "color": "#ea580c",
        "color_light": "#fff7ed",
        "color_border": "#fdba74",
        "icon_path": '<path stroke-linecap="round" stroke-linejoin="round" d="M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h1.125c.621 0 1.129-.504 1.09-1.124a17.902 17.902 0 00-3.213-9.193 2.056 2.056 0 00-1.58-.86H14.25M16.5 18.75h-2.25m0-11.177v-.958c0-.568-.422-1.048-.987-1.106a48.554 48.554 0 00-10.026 0 1.106 1.106 0 00-.987 1.106v7.635m12-6.677v6.677m0 4.5v-4.5m0 0h-12"/>',
    },
    {
        "nombre": "Bloqueo",
        "color": "#7c3aed",
        "color_light": "#f5f3ff",
        "color_border": "#c4b5fd",
        "icon_path": '<path stroke-linecap="round" stroke-linejoin="round" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"/>',
    },
    {
        "nombre": "Asistencia vial",
        "color": "#2563eb",
        "color_light": "#eff6ff",
        "color_border": "#93c5fd",
        "icon_path": '<path stroke-linecap="round" stroke-linejoin="round" d="M11.42 15.17L17.25 21A2.652 2.652 0 0021 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 11-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 004.486-6.336l-3.276 3.277a3.004 3.004 0 01-2.25-2.25l3.276-3.276a4.5 4.5 0 00-6.336 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085m-1.745 1.437L5.909 7.5H4.5L2.25 3.75l1.5-1.5L7.5 4.5v1.409l4.26 4.26m-1.745 1.437l1.745-1.437m6.615 8.206L15.75 15.75M4.867 19.125h.008v.008h-.008v-.008z"/>',
    },
    {
        "nombre": "Trabajos",
        "color": "#d97706",
        "color_light": "#fffbeb",
        "color_border": "#fcd34d",
        "icon_path": '<path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"/>',
    },
    {
        "nombre": "Libre",
        "color": "#16a34a",
        "color_light": "#f0fdf4",
        "color_border": "#86efac",
        "icon_path": '<path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>',
    },
]


def seed_database():
    db = SessionLocal()
    try:
        # Admin user
        if not db.query(User).filter(User.email == "admin@admin.com").first():
            hashed = bcrypt.hashpw("12345678".encode(), bcrypt.gensalt()).decode()
            admin = User(
                name="Admin",
                email="admin@admin.com",
                password=hashed,
                role="editor",
                terms_accepted_at=datetime.now(),
            )
            db.add(admin)

        # Tipos de evento
        for tipo in TIPOS_EVENTO_SEED:
            if not db.query(TipoEvento).filter(TipoEvento.nombre == tipo["nombre"]).first():
                db.add(TipoEvento(**tipo))

        db.commit()

        # Migrar fotos antiguas (columna foto_path) a la tabla bloqueo_fotos
        migrated_ids = {row[0] for row in db.query(BloqueoFoto.bloqueo_id).distinct().all()}
        for b in db.query(Bloqueo).filter(Bloqueo.foto_path.isnot(None)).all():
            if b.id not in migrated_ids:
                db.add(BloqueoFoto(bloqueo_id=b.id, path=b.foto_path, orden=0))

        # Migrar terminología de estado: "Finalizado" -> "Inactivo"
        db.query(Bloqueo).filter(Bloqueo.estado == "Finalizado").update({"estado": "Inactivo"})
        db.commit()
    finally:
        db.close()


seed_database()

# ---------------------------------------------------------------------------
# App & CORS
# ---------------------------------------------------------------------------

app = FastAPI(title="Coyuntura SGIC API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/storage", StaticFiles(directory=STORAGE_PATH), name="storage")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# JWT utils
# ---------------------------------------------------------------------------


def create_token(user: User) -> str:
    payload = {
        "sub": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "terms_accepted": user.terms_accepted_at is not None,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No autenticado")
    payload = decode_token(auth[7:])
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user


def require_editor(user: User = Depends(get_current_user)) -> User:
    if user.role != "editor":
        raise HTTPException(status_code=403, detail="Acceso restringido a editores")
    return user


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    terms_accepted: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TipoEventoOut(BaseModel):
    id: int
    nombre: str
    color: str
    color_light: str
    color_border: str
    icon_path: str

    class Config:
        from_attributes = True


class BloqueoOut(BaseModel):
    id: int
    direccion: str
    municipio: str
    departamento: str
    tipo_evento: str
    estado: str
    manifestantes_aproximados: Optional[int]
    observaciones: Optional[str]
    foto_path: Optional[str]
    latitud: float
    longitud: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------


@app.post("/api/auth/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not bcrypt.checkpw(body.password.encode(), user.password.encode()):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = create_token(user)
    return {
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "terms_accepted": user.terms_accepted_at is not None,
        },
    }


@app.post("/api/auth/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=422, detail="El correo ya está registrado")
    if len(body.password) < 8:
        raise HTTPException(status_code=422, detail="La contraseña debe tener al menos 8 caracteres")
    hashed = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()
    user = User(name=body.name, email=body.email, password=hashed, role="lector")
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_token(user)
    return {
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "terms_accepted": user.terms_accepted_at is not None,
        },
    }


@app.get("/api/auth/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "terms_accepted": current_user.terms_accepted_at is not None,
    }


@app.post("/api/auth/accept-terms")
def accept_terms(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user.id).first()
    user.terms_accepted_at = datetime.now()
    db.commit()
    token = create_token(user)
    return {"token": token, "message": "Términos aceptados"}


@app.patch("/api/auth/profile")
def update_profile(
    name: str = Form(None),
    email: str = Form(None),
    password: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if name:
        user.name = name
    if email and email != user.email:
        if db.query(User).filter(User.email == email, User.id != user.id).first():
            raise HTTPException(status_code=422, detail="El correo ya está en uso")
        user.email = email
    if password:
        if len(password) < 8:
            raise HTTPException(status_code=422, detail="La contraseña debe tener al menos 8 caracteres")
        user.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    db.commit()
    db.refresh(user)
    token = create_token(user)
    return {
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "terms_accepted": user.terms_accepted_at is not None,
        },
    }


@app.delete("/api/auth/profile")
def delete_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user.id).first()
    db.delete(user)
    db.commit()
    return {"message": "Cuenta eliminada"}


# ---------------------------------------------------------------------------
# Tipos de evento
# ---------------------------------------------------------------------------


@app.get("/api/tipos-evento", response_model=list[TipoEventoOut])
def list_tipos_evento(db: Session = Depends(get_db)):
    return db.query(TipoEvento).order_by(TipoEvento.nombre).all()


@app.post("/api/tipos-evento", response_model=TipoEventoOut, status_code=201)
def create_tipo_evento(
    nombre: str = Form(...),
    color: str = Form(...),
    color_light: str = Form(...),
    color_border: str = Form(...),
    icon_path: str = Form(...),
    _: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    if db.query(TipoEvento).filter(TipoEvento.nombre == nombre).first():
        raise HTTPException(status_code=422, detail="Ya existe un tipo con ese nombre")
    tipo = TipoEvento(
        nombre=nombre,
        color=color,
        color_light=color_light,
        color_border=color_border,
        icon_path=icon_path,
    )
    db.add(tipo)
    db.commit()
    db.refresh(tipo)
    return tipo


@app.patch("/api/tipos-evento/{tipo_id}", response_model=TipoEventoOut)
def update_tipo_evento(
    tipo_id: int,
    nombre: str = Form(...),
    color: str = Form(...),
    color_light: str = Form(...),
    color_border: str = Form(...),
    icon_path: str = Form(...),
    _: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    tipo = db.query(TipoEvento).filter(TipoEvento.id == tipo_id).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo no encontrado")
    duplicado = db.query(TipoEvento).filter(TipoEvento.nombre == nombre, TipoEvento.id != tipo_id).first()
    if duplicado:
        raise HTTPException(status_code=422, detail="Ya existe un tipo con ese nombre")
    nombre_anterior = tipo.nombre
    tipo.nombre = nombre
    tipo.color = color
    tipo.color_light = color_light
    tipo.color_border = color_border
    tipo.icon_path = icon_path
    if nombre_anterior != nombre:
        db.query(Bloqueo).filter(Bloqueo.tipo_evento == nombre_anterior).update({Bloqueo.tipo_evento: nombre})
    db.commit()
    db.refresh(tipo)
    return tipo


@app.delete("/api/tipos-evento/{tipo_id}")
def delete_tipo_evento(
    tipo_id: int,
    _: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    tipo = db.query(TipoEvento).filter(TipoEvento.id == tipo_id).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo no encontrado")
    db.delete(tipo)
    db.commit()
    return {"message": "Eliminado"}


# ---------------------------------------------------------------------------
# Bloqueos
# ---------------------------------------------------------------------------


MAX_FOTOS_POR_BLOQUEO = 8
POR_ESTABLECER = "Por establecer"

# Campos de "análisis" que en la matriz institucional se muestran como
# "POR ESTABLECER" cuando todavía no se conocen en el momento del registro.
CAMPOS_POR_ESTABLECER = (
    "referencia_inicio",
    "zona_inicio",
    "comisaria_inicio",
    "instrumentos",
    "nivel_conflicto",
    "presencia_policial",
    "cantidad_vehiculos",
    "demandas",
    "actores",
    "lideres_vulnerables",
)


def _formatear_duracion(inicio: Optional[datetime], fin: Optional[datetime]) -> Optional[str]:
    if not inicio or not fin or fin < inicio:
        return None
    total_min = int((fin - inicio).total_seconds() // 60)
    horas, minutos = divmod(total_min, 60)
    if horas and minutos:
        return f"{horas}h {minutos}min"
    if horas:
        return f"{horas}h"
    return f"{minutos}min"


def bloqueo_to_dict(b: Bloqueo, db: Session) -> dict:
    fotos = (
        db.query(BloqueoFoto)
        .filter(BloqueoFoto.bloqueo_id == b.id)
        .order_by(BloqueoFoto.orden, BloqueoFoto.id)
        .all()
    )
    fotos_paths = [f.path for f in fotos]
    return {
        "id": b.id,
        "direccion": b.direccion,
        "municipio": b.municipio,
        "departamento": b.departamento,
        "tipo_evento": b.tipo_evento,
        "estado": b.estado,
        "manifestantes_aproximados": b.manifestantes_aproximados,
        "observaciones": b.observaciones,
        "foto_path": fotos_paths[0] if fotos_paths else None,
        "fotos": fotos_paths,
        "latitud": b.latitud,
        "longitud": b.longitud,
        # Inicio
        "fecha_hora_inicio": b.fecha_hora_inicio.isoformat() if b.fecha_hora_inicio else None,
        "referencia_inicio": b.referencia_inicio,
        "zona_inicio": b.zona_inicio,
        "comisaria_inicio": b.comisaria_inicio,
        "instrumentos": b.instrumentos,
        "nivel_conflicto": b.nivel_conflicto,
        "presencia_policial": b.presencia_policial,
        "cantidad_vehiculos": b.cantidad_vehiculos,
        "demandas": b.demandas,
        "actores": b.actores,
        "lideres_vulnerables": b.lideres_vulnerables,
        # Finalización
        "fecha_hora_fin": b.fecha_hora_fin.isoformat() if b.fecha_hora_fin else None,
        "direccion_fin": b.direccion_fin,
        "latitud_fin": b.latitud_fin,
        "longitud_fin": b.longitud_fin,
        "referencia_fin": b.referencia_fin,
        "departamento_fin": b.departamento_fin,
        "municipio_fin": b.municipio_fin,
        "zona_fin": b.zona_fin,
        "comisaria_fin": b.comisaria_fin,
        "personas_fin": b.personas_fin,
        "duracion": _formatear_duracion(b.fecha_hora_inicio, b.fecha_hora_fin),
        "created_at": b.created_at.isoformat() if b.created_at else None,
        "updated_at": b.updated_at.isoformat() if b.updated_at else None,
    }


def _guardar_fotos(db: Session, bloqueo_id: int, fotos: List[UploadFile], orden_inicial: int = 0):
    orden = orden_inicial
    for foto in fotos:
        if not foto or not foto.filename:
            continue
        ext = os.path.splitext(foto.filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        dest = os.path.join(STORAGE_PATH, filename)
        with open(dest, "wb") as f:
            shutil.copyfileobj(foto.file, f)
        db.add(BloqueoFoto(bloqueo_id=bloqueo_id, path=f"/storage/{filename}", orden=orden))
        orden += 1


@app.get("/api/bloqueos")
def list_bloqueos(db: Session = Depends(get_db)):
    bloqueos = db.query(Bloqueo).order_by(Bloqueo.created_at.desc()).all()
    return [bloqueo_to_dict(b, db) for b in bloqueos]


@app.get("/api/bloqueos/{bloqueo_id}")
def get_bloqueo(bloqueo_id: int, db: Session = Depends(get_db)):
    b = db.query(Bloqueo).filter(Bloqueo.id == bloqueo_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return bloqueo_to_dict(b, db)


@app.post("/api/bloqueos", status_code=201)
def create_bloqueo(
    direccion: str = Form(...),
    municipio: str = Form(...),
    departamento: str = Form(...),
    tipo_evento: str = Form(...),
    latitud: float = Form(...),
    longitud: float = Form(...),
    estado: str = Form("Activo"),
    manifestantes_aproximados: Optional[int] = Form(None),
    observaciones: Optional[str] = Form(None),
    fotos: List[UploadFile] = File(default=[]),
    # Inicio (matriz institucional)
    fecha_hora_inicio: Optional[datetime] = Form(None),
    referencia_inicio: Optional[str] = Form(None),
    zona_inicio: Optional[str] = Form(None),
    comisaria_inicio: Optional[str] = Form(None),
    instrumentos: Optional[str] = Form(None),
    nivel_conflicto: Optional[str] = Form(None),
    presencia_policial: Optional[str] = Form(None),
    cantidad_vehiculos: Optional[str] = Form(None),
    demandas: Optional[str] = Form(None),
    actores: Optional[str] = Form(None),
    lideres_vulnerables: Optional[str] = Form(None),
    _: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    if len(fotos) > MAX_FOTOS_POR_BLOQUEO:
        raise HTTPException(status_code=422, detail=f"Máximo {MAX_FOTOS_POR_BLOQUEO} fotos por evento")

    valores_analisis = {
        "referencia_inicio": referencia_inicio,
        "zona_inicio": zona_inicio,
        "comisaria_inicio": comisaria_inicio,
        "instrumentos": instrumentos,
        "nivel_conflicto": nivel_conflicto,
        "presencia_policial": presencia_policial,
        "cantidad_vehiculos": cantidad_vehiculos,
        "demandas": demandas,
        "actores": actores,
        "lideres_vulnerables": lideres_vulnerables,
    }
    for campo in CAMPOS_POR_ESTABLECER:
        if not valores_analisis[campo]:
            valores_analisis[campo] = POR_ESTABLECER

    b = Bloqueo(
        direccion=direccion,
        municipio=municipio,
        departamento=departamento,
        tipo_evento=tipo_evento,
        latitud=latitud,
        longitud=longitud,
        estado=estado if estado in ("Activo", "Inactivo") else "Activo",
        manifestantes_aproximados=manifestantes_aproximados,
        observaciones=observaciones,
        fecha_hora_inicio=fecha_hora_inicio or datetime.now(),
        **valores_analisis,
    )
    db.add(b)
    db.commit()
    db.refresh(b)

    _guardar_fotos(db, b.id, fotos)
    db.commit()
    db.refresh(b)
    return bloqueo_to_dict(b, db)


@app.patch("/api/bloqueos/{bloqueo_id}")
def update_bloqueo(
    bloqueo_id: int,
    direccion: Optional[str] = Form(None),
    municipio: Optional[str] = Form(None),
    departamento: Optional[str] = Form(None),
    tipo_evento: Optional[str] = Form(None),
    latitud: Optional[float] = Form(None),
    longitud: Optional[float] = Form(None),
    estado: Optional[str] = Form(None),
    manifestantes_aproximados: Optional[int] = Form(None),
    observaciones: Optional[str] = Form(None),
    fotos: List[UploadFile] = File(default=[]),
    remove_fotos: List[str] = Form(default=[]),
    # Inicio
    fecha_hora_inicio: Optional[datetime] = Form(None),
    referencia_inicio: Optional[str] = Form(None),
    zona_inicio: Optional[str] = Form(None),
    comisaria_inicio: Optional[str] = Form(None),
    instrumentos: Optional[str] = Form(None),
    nivel_conflicto: Optional[str] = Form(None),
    presencia_policial: Optional[str] = Form(None),
    cantidad_vehiculos: Optional[str] = Form(None),
    demandas: Optional[str] = Form(None),
    actores: Optional[str] = Form(None),
    lideres_vulnerables: Optional[str] = Form(None),
    # Finalización
    fecha_hora_fin: Optional[datetime] = Form(None),
    direccion_fin: Optional[str] = Form(None),
    latitud_fin: Optional[float] = Form(None),
    longitud_fin: Optional[float] = Form(None),
    referencia_fin: Optional[str] = Form(None),
    departamento_fin: Optional[str] = Form(None),
    municipio_fin: Optional[str] = Form(None),
    zona_fin: Optional[str] = Form(None),
    comisaria_fin: Optional[str] = Form(None),
    personas_fin: Optional[int] = Form(None),
    _: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    b = db.query(Bloqueo).filter(Bloqueo.id == bloqueo_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    if direccion is not None:
        b.direccion = direccion
    if municipio is not None:
        b.municipio = municipio
    if departamento is not None:
        b.departamento = departamento
    if tipo_evento is not None:
        b.tipo_evento = tipo_evento
    if latitud is not None:
        b.latitud = latitud
    if longitud is not None:
        b.longitud = longitud
    if estado is not None and estado in ("Activo", "Inactivo"):
        b.estado = estado
    if manifestantes_aproximados is not None:
        b.manifestantes_aproximados = manifestantes_aproximados
    if observaciones is not None:
        b.observaciones = observaciones

    if fecha_hora_inicio is not None:
        b.fecha_hora_inicio = fecha_hora_inicio
    if referencia_inicio is not None:
        b.referencia_inicio = referencia_inicio
    if zona_inicio is not None:
        b.zona_inicio = zona_inicio
    if comisaria_inicio is not None:
        b.comisaria_inicio = comisaria_inicio
    if instrumentos is not None:
        b.instrumentos = instrumentos
    if nivel_conflicto is not None:
        b.nivel_conflicto = nivel_conflicto
    if presencia_policial is not None:
        b.presencia_policial = presencia_policial
    if cantidad_vehiculos is not None:
        b.cantidad_vehiculos = cantidad_vehiculos
    if demandas is not None:
        b.demandas = demandas
    if actores is not None:
        b.actores = actores
    if lideres_vulnerables is not None:
        b.lideres_vulnerables = lideres_vulnerables

    if fecha_hora_fin is not None:
        b.fecha_hora_fin = fecha_hora_fin
    if direccion_fin is not None:
        b.direccion_fin = direccion_fin
    if latitud_fin is not None:
        b.latitud_fin = latitud_fin
    if longitud_fin is not None:
        b.longitud_fin = longitud_fin
    if referencia_fin is not None:
        b.referencia_fin = referencia_fin
    if departamento_fin is not None:
        b.departamento_fin = departamento_fin
    if municipio_fin is not None:
        b.municipio_fin = municipio_fin
    if zona_fin is not None:
        b.zona_fin = zona_fin
    if comisaria_fin is not None:
        b.comisaria_fin = comisaria_fin
    if personas_fin is not None:
        b.personas_fin = personas_fin

    # Al marcar el evento como Inactivo, si no se indicó fecha/hora de fin, se registra automáticamente
    if estado == "Inactivo" and b.fecha_hora_fin is None and fecha_hora_fin is None:
        b.fecha_hora_fin = datetime.now()

    if remove_fotos:
        a_eliminar = (
            db.query(BloqueoFoto)
            .filter(BloqueoFoto.bloqueo_id == b.id, BloqueoFoto.path.in_(remove_fotos))
            .all()
        )
        for foto in a_eliminar:
            filepath = os.path.join(STORAGE_PATH, os.path.basename(foto.path))
            if os.path.exists(filepath):
                os.remove(filepath)
            db.delete(foto)

    if fotos:
        restantes = db.query(BloqueoFoto).filter(BloqueoFoto.bloqueo_id == b.id).count()
        if remove_fotos:
            restantes -= len(remove_fotos)
        if restantes + len(fotos) > MAX_FOTOS_POR_BLOQUEO:
            raise HTTPException(status_code=422, detail=f"Máximo {MAX_FOTOS_POR_BLOQUEO} fotos por evento")
        siguiente_orden = db.query(BloqueoFoto).filter(BloqueoFoto.bloqueo_id == b.id).count() + 1000
        _guardar_fotos(db, b.id, fotos, orden_inicial=siguiente_orden)

    b.updated_at = datetime.now()
    db.commit()
    db.refresh(b)
    return bloqueo_to_dict(b, db)


@app.delete("/api/bloqueos/{bloqueo_id}")
def delete_bloqueo(
    bloqueo_id: int,
    _: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    b = db.query(Bloqueo).filter(Bloqueo.id == bloqueo_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    fotos = db.query(BloqueoFoto).filter(BloqueoFoto.bloqueo_id == b.id).all()
    for foto in fotos:
        filepath = os.path.join(STORAGE_PATH, os.path.basename(foto.path))
        if os.path.exists(filepath):
            os.remove(filepath)
        db.delete(foto)
    if b.foto_path:
        filepath = os.path.join(STORAGE_PATH, os.path.basename(b.foto_path))
        if os.path.exists(filepath):
            os.remove(filepath)
    db.delete(b)
    db.commit()
    return {"message": "Eliminado"}


# ---------------------------------------------------------------------------
# Users (editor only)
# ---------------------------------------------------------------------------


@app.get("/api/usuarios")
def list_usuarios(_: User = Depends(require_editor), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.name).all()
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "terms_accepted": u.terms_accepted_at is not None,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


@app.post("/api/usuarios", status_code=201)
def create_usuario(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form("lector"),
    _: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=422, detail="El correo ya está registrado")
    if len(password) < 8:
        raise HTTPException(status_code=422, detail="La contraseña debe tener al menos 8 caracteres")
    if role not in ("editor", "lector"):
        role = "lector"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = User(name=name, email=email, password=hashed, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "terms_accepted": user.terms_accepted_at is not None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@app.patch("/api/usuarios/{user_id}/role")
def update_user_role(
    user_id: int,
    role: str = Form(...),
    current_user: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    if role not in ("editor", "lector"):
        raise HTTPException(status_code=422, detail="Rol inválido")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.role = role
    db.commit()
    return {"message": "Rol actualizado", "role": user.role}


@app.patch("/api/usuarios/{user_id}/email")
def update_user_email(
    user_id: int,
    email: str = Form(...),
    current_user: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    duplicado = db.query(User).filter(User.email == email, User.id != user_id).first()
    if duplicado:
        raise HTTPException(status_code=422, detail="Ya existe una cuenta con ese correo")
    user.email = email
    user.updated_at = datetime.now()
    db.commit()
    return {"message": "Correo actualizado", "email": user.email}


@app.patch("/api/usuarios/{user_id}/password")
def reset_user_password(
    user_id: int,
    new_password: str = Form(...),
    current_user: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    if len(new_password) < 8:
        raise HTTPException(status_code=422, detail="La contraseña debe tener al menos 8 caracteres")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    user.updated_at = datetime.now()
    db.commit()
    return {"message": "Contraseña restablecida"}


@app.delete("/api/usuarios/{user_id}")
def delete_usuario(
    user_id: int,
    current_user: User = Depends(require_editor),
    db: Session = Depends(get_db),
):
    if current_user.id == user_id:
        raise HTTPException(status_code=403, detail="No puedes eliminar tu propia cuenta desde aquí")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(user)
    db.commit()
    return {"message": "Usuario eliminado"}
