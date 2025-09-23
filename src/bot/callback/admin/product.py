from aiogram.filters.callback_data import CallbackData

from src.bot.callback.base import BasePageCallback


class AdmProductListCallbackFactory(BasePageCallback, prefix="adm_products"): ...


class AdmProductIDCallbackFactory(CallbackData, prefix="adm_prodID"):
    product_id: int


class AdmChangeProductCallbackFactory(CallbackData, prefix="adm_upd_product"):
    product_id: int
    field: str

class AdmChangeProductImgCallbackFactory(CallbackData, prefix="adm_upd_img"):
    product_id: int

class AdmCreateProductCallbackFactory(BasePageCallback, prefix="adm_create_product"): ...


class CreateProductCategoryCallbackFactory(CallbackData, prefix="adm_cp_category"):
    category_id: int
    category_name: str


class AdmCreateProductConfirmCallbackFactory(CallbackData, prefix="admin_cp_confirm"):
    confirm: bool