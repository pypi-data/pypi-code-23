import logging
from django.db import transaction
from django.db.models import Q
from django_datatools.data_retriever import DataRetriever

from .models import VehicleMake, VehicleModel, VehicleSubModel, VehicleEngine, Vehicle, VehicleYear, FuelType, FuelDelivery, EngineAspiration

logger = logging.getLogger("FitmentDataStorage")


class FitmentDataStorage(object):
    def __init__(self, brand_record, product_model_class, fitment_model_class, brand_relation):
        self.fuel_type_lookup = dict()
        self.fuel_delivery_lookup = dict()
        self.aspiration_lookup = dict()
        self.brand_record = brand_record
        self.product_model_class = product_model_class
        self.fitment_model_class = fitment_model_class
        self.brand_relation = brand_relation

    @transaction.atomic
    def clean_and_store_data(self, fitment_lookup):
        fitment_lookup = self._clean_fitment_data(fitment_lookup)
        if len(fitment_lookup):
            logger.info('Storing fitment for parts {}'.format(",".join(list(fitment_lookup.keys()))))
            self._store_data(fitment_lookup)

    def _store_data(self, fitment_lookup):
        storage_objects = self._generate_storage_objects(fitment_lookup)
        make_records = self._get_make_records(storage_objects['make_storage'])
        model_records = self._get_model_records(storage_objects['model_storage'], make_records)
        sub_model_records = self._get_sub_model_records(storage_objects['sub_model_storage'], model_records)
        engine_records = self._get_engine_records(storage_objects['engine_storage'])
        vehicle_records = self._get_vehicle_records(storage_objects['vehicle_storage'], make_records, model_records, sub_model_records, engine_records)
        make_records.clear()
        model_records.clear()
        if sub_model_records:
            sub_model_records.clear()

        if engine_records:
            engine_records.clear()

        self._store_fitment(fitment_lookup, vehicle_records)

    def _generate_storage_objects(self, fitment_lookup):
        make_storage = {
            'storage_objects': dict(),
            'makes': set()
        }
        model_storage = {
            'storage_objects': dict(),
            'models': set()
        }
        sub_model_storage = {
            'storage_objects': dict(),
            'sub_models': set()
        }
        engine_storage = {
            'storage_objects': dict(),
            'configurations': set(),
            'engine_codes': set()
        }
        vehicle_storage = {
            'storage_objects': dict()
        }
        for part_fitment_data in fitment_lookup.values():
            for fitment_row in part_fitment_data.values():
                make = self._generate_make_storage_object(make_storage, fitment_row)
                model = self._generate_model_storage_object(model_storage, make, fitment_row)
                sub_model = self._generate_sub_model_storage_object(sub_model_storage, make, model, fitment_row)
                engine_key = self._generate_engine_storage_object(engine_storage, fitment_row)
                self._generate_vehicle_storage_object(vehicle_storage, make, model, sub_model, engine_key, fitment_row)
        return {
            "make_storage": make_storage,
            "model_storage": model_storage,
            "sub_model_storage": sub_model_storage,
            "engine_storage": engine_storage,
            "vehicle_storage": vehicle_storage
        }

    def _generate_make_storage_object(self, make_storage, fitment_row):
        make = fitment_row['make']
        make_storage['makes'].add(make)
        if make not in make_storage['storage_objects']:
            make_storage['storage_objects'][make] = {'name': make}
        return make

    def _generate_model_storage_object(self, model_storage, make, fitment_row):
        model = fitment_row['model']
        model_storage['models'].add(model)
        model_key = make + model
        if model_key not in model_storage['storage_objects']:
            model_storage['storage_objects'][model_key] = {
                'name': model,
                'make': make
            }
        return model

    def _generate_sub_model_storage_object(self, sub_model_storage, make, model, fitment_row):
        model_key = make + model
        sub_model = fitment_row['sub_model']
        if sub_model:
            sub_model_storage['sub_models'].add(sub_model)
            sub_model_key = make + model + sub_model
            if sub_model_key not in sub_model_storage['storage_objects']:
                sub_model_storage['storage_objects'][sub_model_key] = {
                    'name': sub_model,
                    'model': model_key
                }
        return sub_model

    def _generate_engine_storage_object(self, engine_storage, fitment_row):
        engine_data = fitment_row['engine']
        engine_key = None
        if engine_data:
            engine_configuration = engine_data['configuration']
            if engine_configuration:
                engine_liters = engine_data.get("liters", None)
                engine_code = engine_data.get('engine_code', None)
                aspiration = engine_data['aspiration']
                fuel_type = engine_data['fuel_type']
                fuel_delivery = engine_data['fuel_delivery']
                engine_key = engine_configuration + str(engine_liters or '') + fuel_type + fuel_delivery + (engine_code or '') + aspiration

                engine_storage['configurations'].add(engine_configuration)
                if engine_code:
                    engine_storage['engine_codes'].add(engine_code)
                if engine_key not in engine_storage['storage_objects']:
                    engine_storage['storage_objects'][engine_key] = {
                        'configuration': engine_configuration,
                        'liters': engine_liters,
                        'engine_code': engine_code,
                        'fuel_type': fuel_type,
                        'fuel_delivery': fuel_delivery,
                        'aspiration': aspiration
                    }
        return engine_key

    def _generate_vehicle_storage_object(self, vehicle_storage, make, model, sub_model, engine_key, fitment_row):
        vehicle_key = make + model + (sub_model or '') + (engine_key or '')
        sub_model_key = make + model + sub_model if sub_model else None

        if vehicle_key not in vehicle_storage['storage_objects']:
            vehicle_storage['storage_objects'][vehicle_key] = {
                'make': make,
                'model': make + model,
                'sub_model': sub_model_key,
                'engine': engine_key,
                'years': set()
            }
        for year in range(fitment_row['start_year'], fitment_row['end_year'] + 1):
            vehicle_storage['storage_objects'][vehicle_key]['years'].add(year)
        return vehicle_key

    def _clean_fitment_data(self, fitment_lookup):
        """
        This method cleans the fitment data.
        1. If the fitment_data input is the same as database, do not store
        2. If the fitment_data and database differ, delete existing records from the database and re-insert new records
        3. If the fitment_data is storing a part that does not exist, remove it

        """
        existing_fitment_lookup = dict()
        product_fitment_to_delete = list()
        existing_product_lookup = self.product_model_class.objects.filter(**{self.brand_relation: self.brand_record, "part_number__in": fitment_lookup.keys()}).values_list("part_number", flat=True)
        fitment_lookup = {key: value for key, value in fitment_lookup.items() if key in existing_product_lookup}
        existing_fitment_records = self.fitment_model_class.objects.filter(**{f"product__{self.brand_relation}": self.brand_record, "product__part_number__in": fitment_lookup.keys()})
        existing_fitment_records = existing_fitment_records.select_related("product", "vehicle", "vehicle__make", "vehicle__model", "vehicle__sub_model", "vehicle__engine", "vehicle__engine__fuel_delivery", "vehicle__engine__fuel_type", "vehicle__engine__aspiration")
        vehicle_key_parts = [
            "vehicle__make__name", "vehicle__model__name", "vehicle__sub_model__name", "vehicle__engine__configuration", "vehicle__engine__liters", "vehicle__engine__fuel_type__name", "vehicle__engine__fuel_delivery__name", "vehicle__engine__engine_code", "vehicle__engine__aspiration__name"
        ]
        vehicle_fitment_key_parts = ["start_year", "end_year"] + vehicle_key_parts + ["fitment_info_1", "fitment_info_2"]
        existing_fitment_records = existing_fitment_records.values(*(["id", "product__part_number"] + vehicle_fitment_key_parts))
        for existing_fitment_record in existing_fitment_records:
            vehicle_fitment_key = DataRetriever.get_record_key(existing_fitment_record, vehicle_fitment_key_parts)
            vehicle_key = DataRetriever.get_record_key(existing_fitment_record, vehicle_key_parts)
            part_number = existing_fitment_record['product__part_number']
            if part_number not in existing_fitment_lookup:
                existing_fitment_lookup[part_number] = dict()
            existing_fitment_lookup[part_number][vehicle_fitment_key] = {
                'product': part_number,
                'vehicle': vehicle_key,
                'start_year': existing_fitment_record['start_year'],
                'end_year': existing_fitment_record['end_year'],
                'fitment_info_1': existing_fitment_record['fitment_info_1'],
                'fitment_info_2': existing_fitment_record['fitment_info_2'],
                'fitment_id': existing_fitment_record['id']
            }

        if existing_fitment_lookup:
            for part_number in list(fitment_lookup.keys()):
                if part_number in existing_fitment_lookup:
                    new_part_fitment_storage = fitment_lookup[part_number]
                    existing_part_fitment_storage = existing_fitment_lookup[part_number]
                    for existing_fitment_key, existing_fitment_data in existing_part_fitment_storage.items():
                        fitment_id = existing_fitment_data.pop('fitment_id')

                        if existing_fitment_key not in new_part_fitment_storage:
                            product_fitment_to_delete.append(fitment_id)
                            # TODO, clean up unused vehicle data
                        else:
                            del fitment_lookup[part_number][existing_fitment_key]
                            if len(fitment_lookup[part_number]) == 0:
                                del fitment_lookup[part_number]

        if product_fitment_to_delete:
            self.fitment_model_class.objects.filter(id__in=product_fitment_to_delete).delete()
        return fitment_lookup

    def _get_make_records(self, make_storage):
        make_retriever = DataRetriever(VehicleMake, VehicleMake.objects.filter(name__in=make_storage['makes']), ('name',))
        return make_retriever.bulk_get_or_create(make_storage['storage_objects'])

    def _get_model_records(self, model_storage, make_records):
        storage_objects = model_storage['storage_objects']
        for model_key, model_object in storage_objects.items():
            model_object["make_id"] = make_records[model_object.pop("make")]

        model_retriever = DataRetriever(VehicleModel, VehicleModel.objects.filter(name__in=model_storage['models'], make_id__in=make_records.values()).select_related("make"), ("make__name", "name",))
        return model_retriever.bulk_get_or_create(storage_objects)

    def _get_sub_model_records(self, sub_model_storage, model_records):
        storage_objects = sub_model_storage['storage_objects']
        if storage_objects:
            for sub_model_key, sub_model_object in storage_objects.items():
                sub_model_object['model_id'] = model_records[sub_model_object.pop('model')]
            sub_model_retriever = DataRetriever(VehicleSubModel, VehicleSubModel.objects.filter(name__in=sub_model_storage['sub_models'], model_id__in=model_records.values()).select_related("model__make"), ("model__make__name", "model__name", "name",))
            return sub_model_retriever.bulk_get_or_create(storage_objects)
        return None

    def _get_engine_records(self, engine_storage):
        storage_objects = engine_storage['storage_objects']
        if storage_objects:
            for engine_key, engine_object in storage_objects.items():
                engine_object['fuel_type'] = self._get_fuel_type(engine_object['fuel_type'])
                engine_object['fuel_delivery'] = self._get_fuel_delivery(engine_object['fuel_delivery'])
                engine_object['aspiration'] = self._get_aspiration(engine_object['aspiration'])
            engine_retriever = DataRetriever(VehicleEngine, VehicleEngine.objects.filter(configuration__in=engine_storage['configurations']).filter(Q(engine_code__isnull=True) | Q(engine_code__in=engine_storage['engine_codes'])).select_related(),
                                             ("configuration", "liters", "fuel_type__name", "fuel_delivery__name", "engine_code", "aspiration__name"))
            return engine_retriever.bulk_get_or_create(storage_objects)
        return None

    def _get_vehicle_records(self, vehicle_storage, make_records, model_records, sub_model_records, engine_records):
        storage_objects = vehicle_storage['storage_objects']
        vehicle_year_storage = dict()
        for vehicle_key, vehicle_object in storage_objects.items():
            vehicle_object['make_id'] = make_records[vehicle_object.pop('make')]
            vehicle_object['model_id'] = model_records[vehicle_object.pop('model')]
            if vehicle_object['sub_model'] and sub_model_records:
                vehicle_object['sub_model_id'] = sub_model_records[vehicle_object.pop('sub_model')]
            if vehicle_object['engine'] and engine_records:
                vehicle_object['engine_id'] = engine_records[vehicle_object.pop('engine')]
            vehicle_years = vehicle_object.pop("years")
            for vehicle_year in vehicle_years:
                vehicle_year_key = str(vehicle_year) + vehicle_key
                vehicle_year_storage[vehicle_year_key] = {
                    'vehicle': vehicle_key,
                    'year': vehicle_year
                }
        vehicle_retriever = DataRetriever(
            Vehicle,
            Vehicle.objects.filter(model_id__in=model_records.values()).select_related("make", "model", "sub_model", "engine", "engine__fuel_delivery", "engine__fuel_type", "engine__aspiration"),
            ("make__name", "model__name", "sub_model__name", "engine__configuration", "engine__liters", "engine__fuel_type__name", "engine__fuel_delivery__name", "engine__engine_code", "engine__aspiration__name")
        )
        vehicle_records = vehicle_retriever.bulk_get_or_create(storage_objects)
        for vehicle_year_object in vehicle_year_storage.values():
            vehicle_year_object['vehicle_id'] = vehicle_records[vehicle_year_object.pop('vehicle')]

        vehicle_year_retriever = DataRetriever(
            VehicleYear,
            VehicleYear.objects.filter(vehicle_id__in=vehicle_records.values()).select_related("vehicle", "vehicle__make", "vehicle__model", "vehicle__sub_model", "vehicle__engine", "vehicle__engine__fuel_delivery", "vehicle__engine__fuel_type", "vehicle__engine__aspiration"),
            (
                "year", "vehicle__make__name", "vehicle__model__name", "vehicle__sub_model__name", "vehicle__engine__configuration", "vehicle__engine__liters", "vehicle__engine__fuel_type__name", "vehicle__engine__fuel_delivery__name", "vehicle__engine__engine_code",
                "vehicle__engine__aspiration__name")
        )
        vehicle_year_retriever.bulk_get_or_create(vehicle_year_storage)
        return vehicle_records

    def _store_fitment(self, fitment_lookup, vehicle_records):
        product_retriever = DataRetriever(self.product_model_class, self.product_model_class.objects.filter(**{self.brand_relation: self.brand_record, "part_number__in": fitment_lookup.keys()}), ("part_number",))
        product_fitment_objects = list()
        for part_number, fitment in fitment_lookup.items():
            for fitment_data in fitment.values():
                engine_data = fitment_data['engine']
                engine_key = ''
                if engine_data and engine_data['configuration']:
                    engine_key = engine_data['configuration'] + str(engine_data['liters'] or '') + engine_data['fuel_type'] + engine_data['fuel_delivery'] + (engine_data['engine_code'] or '') + engine_data['aspiration']
                vehicle_key = fitment_data['make'] + fitment_data['model'] + (fitment_data['sub_model'] or '') + engine_key
                storage_object = {
                    "product_id": product_retriever.get_instance(part_number),
                    "vehicle_id": vehicle_records[vehicle_key],
                    "start_year": fitment_data['start_year'],
                    "end_year": fitment_data['end_year'],
                    "fitment_info_1": fitment_data['fitment_info_1'],
                    "fitment_info_2": fitment_data['fitment_info_2']
                }

                product_fitment_objects.append(self.fitment_model_class(**storage_object))
        if product_fitment_objects:
            self.fitment_model_class.objects.bulk_create(product_fitment_objects)

    def _get_fuel_type(self, fuel_type):
        fuel_type_record = self.fuel_type_lookup.get(fuel_type, None)
        if not fuel_type_record:
            fuel_type_record = FuelType.objects.get_or_create(name=fuel_type)[0]
            self.fuel_type_lookup[fuel_type] = fuel_type_record
        return fuel_type_record

    def _get_fuel_delivery(self, fuel_delivery):
        fuel_delivery_record = self.fuel_delivery_lookup.get(fuel_delivery, None)
        if not fuel_delivery_record:
            fuel_delivery_record = FuelDelivery.objects.get_or_create(name=fuel_delivery)[0]
            self.fuel_delivery_lookup[fuel_delivery] = fuel_delivery_record
        return fuel_delivery_record

    def _get_aspiration(self, aspiration):
        aspiration_record = self.aspiration_lookup.get(aspiration, None)
        if not aspiration_record:
            aspiration_record = EngineAspiration.objects.get_or_create(name=aspiration)[0]
            self.aspiration_lookup[aspiration] = aspiration_record
        return aspiration_record
