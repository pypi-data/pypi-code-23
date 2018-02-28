from django.db import models


class Base(models.Model):
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_on = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ('created_on',)


class VehicleMake(Base):
    name = models.CharField(max_length=100, db_index=True, unique=True)


class VehicleModel(Base):
    name = models.CharField(max_length=100, db_index=True)
    make = models.ForeignKey(VehicleMake, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("name", "make",)


class VehicleSubModel(Base):
    name = models.CharField(max_length=100, db_index=True)
    model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("name", "model",)


class FuelType(Base):
    name = models.CharField(max_length=20)


class FuelDelivery(Base):
    name = models.CharField(max_length=10)


class EngineAspiration(Base):
    name = models.CharField(max_length=12)


class VehicleEngine(Base):
    configuration = models.CharField(max_length=3, db_index=True)
    liters = models.DecimalField(max_digits=3, decimal_places=1, null=True, db_index=True)
    engine_code = models.CharField(max_length=100, db_index=True, null=True)
    aspiration = models.ForeignKey(EngineAspiration, on_delete=models.PROTECT, related_name="engines")
    fuel_type = models.ForeignKey(FuelType, on_delete=models.PROTECT, related_name="engines")
    fuel_delivery = models.ForeignKey(FuelDelivery, on_delete=models.PROTECT, related_name="engines")

    class Meta:
        unique_together = ("configuration", "liters", "fuel_type", "fuel_delivery", "aspiration", "engine_code",)


class Vehicle(Base):
    make = models.ForeignKey(VehicleMake, on_delete=models.CASCADE)
    model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE)
    sub_model = models.ForeignKey(VehicleSubModel, on_delete=models.CASCADE, null=True)
    engine = models.ForeignKey(VehicleEngine, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ("make", "model", "sub_model", "engine",)


class VehicleYear(Base):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    year = models.PositiveIntegerField(db_index=True)

    class Meta:
        unique_together = ("vehicle", "year",)


"""
Years are denormalized now to save space
Original design was to put 1 year per row for each table, but this took up too much space for little gain
Now the data is denormalized and each table stores a range of years instead
This still allows the ability to easily determine if a part fits a given car or not and there isn't much downside to doing it this way
"""


class ProductFitmentBase(Base):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    start_year = models.PositiveSmallIntegerField(db_index=True)
    end_year = models.PositiveSmallIntegerField(db_index=True)
    fitment_info_1 = models.CharField(max_length=1000, null=True)
    fitment_info_2 = models.CharField(max_length=1000, null=True)

    class Meta:
        abstract = True
        unique_together = ("product", "vehicle", "start_year", "end_year", "fitment_info_1", "fitment_info_2",)
