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


class UpdateWarehouse(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        latitude = graphene.String(required=True)  # Change from Float to String
        longitude = graphene.String(required=True)  # Change from Float to String

    warehouse = graphene.Field(WarehouseType)

    def mutate(self, info, id, latitude, longitude):
        try:
            warehouse = Warehouse.objects.get(id=id)
            # Convert strings to Decimal
            from decimal import Decimal
            warehouse.latitude = Decimal(latitude)
            warehouse.longitude = Decimal(longitude)
            warehouse.save()
            return UpdateWarehouse(warehouse=warehouse)
        except Warehouse.DoesNotExist:
            raise Exception(f'Warehouse with ID {id} does not exist')
        
class Mutation(graphene.ObjectType):
    update_warehouse = UpdateWarehouse.Field()


class Query(graphene.ObjectType):
    all_warehouses = graphene.List(WarehouseType, name=graphene.String())
    all_payments = graphene.List(PaymentType)
    all_client_types = graphene.List(ClientTypeType)
    all_product_lines = graphene.List(ProductLineType)
    all_sales = graphene.List(SalesType)

    def resolve_all_warehouses(self, info, name=None):
        if name:
            return Warehouse.objects.filter(name__icontains=name)
        return Warehouse.objects.all()
    
    def resolve_all_payments(self, info):
        return Payment.objects.all()
    
    def resolve_all_client_types(self, info):
        return ClientType.objects.all()
    
    def resolve_all_product_lines(self, info):
        return ProductLine.objects.all()
    
    def resolve_all_sales(self, info):
        return Sales.objects.all()
    

schema = graphene.Schema(query=Query, mutation=Mutation)