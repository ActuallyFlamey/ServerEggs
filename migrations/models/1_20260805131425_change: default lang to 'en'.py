from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "guild" ALTER COLUMN "lang" SET DEFAULT 'en';
        ALTER TABLE "user" ALTER COLUMN "lang" SET DEFAULT 'en';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" ALTER COLUMN "lang" SET DEFAULT 'en-us';
        ALTER TABLE "guild" ALTER COLUMN "lang" SET DEFAULT 'en-us';"""


MODELS_STATE = (
    "eJztmm1v4jgQgP9K5E9dqbeiaSk9vgGlXW5bOLXZu9WuVpZJhmDV2NQxS1GP/36y80ZCwk"
    "K3oFLxrYxnEucZe17sPqOR8IAFH9u+j+rWM+JkBKhuLYqPLUTG41SoBYr0mdGDSKEfKElc"
    "herWgLAAji3kQeBKOlZUcFS3+IQxLRRuoCTlfiqacPo4AayED2oIEtWt7z+OLUS5B08QxD"
    "/HD3hAgXmZSVJPv9vIsZqNjazD1ZVR1G/rY1ewyYinyuOZGgqeaFOutNQHDpIo0I9XcqKn"
    "r2cXfWT8ReFMU5Vwigs2HgzIhKmFz+3jVIYw7vYcfN92MEYbAHIF13ApV5rGM/L1FP6wT8"
    "5qZxen52cXxxYy00wktXn46hRMaGjwdB00N+NEkVDDME6hKnhSy1gdeCrhGuvnyAZK5snG"
    "HBfQRuASsrFKijZdTjtguwKc0/7q6CePguCRaUH3n8Zd61Pj7ui28fWDGZlFIze97nWsLi"
    "Rxw53Sbd30moZ9ypooRdwhHhM13AR5zuxAfnPyPBhMl5E3hWBAeDH12CSHuy8EW2OlLwWR"
    "dZZ6ItntWm/2ejeZtd7s5JF+uW22745OzMIPHhlVsBhdUs6uBM0Ek4KYckkUKDqCYtxZyx"
    "x0LzL9GP+xLQ9sM5BLIF6Ps1kUB1cFn85t+95p3P6d8cplw2nrETsTfWLp0fmHrM+Sh1j/"
    "dpxPlv5pfet12wavCJQvzRtTPecb0nMiEyUwF1NMvIVcF0tjahmvg0df5vSM4cHnb8Xn8b"
    "5YcHq0YnM7XUhcVJQ1qV9al2Xtfl2f7cPODku0P2379LRmV07PL6pntVr1opLUastDq4q2"
    "ZudaR9aMZ5dDrZDUp3xj/hmzA/6N8OvOZPBQWEZHy3rZF1dCAvX5Z5gZf3R4oAh3oYB+1I"
    "N9CUDu4SaI1nMqTXOHJNOkm8vtf8GxBwzCcqLVuG81LtuoYJm/AtfrCQ23wzsFm9nYxVz1"
    "+u0T92FKpIczC1mPCFvkJInu8tDIHuUlhBPf4NHfoWedAV9w2pB4pPy8wU9U3syJw6rg+p"
    "pR9S2cOuwkpZWfTTDC/WUHtIZEFuOP9V/UIb9o3yMwoWkrLhiRJ8yA+2qI6lZ1Bdz4ZKKa"
    "qwbjIwtbj+ROIhgTUzwJQOJiyCtb4wLrHXbJ8T7YqyZ5qXQoj8ULfZXvBwWuiayuPt8BI+"
    "YTS5NedKD7TlLefJtpytRdBVkqrsfKk5TeCIccdchRhxz1qjmqTzgHb8PUlBodzm0PKWnP"
    "U1IDJHWHRUkpGlmZlkiq82aap8N17W9e1/4EGUQV37pd0YLJ7hqjbfammcbIrq7TGtnV8s"
    "RjxnLt0Xi8CeFI/R3SPalU1qB7UqmU0jVjuUtCwRWEhyJZwn/d97oltwapSf6aiLrK+s9i"
    "NNjHq4N5OVwNY/V/IOSvvHOXPPoB+h58g9bz9ZPZ/H/w+ZeF"
)
