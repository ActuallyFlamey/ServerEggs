import os

import dotenv

dotenv.load_dotenv()

TORTOISE_ORM = {
    "connections": {"default": os.getenv("DATABASE_URL")},
    "apps": {
        "models": {
            "models": ["schema", "aerich.models"], 
            "default_connection": "default",
        }
    }
}