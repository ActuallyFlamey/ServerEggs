from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "egg" ADD "attach_hash" VARCHAR(64);
        CREATE INDEX IF NOT EXISTS "idx_egg_attach__91d888" ON "egg" ("attach_hash");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "idx_egg_attach__91d888";
        ALTER TABLE "egg" DROP COLUMN "attach_hash";"""


MODELS_STATE = (
    "eJztmm1v4jgQgP9K5E9dqbeiKdAe34DSLrctnNrs3WpPJ8skQ7BqbOqYpajHfz/ZeSMh4a"
    "BXUKn41s5L4jz2zHhsXtBYeMCCzx3fRw3rBXEyBtSwlsWnFiKTSSrUAkUGzNhBZDAIlCSu"
    "Qg1rSFgApxbyIHAlnSgqOGpYfMqYFgo3UJJyPxVNOX2aAlbCBzUCiRrWX3+fWohyD54hiP"
    "+dPOIhBeZlBkk9/W4jx2o+MbIuV9fGUL9tgF3BpmOeGk/maiR4Yk250lIfOEiiQD9eyake"
    "vh5d9JHxF4UjTU3CIS75eDAkU6aWPneAUxnCuNd38EPHwRhtAcgVXMOlXGkaL8jXQ/jFPq"
    "teVC/P69XLUwuZYSaSi0X46hRM6Gjw9By0MHqiSGhhGKdQFTyrVawOPJdwje1zZAMl82Rj"
    "jktoI3AJ2dgkRZsupz2wXQPO6Xx39JPHQfDEtKD3R/O+/aV5f3LX/P7JaOaR5rbfu4nNhS"
    "RuGCm99m2/ZdinrIlSxB3hCVGjbZDn3I7kX01+RIIC8u0RkWvJx247Ir/XdDImz5gB99UI"
    "Nax6dU0IxAu+Xv2UAxxpbKPKgubBcLZKuCUEA8KLIccuOboDIdgGeFey9SY5JZHsN6m0+v"
    "3bTFJpdfNr99tdq3N/cmaIB0+MKlhO4ylnV4JmgklB8r4iChQdQzHurGcOuhe5fo7/2NUM"
    "7HKJSyBen7N5FFrrsnz3rvPgNO9+z8zKVdPpaI2dSfOx9KSeC4fkIdafXeeLpf+1fvR7HY"
    "NXBMqX5o2pnfMD6TGRqRKYixkm3lIWiKUxtcysg0dfN+kZx+Ocv5c5j+NiadKjFZuLdCFx"
    "0e63Rf3SDXDW7783wocQ2eFe+FfbPj+/sCvn9cta9eKidllJNsWrqnW741b3RmfWzMyupl"
    "ohqU/51vwzbkf8W+HXLeDwsbBfiZb16lxcCwnU519hbuajywNFuAsF9KNm91sA8gCDIFrP"
    "qTStHZLMkrY5F/+CYw8YhNuJdvOh3bzqoIJl/gZcb6Y0DIcPCjYT2MVc9fodEPdxRqSHMw"
    "tZa4QtcpLEdlU1tsd5CeHEN3j0d+hRZ8AXHOskM1J+sOMnJu/maGddcn3LrPoejnf2UtLK"
    "D4EY4f42fXFs/6qG+FVxj8Ckpt23xLUNOuJaaUNcy/fDhDExw9MAJC6GvLY1LvDeY5ccx8"
    "FBNckrW4fyXLzUV/l+UDA1kdf113tgxHxiadGLTs4/SMlb7LJMmX1XQZWK92PlRUoHwrFG"
    "HWvUsUa9aY0aEM7B27I0pU7Hc9tjSTrwktQESd1RUVGKNGvLEklt3k3zdLwX/5/34j9BBt"
    "GOb9OuaMllf43R3u4K7domrZFdKy88RpdrjyaTre5jQ/MPSPesUtmA7lmlUkrX6HKXhIIr"
    "CA9FsoR/e+j3Sm4NUpf8NRF1lfWPxWhwiFcHi3K4Gsb6n3rkf1uQu+TRD9A/ONii9Xz7Yr"
    "b4F7UpCwY="
)
