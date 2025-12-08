from fastapi import FastAPI
app = FastAPI(title="Python Service")

@app.get("/")
def read_root():
    return {"message": "Hello from Python Service"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
