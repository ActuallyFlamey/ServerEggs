import asyncio
import io
import logging
import mimetypes
import os
import re

import aiohttp
import discord
import dotenv
import imagehash
from PIL import Image

dotenv.load_dotenv()

logger = logging.getLogger("eggsmedia")

SUPPORTED_FILETYPE_REGEX = r'\.(gif|png|jpg|jpeg|webp|mp4|webm|mov)(?:[?#].*)?$'

async def process_attachment(attach: discord.Attachment, prebytes: bytes | None):
    attach_bytes = prebytes if prebytes else await attach.read()

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

async def url_to_file(url: str) -> discord.File | None:
    file = None

    try:
        async with aiohttp.ClientSession() as session, session.get(url, timeout=10) as res:
            if res.status == 200:
                filebytes = await res.read()
                with io.BytesIO(filebytes) as stream:
                    file = discord.File(stream)
    except (aiohttp.ClientError, asyncio.TimeoutError):
        pass

    return file

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

async def scan_csam(file: discord.File) -> (bool, bytes):
    scanbytes = file.fp.read()
    file.fp.seek(0)

    api_user = os.getenv("ARACHNID_USER")
    api_password = os.getenv("ARACHNID_PASSWORD")

    if not api_user or not api_password:
        print("[Warning] Arachnid Shield credentials missing. Skipping CSAM scan.")
        return False, scanbytes

    endpoint = "https://shield.projectarachnid.com/v1/media"
    auth = aiohttp.BasicAuth(api_user, api_password)

    content_type, _ = mimetypes.guess_type(file.filename)
    headers = {"Content-Type": content_type or "application/octet-stream"}

    try:
        async with aiohttp.ClientSession() as session, session.post(endpoint, auth=auth, data=scanbytes, headers=headers, timeout=15) as response:
            if response.status == 200:
                data = await response.json()

                classification = data.get("classification", "")

                if classification in ["csam", "harmful-abusive-material"]:
                    logger.critical(f"HARMFUL CONTENT DETECTED: {classification}")
                    return True, None

                return False, scanbytes
            else:
                print(f"Arachnid Shield API Error: HTTP {response.status} {response.text}")
                return False, scanbytes
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        print(f"Arachnid Shield API connection failed: {e}")
        return False, scanbytes

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