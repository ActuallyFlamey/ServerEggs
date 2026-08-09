import os

import dotenv

dotenv.load_dotenv()

TORTOISE_ORM = {
    "connections": {"default": os.getenv("DATABASE_URL")},
    "apps": {
        "eggs": {
            "models": ["schema"], 
            "default_connection": "default",
            "migrations": "migrations"
        }
    }
}