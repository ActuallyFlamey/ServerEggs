import os


def safe_remove(path: str | None) -> None:
    if not path or not os.path.exists(path):
        return

    try:
        os.remove(path)
    except OSError:
        print(f"log: failed to delete file {path}")

def truncate(text: str | None, limit: int) -> str | None:
    if not text:
        return None

    return text[:limit] + ("…" if len(text) > limit else "")

async def egg_delete(egg):
    safe_remove(egg.attach_path)

    await egg.delete()