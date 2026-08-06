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

            if getattr(img, "is_animated", False):
                img.save(
                    file_path, 
                    "WEBP", 
                    save_all=True,
                    quality=80, 
                    method=4,
                    loop=img.info.get("loop", 0), 
                    duration=img.info.get("duration", 100)
                )
            else:
                img.save(file_path, "WEBP", quality=80)

    await asyncio.to_thread(save)

    return file_path, file_hash[0]

def show_attachment(egg, embed: discord.Embed):
    file = None

    if egg.attach_path and os.path.exists(egg.attach_path):
        filename = os.path.basename(egg.attach_path)

        file = discord.File(egg.attach_path, filename=filename)

        embed.set_image(url=f"attachment://{filename}")
    
    return file