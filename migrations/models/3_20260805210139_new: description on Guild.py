from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "guild" ADD "description" TEXT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "guild" DROP COLUMN "description";"""


MODELS_STATE = (
    "eJztml9z4jYQwL+KR0+5mfSGOEBS3oCQHL0EOomvvblORyNsYTQREpFECZPy3TuS/xub4j"
    "QwIeUtWe3a8m+l3dWKFzDlHqbyc8/3Qct6AQxNMWhZafGpBdBslgi1QKERNXo4VBhJJZCr"
    "QMsaIyrxqQU8LF1BZopwBloWm1OqhdyVShDmJ6I5I09zDBX3sZpgAVrWH3+eWoAwDz9jGf"
    "07e4RjgqmXmSTx9LuNHKrlzMj6TF0bRf22EXQ5nU9ZojxbqglnsTZhSkt9zLBACuvHKzHX"
    "09ezCz8y+qJgpolKMMWUjYfHaE5V6nNHMJEBCAdDBz70HAhBBUAuZxouYUrTeAG+nsJP9l"
    "n9on553qxfnlrATDOWXKyCVydgAkODZ+CAlRlHCgUahnECVeFntY7Vwc8lXCP9HFmpRJ5s"
    "xDGFNgQXk41UErTJctoD2w3gnN53Rz95KuUT1YLBb+377pf2/cld+/snM7IMR26Hg5tInQ"
    "vkBjtl0L0ddgz7hDVSCrkTOENqUgV5zuxI/tXkJ0gWkO9OkNhIPjLbEfm9hpMpeoYUM19N"
    "QMtq1jdsgWjBN+ufcoDDEdsMZUEzOV6sE+5wTjFixZAjkxzdEed0C7xr0XqbmBJL9htUOs"
    "PhbSaodPr5tfvtrtO7PzkzxOUTJQqnw3jC2RVYM4GoIHhfIYUVmeJi3FnLHHQvNP0c/bEr"
    "D+xyiQuMvCGjy3BrbYry/bveg9O++zXjlau209MjdibMR9KTZm47xA+xfu87Xyz9r/VjOO"
    "gZvFwqX5g3JnrOD6DnhOaKQ8YXEHmpKBBJI2oZr2OPvM7pGcOjz9+Lz6N9kXJ6uGJzO50L"
    "WFT9dohfWgBn7f69ED6EnR3Uwj/b9vn5hV07b1426hcXjctaXBSvD22qjjv9Gx1ZM55dD7"
    "VcEJ+wyvwzZkf8lfDrI+D4sfC8Ei7rdV9cc4GJz77ipfFHn0mFmIsL6IeH3W8SiwPcBOF6"
    "TqRJ7hBoER+bc/ufM+hhioNyott+6LaveqBgmb8B15s5CbbDBwWb2djFXPX6HSH3cYGEBz"
    "MLWY9wm+ckse760NSe5iWIId/g0d+hZ50BX9DWiT1S3tjxY5V309rZFFzfMqq+h/bOXlJa"
    "eRMoPfkKjYmc2bExUb0xQRHzq3QkIv1XsX5VxAXYOHf3zYjGFr2IRmkropHvRCBK+QLOJR"
    "awGPLGpkSB9R77E1EEOqj2xFrRVp4FUyda35cFrgmtrr/eY4pK4kv2zuKDFBurXRYIpuIt"
    "qA+iSri8PNAb4Vgd/E+rg2OO2lWOGiHGsFcxNSVGx475MSUdeEpqY0HcSVFSCkc2piWU6L"
    "ybY+vxFwn/8RcJf2EhCw+i5aeilMn+DkZ7u6W1G9ukHbtRnnjMWO54NJtVugkP1D8g3bNa"
    "bQu6Z7VaKV0zlrue5UzhoB2VJfzLw3BQcl+TmOQv6IirrL8tSuQhXtqsyuFqGJt/ZJNvnu"
    "Su1/QDdEelwtHz7ZPZ6h/tc4OF"
)
