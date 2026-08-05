from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "guild" ADD "invite" TEXT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "guild" DROP COLUMN "invite";"""


MODELS_STATE = (
    "eJztmltv4jgUgP9K5KeO1B3RlEuXN6C0w04LozYzO5rVyjKJCVaNTR0zFHX57yM795CwpF"
    "tQ6eatPT6HOJ99Lj7OM5hxB1PvY991Qdt4BgzNMGgbSfGpAdB8HguVQKIx1Xo4UBh7UiBb"
    "grYxQdTDpwZwsGcLMpeEM9A22IJSJeS2JwVhbixaMPK4wFByF8spFqBt/PX3qQEIc/AT9s"
    "J/5w9wQjB1UpMkjnq2lkO5mmvZgMkrraieNoY2p4sZi5XnKznlLNImTCqpixkWSGL181Is"
    "1PTV7IKXDN/In2ms4k8xYePgCVpQmXjdMYxlAMLhyIL3fQtCUAKQzZmCS5hUNJ6Bq6bwm3"
    "lWb9Uvzpv1i1MD6GlGktbaf3QMxjfUeIYWWOtxJJGvoRnHUCV+kptYLfxUwDXUz5D1pMiS"
    "DTkm0AbgIrKhSow23k4HYLsFnNX/bqlfnnneI1WC4bfOXe9T5+7ktvP9gx5ZBSM3o+F1qM"
    "4Fsn1PGfZuRl3NPmaNpET2FM6RnJZBnjGryL+Y/BR5OeR7UyS2kg/N9kT+oOFkhp4gxcyV"
    "U9A2mvUtLhBu+Gb9QwZwMGLqoTRo5k2Wm4S7nFOMWD7k0CRDd8w53QHvRrTeJaZEksMGle"
    "5odJMKKt1Bdu9+ve32707ONHHvkRKJk2E85mwLrJhAlBO8L5HEksxwPu60ZQa6E5h+DP/Y"
    "1wrsc4sLjJwRo6vAtbZF+cFt/97q3H5Jrcplx+qrETMV5kPpSTPjDtGPGH8OrE+G+tf4MR"
    "r2NV7uSVfoJ8Z61g+g5oQWkkPGlxA5iSgQSkNqqVXHDnnZoqcMqzV/K2se+kVi0YMdm/F0"
    "LmBe9dslbmEBnLb790L4GDzbr4V/N83z85ZZO29eNOqtVuOiFhXFm0PbquPu4FpF1tTKbo"
    "ZaLohLWGn+KbMKfyn86gg4ecg9rwTbenMtrrjAxGWf8Uqvx4B5EjEb59APDrtfPSyO0AmC"
    "/RxL49wh0DI6Nmf8nzPoYIr9cqLXue91LvsgZ5u/AtfrBfHd4Z2CTTl2Ple1f8fIflgi4c"
    "DURlYj3OQZSaS7OTQzZ1kJYsjVeNR7qFmnwOe0daIVKW7suJHKm2ntbAuurxlV30J75yAp"
    "rbgJlJx8icZExqxqTJRvTBD2U53xSkCPLSre5XlTxNwyHaBQ/0WsX5ThANbOtP/mT2OH3k"
    "+jsPXTyHZ+EKV8CRceFjAf8tYmUI71AftBYcQ/qnbQRpFcXHUkOgiu6+UsTWB19fkOU1QQ"
    "z9N3RO+kuFvvsyDTJ4yceiw8eRSXY8oRqmrsf1qNVTlqXzlqjBjDTsnUFBtVNxRVSjrylN"
    "TBgtjTvKQUjGxNSyjWeTNtguoLkP/4BchPLLzcg3/xqShhcriD0cFuxc3GLmnHbBQnHj2W"
    "OR7N56W+PPDV3yHds1ptB7pntVohXT2WuQ7nTGK//Zcm/Mf9aFhwPxabZC9EiS2NfwxKvG"
    "O8JFsXw1Uwtn/UlG2eZK4z1Q+ojkqJo+frJ7P1L6Zu99o="
)
