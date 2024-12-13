from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nlp = spacy.load("es_core_news_sm")


# Crear la aplicación FastAPI
app = FastAPI()

# Montar la carpeta 'static' para servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Diccionario para almacenar el nombre del usuario
user_data = {"name": None}


@app.get("/", response_class=HTMLResponse)
async def get_home():
    with open("index.html", "r", encoding="utf-8") as file:
        return HTMLResponse(file.read())

@app.get("/chat", response_class=HTMLResponse)
async def get_chat():
    with open("chat.html", "r", encoding="utf-8") as file:
        return HTMLResponse(file.read())
    
@app.get("/portal", response_class=HTMLResponse)
async def get_portal():
    with open("portal.html", "r", encoding="utf-8") as file:
        return HTMLResponse(file.read())

# Datos de preguntas y respuestas 
data = [
    {"category": "Gestión de baterías", "phrase": "¿Cómo optimiza la inteligencia artificial la carga y descarga de las baterías?"},
    {"category": "Vida útil de las baterías", "phrase": "¿Cómo afecta una mala gestión de carga a la vida útil de las baterías?"},
    {"category": "Intermitencia en la generación", "phrase": "¿Cómo puede la inteligencia artificial ayudar a lidiar con la intermitencia de la energía solar y eólica?"},
    {"category": "Costos operativos", "phrase": "¿Cómo puede optimizarse el sistema de almacenamiento para reducir los costos operativos?"}
]

responses = {
    "Gestión de baterías": "La inteligencia artificial puede monitorear y predecir los momentos más adecuados para cargar y descargar las baterías, maximizando su eficiencia y evitando ciclos innecesarios que podrían reducir su vida útil.",
    "Vida útil de las baterías": "Una mala gestión de la carga y descarga, como sobrecargar o descargar excesivamente las baterías, puede generar un desgaste acelerado, reduciendo su capacidad y vida útil. La optimización de estos procesos es clave para prolongar su durabilidad.",
    "Intermitencia en la generación": "La inteligencia artificial puede analizar la disponibilidad de energía renovable en tiempo real y ajustar la carga y descarga de las baterías para equilibrar la oferta y la demanda, minimizando el impacto de la intermitencia en el suministro energético.",
    "Costos operativos": "Al optimizar los ciclos de carga y descarga y prever el consumo futuro de energía, la inteligencia artificial puede reducir el desgaste de las baterías y maximizar su rendimiento, lo que ayuda a reducir los costos operativos asociados con el mantenimiento y la gestión del sistema."
}
# Modelo de entrada para preguntas y nombre
class UserQuery(BaseModel):
    question: str

class NameRequest(BaseModel):
    name: str

@app.post("/set_name")
async def set_name(request: NameRequest):
    if not request.name.strip():
        raise HTTPException(status_code=400, detail="El nombre no puede estar vacío.")
    user_data["name"] = request.name.strip()
    return {"message": f"¡Hola, {user_data['name']}! Bienvenido al Chatbot de Energías Renovables. ¿En qué puedo ayudarte?"}

def find_best_match_with_spacy(input_text):
    user_doc = nlp(input_text.lower())
    user_keywords = [token.lemma_ for token in user_doc if not token.is_stop and not token.is_punct]

    best_match = None
    highest_similarity = 0

    for item in data:
        category_doc = nlp(item["phrase"].lower())
        category_keywords = [token.lemma_ for token in category_doc if not token.is_stop and not token.is_punct]

        common_keywords = set(user_keywords) & set(category_keywords)
        similarity_score = len(common_keywords) / len(set(category_keywords))

        if similarity_score > highest_similarity and similarity_score > 0.3:
            highest_similarity = similarity_score
            best_match = item["category"]

    return best_match


@app.post("/chat")
async def chat(request: UserQuery):
    if not user_data["name"]:
        return {"response": "Por favor, proporciona tu nombre primero."}
    category = find_best_match_with_spacy(request.question.lower())
    response = responses.get(category, "Lo siento, no entiendo la pregunta. ¿Puedes reformularla?")

    return {"response": response}


