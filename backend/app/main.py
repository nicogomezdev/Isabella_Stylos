from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    tittle="Isabella Stylos API",
    description="Sistema de gestión de citas para salon de belleza",
    version="1.0.0"
) 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message" :"Isabella Stylos API funcionando"}