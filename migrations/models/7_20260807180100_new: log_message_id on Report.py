from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "report" ADD "log_message_id" BIGINT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "report" DROP COLUMN "log_message_id";"""


MODELS_STATE = (
    "eJztm21T4joUx79Kp6/cGe8OIqiXd6DoclfhjrL37uzOTie0x5IxJJiERcfrd7+TtKU0bZ"
    "GioGLf6UlOk/7ydPI/5cEeMQ+I+Nz2fbthPdgUjcBuWPPmXctG43FsVAaJBkTXg7DCQEiO"
    "XGk3rGtEBOxatgfC5XgsMaN2w6ITQpSRuUJyTP3YNKH4dgKOZD7IIXC7Yf38tWvZmHpwBy"
    "L6d3zjXGMgXqKT2FNta7sj78fa1qHyVFdUrQ0cl5HJiMaVx/dyyOisNqZSWX2gwJEE9XjJ"
    "J6r7qnfhS0ZvFPQ0rhJ0cc7Hg2s0IXLudQdObLMdp9vrO1ftvuPYBQC5jCq4mEpF48H2VR"
    "f+qO7VDmtH+we1o13L1t2cWQ4fg6ZjMIGjxtPt24+6HEkU1NCMY6gS7mQaax/ucrhG9Q2y"
    "QnKTbMRxDm0IbkY2qhKjjafTBtguANdvf++rJ4+EuCXK0P2neXn8pXm5c9H8/kmX3Icl57"
    "3uWVSdceQGK6V7fN5rafYxayQlcofOGMlhEeSGW0l+ZfJDJDLIHw8RX0g+clsT+Y1uJyN0"
    "5xCgvhzaDeugtmAJRBP+oPbJAByWVHVRJmiC6c0KUzxyK6d48SlOxfU0jbzFGAFEs6lHLg"
    "buAWNkiYmdOieX2c1nls1u561e7zyxnbc6JtJvF6325c6enuvilmAJ8wdozNnloJg4KOPY"
    "PEESJB5BNu6kpwHdC10/R3+sawTWublwQF6PkvtwU1t0vnYu2lf95sXfiVE5afbbqqSaOG"
    "Aj686BsRHNHmL92+l/sdS/1o9et63xMiF9rluM6/V/2KpPaCKZQ9nUQd7c/htZI2qJUQcP"
    "rzboCcdyzN/KmEfrYm7QwxlrrHTGnax7Rwv7uVePpN/TV5D3sLKDW8if1er+/mG1sn9wVK"
    "8dHtaPKrPrSLpo0b2k1TlTO2tiZNNbLePYx7Qw/4Rbib8QfnX5vr7JvCmG0zo9FqeMA/bp"
    "V7jX49GhQiLqQgb9UGb4JoC/w0UQzufYGp8dHE1ngoWx/hl1PCAQhBPHzavj5knbzpjmL8"
    "D1bIKD5bClYBMLO5urmr8D5N5MEfecnInMYcy4FBmbSuh4+vUSCNJvkcv6Uj9ki2BrdKzK"
    "5pAlYKaLRtWRaUEU+fqVVNuqpcTMzFAcZ1M2X3P0Z1XejOq46PR5yWPnLSiPGznz8/XJ+c"
    "4XEBQMt1JQKC4oYPpbXYILQI89St7FeRNE/SLiZFR/JdYrnUo26MW0fl2yvoQsWc9VJesp"
    "UZIQNnUmAriTDXmhSpbhvUHBLNrx35VelrpFLBOWge8/MyYL05dlQPZ0QBaGrxkRWRzY5o"
    "dkQQT98jHZzyjBHDQA3P712mHaO8kPv3KURpjvjEAI5ENhuSbtu1Lw/MZyy6+jmJXJiQ+Z"
    "nPD9zFWXu+Rih22SR5/5jYwpEEFx5d9w3Ca4r6s9h2HBM/XR7YoPTXU0XtRPS86z+KoU85"
    "+gaizpoqrzOkVVnUbJiOCj9Ep+/K4us6Wi+lFj9VJnWpPONECUgldQXoqdys+wSllpA3m+"
    "dBxQpkI3mAptAsfuMOvcDksWntworvNmsqEfRWNb228wfgMXmfnN/OTPnMvm8j8b+y69Wl"
    "/mZK7W889mXWZkgcbjIoTD6ltId69SWYLuXqWSS1eXGcojoxKCpZ0k/NdVr5vznWTsYn4Y"
    "i11p/WcRLN6jYvKYD1fBSIiKqZ8VmTliQy1UD1CJ4wIZtpc/zB7/B06V7zI="
)
