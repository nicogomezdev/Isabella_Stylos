<h1 align=center> ISABELLA STYLOS <h1>

<h3 align=center> descripcion </h3>

### Sistema de gestión de citas para salon de belleza

<h3 align=center> STACK </h3>

<p align=center>
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![Python](https://img.shields.io/badge/Python-3.12-3776AB)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791)
![JWT](https://img.shields.io/badge/Auth-JWT-orange)

</p>


<h3 align=center> INSTALACIÓN </h3>

## Requisitos previos

- Python 3.12+
- Node.js 20+
- PostgreSQL 18.3+

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```


Crea un archivo `.env` basado en `.env.example` y configura tus variables.
```bash
uvicorn app.main:app --reload
```
Si contesta http://localhost:8000/ ya se enceuntra operativo el backend, y es la dir de la API
Documentación: http://localhost:8000/docs

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Si contesta http://localhost:3000/ ya se encuentra operativo el frontend, es la dir del APP


![URL](https://img.shields.io/badge/Disponible%20En-Proximamente-red)

<h3 align=center> tests </h3>

<h3 align=center>Funcionalidades </h3>

<h3 align=center> structura del proyecto </h3>

<h3 align=center> Autor <h3>

## Funcionalidades
- [ ] Autenticación (registro/login)
- [ ] Gestión de servicios
- [ ] Sistema de citas
- [ ] Panel de administración