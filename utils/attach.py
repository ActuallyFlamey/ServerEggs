import asyncio
import io
import os

import discord
import dotenv
import imagehash
from PIL import Image

dotenv.load_dotenv()

async def process_attachment(attach: discord.Attachment):
    attach_bytes = await attach.read()

    file_hash = []
    file_path = f"{os.getenv("MEDIA_PATH")}/{attach.id}.webp"

    def save():
        with Image.open(io.BytesIO(attach_bytes)) as img:
            img_hash = str(imagehash.average_hash(img))
            file_hash.append(img_hash)

            img.save(file_path, "WEBP", quality=80)

    await asyncio.to_thread(save)

    return file_path, file_hash[0]