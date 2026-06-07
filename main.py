from fastapi import FastAPI

app = FastAPI(title="Camellando")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "proyecto": "Camellando",
        "version": "1.0.0"
    }
