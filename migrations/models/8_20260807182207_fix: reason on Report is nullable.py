from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "report" ADD "reason" VARCHAR(200);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "report" DROP COLUMN "reason";"""


MODELS_STATE = (
    "eJztm21T4joUx79Kp6/cGe8OIqiXd6DoclfhjrL37uzOTie0x5KxJJiERcfrd7+TtCU0bZ"
    "GioGLfaZLTpL88nJP/KQ/2iHoQ8M9t37cb1oNN0AjshjVfvGvZaDzWhbJAoEGg2kHUYMAF"
    "Q66wG9Y1CjjsWrYH3GV4LDAldsMikyCQhdTlgmHi66IJwbcTcAT1QQyB2Q3r569dy8bEgz"
    "vg8b/jG+caQ+AlBok92bcqd8T9WJV1iDhVDWVvA8elwWREdOPxvRhSMmuNiZClPhBgSIB8"
    "vGATOXw5uugl4zcKR6qbhEOcs/HgGk0CMfe6A0eX2Y7T7fWdq3bfcewCgFxKJFxMhKTxYP"
    "tyCH9U92qHtaP9g9rRrmWrYc5KDh/DrjWY0FDh6fbtR1WPBApbKMYaqoA7kcbah7scrnF7"
    "gywXzCQbc5xDG4GbkY2baLR6OW2A7QJw/fb3vnzyiPPbQBZ0/2leHn9pXu5cNL9/UjX3Uc"
    "15r3sWN6cMueFO6R6f91qKvWaNhEDu0BkjMSyC3DArya9Mfoh4BvnjIWILycdmayK/0eNk"
    "hO6cAIgvhnbDOqgt2ALxgj+ofTIARzVVVZUJOsDkZoUlHpuVS7z4Eif8eppG3qI0AESyqc"
    "cmBu4BpcESCzvlJ5c5zWclmz3OW73eeeI4b3VMpN8uWu3LnT211vltgAXMO1DN2WUgmTgo"
    "w22eIAECjyAbd9LSgO5Fpp/jP9Y1A+s8XBggr0eC++hQW+RfOxftq37z4u/ErJw0+21ZU0"
    "042Lh058A4iGYPsf7t9L9Y8l/rR6/bVngpFz5TPep2/R+2HBOaCOoQOnWQN3f+xqUxtcSs"
    "g4dXm/SEYTnnb2XO430xN+nRijV2OmVO1r2jhf3cq0fS7ukryHvY2eEt5M9qdX//sFrZPz"
    "iq1w4P60eV2XUkXbXoXtLqnMmTNTGz6aOWMuxjUph/wqzEXwi/vHxf32TeFKNlnZ6LU8oA"
    "++Qr3Kv56BAuEHEhg34kM3zjwN7hJojWsy7VvoOh6UywMPY/JY4HAYThxHHz6rh50rYzlv"
    "kLcD2b4HA7bCnYxMbO5irX7wC5N1PEPCdnITMYUyZ4xqESGZ5+vYQAqbfIZX2pHrJFsBU6"
    "WqVzyBIw01Wj6sgsQQT56pVk37KnxMrMUBxnSzZfc/RnTd6M6rjI+7yk23kLyuNGfH6+Pj"
    "k/+AKCgmFWCgrFBQVMfstLcAHo2qLkXZx3gIhfRJyM26/EeiWvZIPaTOvXJetLyJL1XFWy"
    "nhIlg4BOnQkH5mRDXqiSZVhvUDCLT/x3pZelbhHLhGXg+8+MyaL0ZRmQPR2QReFrRkSmA9"
    "v8kCyMoF8+JvsZJ5jDDoDZv147THsn+eFXjtIYIJ4VoOV7L22xDbFC0n1VK5UlHFi1Usl1"
    "YarOCA+o74yAc+RDYUUsbbvS/eStQX8VUbLM/3zI/I/vZ+663C2nDbZJgX7mZ0imBgfFky"
    "uG4TbBfV15P4q8nilBb1cIbgrQelM/rerPQtgyX/IEVWNLFxX216lbq0xVxiUpzmDlX5Gk"
    "XlCK1h/0OlRKeeuS8gaIEPAKKnjaqPzSrVTuNpBKTccBZbZ5g9nmJjDsDrP8dlSz0HMj3e"
    "bNJJw/ioy5tp+5/AbGcTGFcs5kcym2zWmU9WU8c7We75tVnZFoG4+LEI6abyHdvaUU4L0F"
    "CrCqM5RHSgSEWztJ+K+rXjfnU1RtYn57jF1h/WcFmL9HxeQxH66EkRAVU7/cMtPwhlooHy"
    "Bz8wWSmC/vzB7/B2QcX5Y="
)
