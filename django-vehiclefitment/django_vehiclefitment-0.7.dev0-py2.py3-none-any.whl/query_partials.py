def queryset_fits_vehicle(queryset, product_fitment_table_name, product_table_name, start_year, end_year, make, model, engine=None):
    """
    Below filters use rawsql because built in django exists filter is quite slow as it adds unnecessary group bys
    The performance on the filter goes from 100+ seconds to under 1 second
    Culprit was entire SQL turns into a subquery with odd group bys
    """
    years_conditions = list()
    engine_condition_sql, engine_condition_join = '', ''
    if end_year != "up":
        for year in range(start_year, end_year + 1):
            years_conditions.append(f"({year} BETWEEN {product_fitment_table_name}.start_year and {product_fitment_table_name}.end_year)")
    else:
        years_conditions.append(f"({product_fitment_table_name}.start_year >= {start_year})")
    years_condition_sql = " OR ".join(years_conditions)
    if engine:
        engine_condition_join = "INNER JOIN django_vehiclefitment_vehicleengine ON django_vehiclefitment_vehicle.engine_id = django_vehiclefitment_vehicleengine.id"
        engine_condition_sql = f"AND django_vehiclefitment_vehicleengine.configuration = '{engine}'"
    queryset = queryset.extra(where=[f"""
        EXISTS (
            SELECT 1 FROM {product_fitment_table_name} 
            INNER JOIN django_vehiclefitment_vehicle ON django_vehiclefitment_vehicle.id = {product_fitment_table_name}.vehicle_id
            INNER JOIN django_vehiclefitment_vehiclemake ON django_vehiclefitment_vehiclemake.id = django_vehiclefitment_vehicle.make_id
            INNER JOIN django_vehiclefitment_vehiclemodel ON django_vehiclefitment_vehiclemodel.id = django_vehiclefitment_vehicle.model_id
            {engine_condition_join}
            WHERE {product_fitment_table_name}.product_id = {product_table_name}.id
            AND django_vehiclefitment_vehiclemake.name = '{make}'
            AND django_vehiclefitment_vehiclemodel.name = '{model}'
            AND ({years_condition_sql})
            {engine_condition_sql}
        )
    """])
    return queryset