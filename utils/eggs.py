import os


async def egg_delete(egg):
    if egg.attach_path and os.path.exists(egg.attach_path):
        try:
            os.remove(egg.attach_path)
        except OSError:
            print(f"log: failed to delete attachment for Egg {egg.id}")
        
    eggid = egg.id

    await egg.delete()

    return eggid