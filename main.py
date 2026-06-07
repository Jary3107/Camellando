import os
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "sqlite:///./camellando.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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

@app.get("/")
def read_root():
    return {
        "mensaje": "Bienvenidos a la API de Camellando",
        "entrega": "Avance 1",
        "documentacion": "/docs"
    }


@app.post("/api/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    db_user = User(
        email=user_in.email,
        password=user_in.password,  
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
    user = db.query(User).filter(User.email == email, User.password == password).first()
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return {
        "status": "success",
        "user_id": user.id,
        "user_type": user.user_type,
        "full_name": user.full_name
    }


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


@app.get("/api/services", response_model=List[ServiceOut])
def list_services(category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Service)
    if category:
        query = query.filter(Service.category.ilike(f"%{category}%"))
    return query.all()

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


@app.get("/api/contracts", response_model=List[ContractOut])
def list_contracts(user_id: int = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")

    if user.user_type == "client":
        return db.query(Contract).filter(Contract.client_id == user_id).all()
    else:
        return db.query(Contract).join(Service).filter(Service.worker_id == user_id).all()


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

