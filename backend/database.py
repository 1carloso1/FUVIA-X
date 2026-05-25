from sqlmodel import Field, SQLModel, create_engine, Session
from typing import Optional
from datetime import datetime

# Definimos el Molde de la Tabla SQL
class InferenceRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Entradas (Vector de Yeh)
    cement: float
    slag: float
    flyash: float
    water: float
    superplasticizer: float
    coarseaggregate: float
    fineaggregate: float
    age: int

    # Salida del Modelo
    predicted_strength: float

    # Validación Empírica
    real_strength: Optional[float] = None
    absolute_error: Optional[float] = None
    relative_error: Optional[float] = None
    is_validated: bool = False

# Configuramos la conexión a un archivo SQLite local
sqlite_file_name = "fuvia_datos.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# El "motor" que se comunica con la base de datos
engine = create_engine(sqlite_url, echo=False)

# Función para crear las tablas si no existen
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Inyección de dependencias para FastAPI
def get_session():
    with Session(engine) as session:
        yield session