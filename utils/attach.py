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

SUPPORTED_FILETYPE_REGEX = r'\.(gif|png|jpg|jpeg|webp)(?:[?#].*)?$'

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

def show_attachment(egg, embed: discord.Embed):
    file = None

    if egg.attach_path and os.path.exists(egg.attach_path):
        filename = os.path.basename(egg.attach_path)

        file = discord.File(egg.attach_path, filename=filename)

        embed.set_image(url=f"attachment://{filename}")
    elif getattr(egg, "attach_link", None):
        if not egg.attach_link.startswith(("http://", "https://")):
            return None

        embed.set_image(url=egg.attach_link)

    return file

# this function was heavily assisted by Gemini 3.1 Pro
# this function is also genuinely made of crystal. touch it too hard and it will break. i hate parsing links.
async def resolve_media_url(url: str) -> str | None:
    if not url.startswith(("http://", "https://")):
        return None

    if re.search(SUPPORTED_FILETYPE_REGEX, url, re.IGNORECASE):
        if "tenor.com" in url.lower():
            tenor_id_match = re.search(r'tenor\.com/(?:m/)?([a-zA-Z0-9_-]+)/', url)
            if tenor_id_match:
                return f"https://c.tenor.com/{tenor_id_match.group(1)}/tenor.gif"
        return url

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Discordbot/2.0; +https://discord.com)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status != 200:
                    print(f"[Debug] HTTP {response.status} for {url}")
                    return None
                    
                html = await response.text()

                meta_tags = re.findall(r'<meta[^>]+>', html, re.IGNORECASE)
                
                for tag in meta_tags:
                    if re.search(r'(?:property|name|itemprop)=[\'"](?:og:video|og:image|twitter:image)[\'"]', tag, re.IGNORECASE):

                        content_match = re.search(r'content=[\'"]([^\'"]+)[\'"]', tag, re.IGNORECASE)
                        if content_match:
                            extracted = content_match.group(1)

                            if re.search(SUPPORTED_FILETYPE_REGEX, extracted, re.IGNORECASE):

                                if "tenor.com" in extracted.lower():
                                    tenor_id_match = re.search(r'tenor\.com/(?:m/)?([a-zA-Z0-9_-]+)/', extracted)
                                    if tenor_id_match:
                                        extracted = f"https://c.tenor.com/{tenor_id_match.group(1)}/tenor.gif"

                                return extracted
                                
                print(f"[Debug] Got 200 OK, but no valid media meta tag found for {url}")

        except (aiohttp.ClientError, asyncio.TimeoutError, UnicodeDecodeError) as e:
            print(f"[Debug] Exception resolving {url}: {e.__class__.__name__} - {e!s}")

    return None