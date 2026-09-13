from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import json
import anthropic
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="CV Optimizer API", description="API para el Mini SaaS de optimización de CVs")

# Permitir CORS para que la demo web pueda llamar a esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class CVRequest(BaseModel):
    target_role: str
    cv_text: str
    job_description: Optional[str] = ""

SYSTEM_PROMPT = """Sos un editor experto en redacción de CVs y un reclutador senior. Devolvé ÚNICAMENTE un objeto JSON válido con la siguiente estructura estricta:
{
  "ats_score": 0,
  "summary_original": "",
  "summary_improved": "",
  "experience_items": [
    {
      "original": "",
      "improved": "",
      "editor_note": ""
    }
  ],
  "missing_keywords": [],
  "recommendations": []
}

REGLAS DE NEGOCIO Y HONESTIDAD (CRÍTICO):
1. NO inventes empleadores, títulos, métricas numéricas ni fechas que no estén explícitamente en el CV original.
2. Limita la salida a: 2 a 5 experiencias, 3 a 6 palabras clave, 3 a 5 recomendaciones.
3. Prioriza el vocabulario de la 'Descripción del puesto' si se provee.
4. Tu respuesta debe ser SOLO JSON válido. No agregues backticks (```json), ni saludos, ni texto explicativo antes o después del JSON.
"""

@app.post("/api/optimize")
async def optimize_cv(request: CVRequest):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not request.cv_text.strip() or not request.target_role.strip():
        raise HTTPException(status_code=400, detail="El puesto objetivo y el texto del CV son obligatorios.")

    user_prompt = f"Puesto objetivo: {request.target_role}\nDescripción del puesto: {request.job_description}\nCV:\n{request.cv_text}"

    if not api_key:
        # Modo simulación si no hay API Key (para poder probar el flujo)
        print("⚠️ ANTHROPIC_API_KEY no encontrada. Devolviendo datos simulados...")
        return {
            "ats_score": 58,
            "summary_original": "Experiencia en ventas y manejo de caja.",
            "summary_improved": "Profesional orientado a resultados con foco en atención al cliente y gestión de transacciones.",
            "experience_items": [
                {
                    "original": "Atendía clientes y cobraba",
                    "improved": "Gestionó un alto volumen de transacciones diarias, asegurando la satisfacción del cliente y el cuadre de caja.",
                    "editor_note": "Se cambió a verbos de acción y foco en impacto."
                }
            ],
            "missing_keywords": ["CRM", "Fidelización", "Resolución de conflictos"],
            "recommendations": ["Agrega cualquier métrica de volumen de clientes atendidos por día."]
        }

    # Llamada real a la API de Claude
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        response = client.messages.create(
            model="claude-3-haiku-20240307", # Haiku es rápido y excelente para formateo JSON
            max_tokens=1500,
            temperature=0.2, # Baja temperatura para mayor apego a las reglas y formato
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Limpieza defensiva del JSON (por si el modelo agrega backticks a pesar de la instrucción)
        response_text = response.content[0].text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        return json.loads(response_text.strip())
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="La IA no devolvió un JSON válido. Reintenta la operación.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Iniciando API de Optimización de CV en http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
