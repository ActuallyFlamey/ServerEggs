import asyncio
import io
import os
import re

import aiohttp
import discord
import dotenv
import imagehash
from PIL import Image

dotenv.load_dotenv()

async def process_attachment(attach: discord.Attachment):
    attach_bytes = await attach.read()

    file_hash = []
    file_path = f"{os.getenv('MEDIA_PATH')}/{attach.id}.webp"

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

async def show_attachment(egg, embed: discord.Embed):
    file = None

    if egg.attach_path and os.path.exists(egg.attach_path):
        filename = os.path.basename(egg.attach_path)

        file = discord.File(egg.attach_path, filename=filename)

        embed.set_image(url=f"attachment://{filename}")
    elif getattr(egg, "attach_link", None):
        good_url = await resolve_media_url(egg.attach_link)

        embed.set_image(url=good_url)

    return file

# this function was heavily assisted by Gemini 3.1 Pro
async def resolve_media_url(url: str) -> str:
    if re.search(r'\.(png|jpg|jpeg|gif|webp)(\?.*)?$', url, re.IGNORECASE):
        return url

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Discordbot/2.0; +https://discordapp.com)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    async with aiohttp.ClientSession() as session, session.get(url, headers=headers, timeout=5) as response:
        if response.status == 200:
            html = await response.text()

            if "tenor.com" in url:
                tenor_match = re.search(r'(https://(?:media|c)\.tenor\.com/[^\'"]+\.gif)', html, re.IGNORECASE)
                if tenor_match:
                    return tenor_match.group(1)

            match = re.search(r'<meta[^>]+property=[\'"](?:og|twitter):image[\'"][^>]+content=[\'"]([^\'"]+)[\'"]', html, re.IGNORECASE)

            if not match:
                match = re.search(r'<meta[^>]+content=[\'"]([^\'"]+)[\'"][^>]+property=[\'"](?:og|twitter):image[\'"]', html, re.IGNORECASE)

            if not match:
                match = re.search(r'<meta[^>]+name=[\'"]twitter:image[\'"][^>]+content=[\'"]([^\'"]+)[\'"]', html, re.IGNORECASE)

            if match:
                return match.group(1)
            else:
                print(f"[Debug] Got 200 OK for {url}, but regex failed to find an image link.")
        else:
            print(f"[Debug] Could not scrape media URL. Server returned HTTP {response.status} for {url}")

    return url