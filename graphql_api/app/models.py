from django.db import models

class Warehouse(models.Model):
    name = models.CharField(max_length=100, unique=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'warehouse'


class Payment(models.Model):
    method = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.method

    class Meta:
        db_table = 'payment'


class ClientType(models.Model):
    type = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.type

    class Meta:
        db_table = 'client_type'


class ProductLine(models.Model):
    line = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.line

    class Meta:
        db_table = 'product_line'


class Sales(models.Model):
    date = models.DateField()
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    client_type = models.ForeignKey(ClientType, on_delete=models.CASCADE)
    product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)

    def __str__(self):
        return f"Sale on {self.date} - {self.total}"

    class Meta:
        db_table = 'sales'