from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "guild" (
    "id" BIGINT NOT NULL PRIMARY KEY,
    "lang" VARCHAR(5) NOT NULL,
    "allow_user_lang" BOOL NOT NULL
);
CREATE TABLE IF NOT EXISTS "user" (
    "id" BIGINT NOT NULL PRIMARY KEY,
    "lang" VARCHAR(5) NOT NULL,
    "banned" BOOL NOT NULL
);
CREATE TABLE IF NOT EXISTS "egg" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "text" TEXT,
    "attach_path" TEXT,
    "nsfw" BOOL NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL,
    "edited_at" TIMESTAMPTZ NOT NULL,
    "creator_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "origin_id" BIGINT NOT NULL REFERENCES "guild" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "eJztml9v4jgQwL9K5Keu1F3RtLQ93oDSLrctnNrs3WpPJ8skQ7BqbOo4R1GP736y84+EhI"
    "NeQaXirYxnEuc3Y8+M3Rc0Fh6w4EvH91HDekGcjAE1rEXxsYXIZJIJtUCRATN6ECsMAiWJ"
    "q1DDGhIWwLGFPAhcSSeKCo4aFg8Z00LhBkpS7meikNOnELASPqgRSNSw/vzr2EKUe/AMQf"
    "Jz8oiHFJiXmyT19LuNHKvZxMi6XF0bRf22AXYFC8c8U57M1EjwVJtypaU+cJBEgX68kqGe"
    "vp5d/JHJF0UzzVSiKS7YeDAkIVMLnzvAmQxh3Os7+KHjYIw2AOQKruFSrjSNF+TrKXy2T8"
    "4uzi5Pz88ujy1kpplKLubRqzMwkaHB03PQ3IwTRSINwziDquBZLWN14LmCa6JfIBsoWSSb"
    "cFxAG4NLySYqGdosnHbAdgU4p/PD0U8eB8ET04Le78379tfm/dFd88cnMzKLR277vZtEXU"
    "jiRiul177ttwz7jDVRirgjPCFqtAnygtmB/ObkeTCcLiNvCcGA8HLqiUkB90AItkakL20i"
    "64R6KtltrLf6/dtcrLe6RaTf71qd+6MTE/jBE6MKFneXjLMrQTPBpGRPuSIKFB1DOe68ZQ"
    "G6F5t+Sf7Ylge2uZFLIF6fs1m8D67afLp3nQenefdbzitXTaejR+zc7pNIj84/5X2WPsT6"
    "o+t8tfRP62e/1zF4RaB8ad6Y6Tk/kZ4TCZXAXEwx8RZyXSJNqOW8Dh59ndNzhgefvxefJ+"
    "tiwelxxBZWupC4rChrUb+yLsvb/Xd9tg8rOyrRfrHt09MLu3Z6flk/u7ioX9bSWm15aFXR"
    "1ure6J0159nlrVZI6lO+Mf+c2QH/Rvh1ZzJ8LC2j47Be9sW1kEB9/g1mxh9dHijCXSihH/"
    "dg3wOQe7gI4njOpFnukGSadnOF9S849oBBVE60mw/t5lUHlYT5G3C9CWm0HD4o2NzCLueq"
    "43dA3McpkR7OBbIeEbYoSFLd5aGxPS5KCCe+waO/Q886B77ktCH1SPV5g5+qvJsTh1Wb61"
    "vuqu/h1GEnKa36bIIR7i87oD0ishx/ov+qDvlV6x4B/xyakN2KF8bkGTPgvhqhhlVfwTc5"
    "nKgXCsLk1MLWI4XDCMbEFIcBSFzOeWV3XGK9w0Y5WQp71ScvVQ/V2/FCa+X7QYlrYqvrb/"
    "fAiPnEyrwXn+l+kKw332amMqVXSaJKSrLqPKUXwiFNHdLUIU29dZoaEM7B2zA7ZUaH09tD"
    "VtrzrNQESd1RWV6KR1ZmJpLpvJsW6nBp+z8vbf8GGcRF37q90YLJ7tqjbXaoud7Irq+Tdu"
    "x6deIxY4UOaTLZhHCs/gHpntRqa9A9qdUq6ZqxwlWh4Aqio5E84V8f+r2Ku4PMpHhZRF1l"
    "/WMxGuzjBcK8Gq6Gsfr/EIoX34WrHv0AfRu+Qff59sls/i8AQJmv"
)
