from src.application.schemas.product import ProductFullInfo


def build_product_view(
    product_info: ProductFullInfo
) -> str:

    msg = (
        f"Товар: {product_info.name}\n"
        f"Описание: {product_info.description}\n"
        f"Цена: {product_info.price} руб.\n\n"
        f"В наличии: {product_info.quantity} шт."
    )

    return msg

