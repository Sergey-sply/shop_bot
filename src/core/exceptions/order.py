from typing import Any


class OutOfStock(Exception):
    def __init__(self, stock_ex: list[dict[str, Any]]):
        self.stock_ex = stock_ex
        super().__init__(self.stock_ex)


class EmptyUserCart(Exception):
    def __init__(self, user_id: int | str):
        self.user_id = user_id
        super().__init__(self.user_id)