energy_storage_by_region = {
    "amazonas": 1000,  # en kWh
    "antioquia": 950,
    "arauca": 1100,
    "atlantico": 1200,
    "bolivar": 1150,
    "boyaca": 900,
    "caldas": 850,
    "caqueta": 1000,
    "casanare": 1050,
    "cauca": 950,
    "cesar": 1100,
    "choco": 800,
    "cordoba": 1150,
    "cundinamarca": 900,
    "guainia": 1000,
    "guaviare": 1000,
    "huila": 1000,
    "la guajira": 1300,
    "magdalena": 1200,
    "meta": 1000,
    "nariño": 850,
    "norte de santander": 1050,
    "putumayo": 900,
    "quindio": 850,
    "risaralda": 850,
    "san andres y providencia": 1150,
    "santander": 1000,
    "sucre": 1150,
    "tolima": 950,
    "valle del cauca": 900,
    "vaupes": 1000,
    "vichada": 1050,
    "bogota": 850,
}

class StorageEfficiencyRequest(BaseModel):
    region: str
    daily_consumption_kwh: float
    storage_cost_per_kwh: float

@app.post("/calculate_storage_efficiency")
async def calculate_storage_efficiency(request: StorageEfficiencyRequest):
    normalized_region = request.region.lower()
    if normalized_region not in energy_storage_by_region:
        raise HTTPException(
            status_code=400,
            detail=f"Región no reconocida. Las regiones disponibles son: {', '.join(energy_storage_by_region.keys())}."
        )

    # Cálculo de la eficiencia del almacenamiento en función del consumo diario
    daily_storage_capacity = energy_storage_by_region[normalized_region]
    efficiency_rate = min(request.daily_consumption_kwh, daily_storage_capacity) * request.storage_cost_per_kwh
    annual_efficiency = efficiency_rate * 365  # Considerando el ahorro por año
    efficiency_3_years = annual_efficiency * 3
    efficiency_15_years = annual_efficiency * 15

    return {
        "message": (
            f"En {request.region}, con un consumo diario de {request.daily_consumption_kwh} kWh "
            f"y un costo de almacenamiento de {request.storage_cost_per_kwh} COP por kWh, podrías mejorar la eficiencia del almacenamiento:\n"
            f"- {round(annual_efficiency, 2)} COP al año.\n"
            f"- {round(efficiency_3_years, 2)} COP en 3 años.\n"
            f"- {round(efficiency_15_years, 2)} COP en 15 años."
        ),
        "annual_efficiency": annual_efficiency,  # Incluye la eficiencia anual
        "efficiency_3_years": efficiency_3_years,  # Incluye la eficiencia a 3 años
        "efficiency_15_years": efficiency_15_years  # Incluye la eficiencia a 15 años
    }

# Función para simular la gestión inteligente de las baterías
def optimize_battery_management(input_data):
    # Lógica para optimizar el ciclo de carga y descarga según las necesidades
    # de la red eléctrica y las condiciones de generación de energía
    optimized_battery_usage = {
        "charge": max(0, min(input_data["charge_demand"], input_data["battery_capacity"])),
        "discharge": max(0, min(input_data["discharge_demand"], input_data["battery_capacity"]))
    }

    # Simulación de la reducción de la vida útil si no se optimizan los ciclos
    if optimized_battery_usage["charge"] > 0 or optimized_battery_usage["discharge"] > 0:
        lifetime_reduction_factor = 0.05  # 5% de reducción por ciclo ineficiente
    else:
        lifetime_reduction_factor = 0.02  # 2% de reducción si se gestiona de manera óptima

    # Regresar resultados optimizados
    return {
        "optimized_usage": optimized_battery_usage,
        "lifetime_reduction": lifetime_reduction_factor
    }
