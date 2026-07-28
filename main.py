from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from strength_evaluator import evaluate_strength
from password_generator import generate_secure_password
from dictionary_checker import load_common_passwords

app = FastAPI(title="Entropy Engine API")

# Load dictionary once at startup
load_common_passwords()


class PasswordRequest(BaseModel):
    password: str
    algorithm: str

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def serve_home():
    return FileResponse("static/index.html")
@app.post("/analyze")

def analyze_password(data: PasswordRequest):

    if len(data.password) > 128:
        return {"error": "Password too long"}

    result = evaluate_strength(data.password, data.algorithm)
    return result


@app.get("/generate")
def generate_password(length: int = 16):
    password = generate_secure_password(length)
    return {"generated_password": password}