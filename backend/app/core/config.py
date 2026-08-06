from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Configuraciones de la aplicación, leídas desde variables de entorno.
    """

    # Parámetros de conexión a SQL Server (sin valores reales por defecto: deben venir del .env)
    SQL_SERVER: str = "localhost"
    SQL_PORT: str = "1433"
    SQL_DATABASE: str = "GestionDatosSiniestros"
    SQL_USER: str = ""
    SQL_PASSWORD: str = ""
    SQL_DRIVER: str = "ODBC Driver 17 for SQL Server"

    # Generamos la cadena de conexión como campo real
    DATABASE_URL: str = None

    # Configuración de seguridad (debe venir del .env, sin valor por defecto real)
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # opcional: ignora variables extra
    )

    def __post_init__(self):
        # Si DATABASE_URL no viene del env, la construimos
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"DRIVER={self.SQL_DRIVER};"
                f"SERVER={self.SQL_SERVER},{self.SQL_PORT};"
                f"DATABASE={self.SQL_DATABASE};"
                f"UID={self.SQL_USER};"
                f"PWD={self.SQL_PASSWORD};"
                "TrustServerCertificate=yes;"
            )

settings = Settings()
