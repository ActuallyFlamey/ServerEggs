from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" ALTER COLUMN "lang" SET DEFAULT '';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" ALTER COLUMN "lang" SET DEFAULT 'en';"""


MODELS_STATE = (
    "eJztm21T4joUx79Kp6/cGe8OIqiXd6DoclfhjrL37uzOTie0x5KxJJiEVcfrd7+TtCU0bZ"
    "GioGDfaZLTpL88nJP/KY/2iHoQ8M9t37cb1qNN0AjshjVbvGvZaDzWhbJAoEGg2kHUYMAF"
    "Q66wG9Y1CjjsWrYH3GV4LDAldsMikyCQhdTlgmHi66IJwbcTcAT1QQyB2Q3r569dy8bEg3"
    "vg8b/jG+caQ+AlBok92bcqd8TDWJV1iDhVDWVvA8elwWREdOPxgxhSMm2NiZClPhBgSIB8"
    "vGATOXw5uugl4zcKR6qbhEOcsfHgGk0CMfO6A0eX2Y7T7fWdq3bfcewCgFxKJFxMhKTxaP"
    "tyCH9U92qHtaP9g9rRrmWrYU5LDp/CrjWY0FDh6fbtJ1WPBApbKMYaqoB7kcbah/scrnF7"
    "gywXzCQbc5xBG4Gbko2baLR6Oa2B7Rxw/fb3vnzyiPPbQBZ0/2leHn9pXu5cNL9/UjUPUc"
    "15r3sWN6cMueFO6R6f91qKvWaNhEDu0BkjMSyC3DAryS9Nfoh4BvnjIWJzycdmKyK/1uNk"
    "hO6dAIgvhnbDOqjN2QLxgj+ofTIARzVVVZUJOsDkZoklHpuVS7z4Eif8+i6NvEVpAIhkU4"
    "9NDNwDSoMFFnbKTy5ymk9L1nuct3q988Rx3uqYSL9dtNqXO3tqrfPbAAuYdaCas8tAMnFQ"
    "hts8QQIEHkE27qSlAd2LTD/Hf6xqBlZ5uDBAXo8ED9GhNs+/di7aV/3mxd+JWTlp9tuypp"
    "pwsHHpzoFxEE0fYv3b6X+x5L/Wj163rfBSLnymetTt+j9sOSY0EdQh9M5B3sz5G5fG1BKz"
    "Dh5ebtIThuWcv5c5j/fFzKRHK9bY6ZQ5WfeOFvZzrx5Ju+evIJuws8NbyJ/V6v7+YbWyf3"
    "BUrx0e1o8q0+tIumrevaTVOZMna2Jm00ctZdjHpDD/hFmJvxB+efm+vsm8KUbLOj0Xp5QB"
    "9slXeFDz0SFcIOJCBv1IZvjGgW3gJojWsy7VvoOhu6lgYex/ShwPAgjDiePm1XHzpG1nLP"
    "NX4Ho2weF22FKwiY2dzVWu3wFyb+4Q85ychcxgTJngGYdKZHj69RICpN4il/WlesgWwVbo"
    "aJXOIEvATFeNqiOzBBHkq1eSfcueEiszQ3GcLtl8zdGfNnk3quM87/Oabuc9KI9r8fn5+u"
    "Ts4AsICoZZKSgUFxQw+S0vwQWga4uSd3HeASJ+EXEybr8U66W8kg1qM61el6wvIEvWc1XJ"
    "ekqUDAJ650w4MCcb8lyVLMN6jYJZfOJvlF6WukUsEpaB778wJovSl2VA9nxAFoWvGRGZDm"
    "zzQ7Iwgn79mOxnnGAOOwBm/3rrMG1D8sNvHKUxQDwrQMv3XtpiG2KFpPuqVioLOLBqpZLr"
    "wlSdER5Q3xkB58iHwopY2nap+8l7g/4momSZ//mQ+R/fz9x1uVtOG2yTAv3Cz5BMDQ6KJ1"
    "cMw22C+7byfhR5vVCC3q4Q3BSg9aZ+XtWfhrBlvuQZqsaWLirsr1K3VpmqjEtSnMHKvyJJ"
    "vaAUrT/odWgDpLyNFPIGiBDwCup32qj8zq3U7daQSE1HAWWueY255iYw7A6zvHZUM9dvI9"
    "3m3aSbP4qIubIfufwGxjMTyPkuecZkfV55fQplfRHPXK3n+2ZVZ6TZxuMihKPmW0h3byH9"
    "d2+O/qvqDN2REgHh1k4S/uuq1835EFWbmF8eY1dY/1kB5puolzzlw5UwEpJi6ndbZhLe0A"
    "rlA2RmvkAK8/Wd2dP/glNeww=="
)
