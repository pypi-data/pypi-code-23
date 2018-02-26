import ibmcloudsql
my_bluemix_apikey = 'YNiXREBMTfQsSzKrXYhQJElNXnUFEgpQ7qVVTkDK3_Zr'
my_instance_crn='crn%3Av1%3Abluemix%3Apublic%3Asql-query%3Aus-south%3Aa%2Fd86af7367f70fba4f306d3c19c938f2f%3Ad1b2c005-e3d8-48c0-9247-e9726a7ed510%3A%3A'
my_target_cos_endpoint='s3.us-south.objectstorage.softlayer.net'
my_target_cos_bucket='sqltempregional'
sqlClient = ibmcloudsql.SQLQuery(my_bluemix_apikey, my_instance_crn, my_target_cos_endpoint, my_target_cos_bucket, client_info='ibmcloudsql test')
result_df = sqlClient.run_sql(
"WITH orders_shipped AS \
  (SELECT OrderID, EmployeeID, (CASE WHEN shippedDate < requiredDate \
                                   THEN 'On Time' \
                                   ELSE 'Late' \
                                END) AS Shipped \
   FROM cos://us-geo/sql/orders.parquet STORED AS PARQUET) \
SELECT e.FirstName, e.LastName, COUNT(o.OrderID) As NumOrders, Shipped \
FROM orders_shipped o, \
     cos://us-geo/sql/employees.parquet STORED AS PARQUET e \
WHERE e.EmployeeID = o.EmployeeID \
GROUP BY e.FirstName, e.LastName, Shipped \
ORDER BY e.LastName, e.FirstName, NumOrders DESC")
result_df.head(200)
sqlClient.sql_ui_link()
sqlClient.get_jobs().head(200)
