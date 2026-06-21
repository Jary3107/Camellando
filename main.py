import os
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

if os.environ.get("VERCEL"):
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////tmp/camellando.db")
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./camellando.db")


if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

import hashlib
import secrets

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hash_val = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}:{hash_val.hex()}"

def verify_password(stored_password: str, provided_password: str) -> bool:
    try:
        salt, hash_hex = stored_password.split(':')
        hash_val = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return secrets.compare_digest(hash_val.hex(), hash_hex)
    except ValueError:
        # Fallback for plain text passwords
        return stored_password == provided_password



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    full_name = Column(String)
    user_type = Column(String) 
    phone = Column(String, nullable=True)


class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    category = Column(String)
    price = Column(Float)
    worker_id = Column(Integer, ForeignKey("users.id"))


class Contract(Base):
    __tablename__ = "contracts"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    status = Column(String, default="pending") 
    price = Column(Float)
    details = Column(String, nullable=True)

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    user_type: str
    phone: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    user_type: str
    phone: Optional[str] = None
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    email: str
    full_name: str
    phone: Optional[str] = None
    password: Optional[str] = None



class ServiceCreate(BaseModel):
    title: str
    description: str
    category: str
    price: float
    worker_id: int

class ServiceOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    price: float
    worker_id: int
    class Config:
        from_attributes = True

class ServiceUpdate(BaseModel):
    title: str
    description: str
    category: str
    price: float



class ContractCreate(BaseModel):
    client_id: int 
    service_id: int
    price: float
    details: Optional[str] = None

class ContractOut(BaseModel):
    id: int
    client_id: int
    service_id: int
    status: str
    price: float
    details: Optional[str] = None
    class Config:
        from_attributes = True

class ServiceDetailOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    price: float
    worker_id: int
    worker_name: str
    worker_phone: Optional[str] = None
    class Config:
        from_attributes = True

class ContractDetailOut(BaseModel):
    id: int
    client_id: int
    client_name: str
    client_phone: Optional[str] = None
    service_id: int
    service_title: str
    worker_id: int
    worker_name: str
    status: str
    price: float
    details: Optional[str] = None
    class Config:
        from_attributes = True


app = FastAPI(
    title="Camellando",
    description="MVP inicial.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")



@app.post("/api/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    db_user = User(
        email=user_in.email,
        password=hash_password(user_in.password),  
        full_name=user_in.full_name,
        user_type=user_in.user_type,
        phone=user_in.phone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/api/login")
def login(email: str = Query(...), password: str = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(user.password, password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return {
        "status": "success",
        "user_id": user.id,
        "user_type": user.user_type,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone
    }

@app.put("/api/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if user_in.email != user.email:
        existing = db.query(User).filter(User.email == user_in.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="El correo ya está registrado por otro usuario")
    
    user.full_name = user_in.full_name
    user.email = user_in.email
    user.phone = user_in.phone
    
    if user_in.password:
        user.password = hash_password(user_in.password)
        
    db.commit()
    db.refresh(user)
    return user



@app.post("/api/services", response_model=ServiceOut)
def create_service(service_in: ServiceCreate, db: Session = Depends(get_db)):

    worker = db.query(User).filter(User.id == service_in.worker_id).first()
    if not worker or worker.user_type != "worker":
        raise HTTPException(status_code=400, detail="El worker_id no corresponde a un trabajador válido")

    db_service = Service(
        title=service_in.title,
        description=service_in.description,
        category=service_in.category,
        price=service_in.price,
        worker_id=service_in.worker_id
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

@app.put("/api/services/{service_id}", response_model=ServiceOut)
def update_service(service_id: int, service_in: ServiceUpdate, worker_id: int = Query(...), db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    
    if service.worker_id != worker_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este servicio")
        
    service.title = service_in.title
    service.description = service_in.description
    service.category = service_in.category
    service.price = service_in.price
    
    db.commit()
    db.refresh(service)
    return service

@app.delete("/api/services/{service_id}")
def delete_service(service_id: int, worker_id: int = Query(...), db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    
    if service.worker_id != worker_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este servicio")
    
    try:
        db.delete(service)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se puede eliminar el servicio porque tiene contratos asociados")
        
    return {"status": "success", "message": "Servicio eliminado correctamente"}



@app.get("/api/services", response_model=List[ServiceDetailOut])
def list_services(category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Service)
    if category:
        query = query.filter(Service.category.ilike(f"%{category}%"))
    services = query.all()
    
    result = []
    for s in services:
        worker = db.query(User).filter(User.id == s.worker_id).first()
        result.append(ServiceDetailOut(
            id=s.id,
            title=s.title,
            description=s.description,
            category=s.category,
            price=s.price,
            worker_id=s.worker_id,
            worker_name=worker.full_name if worker else "Desconocido",
            worker_phone=worker.phone if worker else None
        ))
    return result

@app.post("/api/contracts", response_model=ContractOut)
def create_contract(contract_in: ContractCreate, db: Session = Depends(get_db)):
    client = db.query(User).filter(User.id == contract_in.client_id).first()
    if not client or client.user_type != "client":
        raise HTTPException(status_code=400, detail="El client_id no corresponde a un cliente válido")

    service = db.query(Service).filter(Service.id == contract_in.service_id).first()
    if not service:
        raise HTTPException(status_code=400, detail="El servicio no existe")

    db_contract = Contract(
        client_id=contract_in.client_id,
        service_id=contract_in.service_id,
        price=contract_in.price,
        details=contract_in.details,
        status="pending"
    )
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract


@app.get("/api/contracts", response_model=List[ContractDetailOut])
def list_contracts(user_id: int = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")

    if user.user_type == "client":
        contracts = db.query(Contract).filter(Contract.client_id == user_id).all()
    else:
        contracts = db.query(Contract).join(Service).filter(Service.worker_id == user_id).all()

    result = []
    for c in contracts:
        service = db.query(Service).filter(Service.id == c.service_id).first()
        worker = db.query(User).filter(User.id == service.worker_id).first() if service else None
        client = db.query(User).filter(User.id == c.client_id).first()
        
        result.append(ContractDetailOut(
            id=c.id,
            client_id=c.client_id,
            client_name=client.full_name if client else "Desconocido",
            client_phone=client.phone if client else None,
            service_id=c.service_id,
            service_title=service.title if service else "Servicio Eliminado",
            worker_id=service.worker_id if service else 0,
            worker_name=worker.full_name if worker else "Desconocido",
            status=c.status,
            price=c.price,
            details=c.details
        ))
    return result


@app.patch("/api/contracts/{contract_id}", response_model=ContractOut)
def update_contract(contract_id: int, status: str = Query(...), db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")

    if status.lower() not in ["accepted", "rejected", "completed"]:
        raise HTTPException(status_code=400, detail="Estado no válido")

    contract.status = status.lower()
    db.commit()
    db.refresh(contract)
    return contract

@app.on_event("startup")
def startup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            w1 = User(email="juan@example.com", password="123", full_name="Juan Plomero", user_type="worker", phone="300")
            c1 = User(email="carlos@example.com", password="123", full_name="Carlos Cliente", user_type="client", phone="315")
            db.add_all([w1, c1])
            db.commit()

            s1 = Service(title="Reparación de Fugas", description="Plomería del hogar", category="Hogar", price=30000, worker_id=w1.id)
            db.add(s1)
            db.commit()

            con1 = Contract(client_id=c1.id, service_id=s1.id, price=30000, details="Gotera cocina", status="pending")
            db.add(con1)
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

