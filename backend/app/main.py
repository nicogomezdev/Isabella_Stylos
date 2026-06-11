from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, services, appointments


app = FastAPI(
    title="Isabella Stylos API",
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

app.include_router(auth.router)
app.include_router(services.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(appointments.router)


@app.get("/")
def root():
    return {"message" :"Isabella Stylos API funcionando"}