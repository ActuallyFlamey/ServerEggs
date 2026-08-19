import asyncio
import mimetypes
import os

import aiohttp
import discord


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
    guessed_mime, _ = mimetypes.guess_type(file.filename)
    headers = {"Content-Type": guessed_mime or "application/octet-stream"}

    try:
        async with aiohttp.ClientSession() as session, session.post(endpoint, auth=auth, data=scanbytes, headers=headers, timeout=20) as response:
                if response.status == 200:
                    data = await response.json()

                    classification = data.get("classification", "")
                    if classification in ["csam", "harmful-abusive-material"]:
                        print(f"CRITICAL: HARMFUL CONTENT DETECTED: {classification}")
                        return True, None

                    return False, scanbytes
                else:
                    print(f"ERROR: Arachnid Shield Media Error: HTTP {response.status} {await response.text()}")
                    return False, scanbytes
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        print(f"ERROR: Arachnid Shield connection error: {e}")
        return False, scanbytes