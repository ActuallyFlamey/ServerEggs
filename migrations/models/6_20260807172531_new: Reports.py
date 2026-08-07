from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "report" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL,
    "egg_id" INT NOT NULL REFERENCES "egg" ("id") ON DELETE CASCADE,
    "reporter_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_report_egg_id_184ac7" UNIQUE ("egg_id", "reporter_id")
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "report";"""


MODELS_STATE = (
    "eJztm21T4joUx79Kp6/cGe8OIqiXd4DoclfhDrL37uzOTie0x5IxJJiGVcfrd7+TtCU0bZ"
    "GqoGLfyUlOk/7ycE7+qff2hHlAgs8d37cb1r1N0QTshrVo3rVsNJ1qozQINCKqHkQVRoHg"
    "yBV2w7pEJIBdy/YgcDmeCsyo3bDojBBpZG4gOKa+Ns0ovp6BI5gPYgzcblg/f+1aNqYe3E"
    "IQ/5xeOZcYiJfoJPZk28ruiLupsnWpOFEVZWsjx2VkNqG68vROjBmd18ZUSKsPFDgSIB8v"
    "+Ex2X/Yuesn4jcKe6iphFxd8PLhEMyIWXnfkaJvtOL3+0LnoDB3HLgDIZVTCxVRIGve2L7"
    "vwR3Wvdlg72j+oHe1aturm3HL4EDatwYSOCk9vaD+ociRQWEMx1lAF3Io01iHc5nCN6xtk"
    "A8FNsjHHBbQRuDnZuIpGq6fTBtguATfsfB/KJ0+C4JpIQ++f5qD9pTnYOW9+/6RK7qKSs3"
    "7vNK7OOHLDldJrn/Vbir1mjYRA7tiZIjEugtxwK8k/mfwYBRnk22PEl5KP3dZEfqPbyQTd"
    "OgSoL8Z2wzqoLVkC8YQ/qH0yAEclVVWUCZpgevWEKR67lVO8+BSnweVNGnmLMQKIZlOPXQ"
    "zcI8bIChM7FSdX2c3nls1u561+/yyxnbe6JtJv563OYGdPzfXgmmABiwFUc3Y5SCYOygib"
    "x0iAwBPIxp30NKB7kevn+I91jcA6NxcOyOtTchdtasvia/e8czFsnv+dGJXj5rAjS6qJAB"
    "tbdw6MjWj+EOvf7vCLJX9aP/q9jsLLAuFz1aKuN/xhyz6hmWAOZTcO8hb239gaU0uMOnj4"
    "aYOecCzH/K2MebwuFgY9mrHGSmfcyTp3tLCfe/RI+j1+BHkPKzs8hfxZre7vH1Yr+wdH9d"
    "rhYf2oMj+OpIuWnUta3VO5syZGNr3VMo59TAvzT7iV+Avhl4fvy6vMk2I0rdNjccI4YJ9+"
    "hTs1Hl0aCERdyKAfyQzfAuDvcBFE81lbdezg6GYuWBjrn1HHAwJhOtFuXrSbxx07Y5q/AN"
    "fTGQ6Xw5aCTSzsbK5y/o6Qe3WDuOfkTGQOU8ZFkLGpRI4nXwdAkHqLXNYD9ZAtgq3QsSpb"
    "QJaAmS6aVCemBVHkq1eSbcuWEjMzQ3GcT9l8zdGfV3kzquOy6POSYectKI8bifn5+uRi5w"
    "sICoZbKSgUFxQw/S0PwQWga4+Sd3HeBFG/iDgZ138S6ydFJRvUYlq/LllfQZas56qS9ZQo"
    "SQi7cWYBcCcb8lKVLMN7g4JZvOO/K70sdYpYJS0D339mThZdX5YJ2eMJWZS+ZmRkOrHNT8"
    "nCDPrlc7Kf8QVz2ABw+9drp2nv5H74lbO0UhT/kKK472eKc7mLTjtskyz3zG8zTGECiivO"
    "huM2wX1dzTMKR8/U5bYrLzFVOb2oH5c653G9FJEfoWos6aJq5zrFPCXfZ2SOsayfnzfKQ1"
    "Sp5H3QHLHUN9alb4wQpeAVlDW0U/n5TylnbOB+KZ0HlFdwG7yCawLH7jgrbkclSyM30nXe"
    "zC3cR9F21vbt/2/gQea9Wv6lw4LL5u4dNvY9dLW+SmSu1vNjsyozbh+m0yKEo+pbSHevUl"
    "mB7l6lkktXlRmf4zIqIFzaScJ/XfR7Od/naRfzg0zsCus/i+DgPSomD/lwJYyEqJj6dxbz"
    "btJQC+UD5IVlgZudlw9mD/8Dryd1uA=="
)
