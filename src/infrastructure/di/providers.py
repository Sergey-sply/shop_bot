from dishka import Provider, Scope, provide

from src.application.ports.repository.cart import CartRepositoryPort
from src.application.ports.repository.category import CategoryRepositoryPort
from src.application.ports.repository.delivery_method import DeliveryMethodRepositoryPort
from src.application.ports.repository.order import OrderRepositoryPort
from src.application.ports.repository.product import ProductRepositoryPort
from src.application.ports.repository.user import UserRepositoryPort
from src.application.ports.services.cart import CartServicePort
from src.application.ports.services.category import CategoryServicePort
from src.application.ports.services.delivery_method import DeliveryMethodServicePort
from src.application.ports.services.order import OrderServicePort
from src.application.ports.services.product import ProductServicePort
from src.application.ports.services.user import UserServicePort
from src.application.use_cases.order.create import CreateOrderUseCase
from src.application.use_cases.order.update import UpdateOrderStatusUseCase
from src.application.use_cases.user.get_or_create import GetOrCreateUserUseCase
from src.infrastructure.repository.cart import CartRepository
from src.infrastructure.repository.category import CategoryRepository
from src.infrastructure.repository.delivery_method import DeliveryMethodRepository
from src.infrastructure.repository.order import OrderRepository
from src.infrastructure.repository.product import ProductRepository
from src.infrastructure.repository.user import UserRepository
from src.infrastructure.services.cart import CartService
from src.infrastructure.services.category import CategoryService
from src.infrastructure.services.delivery_method import DeliveryMethodService
from src.infrastructure.services.order import OrderService
from src.infrastructure.services.product import ProductService
from src.infrastructure.services.user import UserService


class RepositoryProvider(Provider):

    scope = Scope.REQUEST

    cart_repo = provide(CartRepository, provides=CartRepositoryPort)
    category_repo = provide(CategoryRepository, provides=CategoryRepositoryPort)
    delivery_repo = provide(DeliveryMethodRepository, provides=DeliveryMethodRepositoryPort)
    order_repo = provide(OrderRepository, provides=OrderRepositoryPort)
    product_repo = provide(ProductRepository, provides=ProductRepositoryPort)
    user_repo = provide(UserRepository, provides=UserRepositoryPort)


class ServiceProvider(Provider):

    scope = Scope.REQUEST

    cart_service = provide(CartService, provides=CartServicePort)
    category_service = provide(CategoryService, provides=CategoryServicePort)
    delivery_service = provide(DeliveryMethodService, provides=DeliveryMethodServicePort)
    order_service = provide(OrderService, provides=OrderServicePort)
    product_service = provide(ProductService, provides=ProductServicePort)
    user_service = provide(UserService, provides=UserServicePort)


class UseCaseProvider(Provider):

    scope = Scope.REQUEST

    create_order_use_case = provide(CreateOrderUseCase)
    update_order_status_use_case = provide(UpdateOrderStatusUseCase)
    get_or_create_user = provide(GetOrCreateUserUseCase)
