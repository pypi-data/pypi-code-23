import ibmcloudsql
my_bluemix_apikey = 'YNiXREBMTfQsSzKrXYhQJElNXnUFEgpQ7qVVTkDK3_Zr'
my_instance_crn='crn%3Av1%3Abluemix%3Apublic%3Asql-query%3Aus-south%3Aa%2Ff5e2ac71094077500e0d4b1ef8b9de0a%3A951a5281-951e-4dac-8159-a35c8b7c2c98%3A%3A'
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
