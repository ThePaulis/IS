import graphene
from graphene_django.types import DjangoObjectType

from .models import Warehouse, Payment, ClientType, ProductLine, Sales


class WarehouseType(DjangoObjectType):
    class Meta:
        model = Warehouse
        fields = "__all__"


class PaymentType(DjangoObjectType):
    class Meta:
        model = Payment
        fields = "__all__"


class ClientTypeType(DjangoObjectType):
    class Meta:
        model = ClientType
        fields = "__all__"


class ProductLineType(DjangoObjectType):
    class Meta:
        model = ProductLine
        fields = "__all__"


class SalesType(DjangoObjectType):
    class Meta:
        model = Sales
        fields = "__all__"


class Query(graphene.ObjectType):
    all_warehouses = graphene.List(WarehouseType)
    all_payments = graphene.List(PaymentType)
    all_client_types = graphene.List(ClientTypeType)
    all_product_lines = graphene.List(ProductLineType)
    all_sales = graphene.List(SalesType)

    def resolve_all_warehouses(self, info):
        return Warehouse.objects.all()
    
    def resolve_all_payments(self, info):
        return Payment.objects.all()
    
    def resolve_all_client_types(self, info):
        return ClientType.objects.all()
    
    def resolve_all_product_lines(self, info):
        return ProductLine.objects.all()
    
    def resolve_all_sales(self, info):
        return Sales.objects.all()
    

schema = graphene.Schema(query=Query)