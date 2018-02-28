import ibmcloudsql
my_bluemix_apikey = 'YNiXREBMTfQsSzKrXYhQJElNXnUFEgpQ7qVVTkDK3_Zr'
my_instance_crn='crn%3Av1%3Abluemix%3Apublic%3Asql-query%3Aus-south%3Aa%2Fd86af7367f70fba4f306d3c19c938f2f%3Ad1b2c005-e3d8-48c0-9247-e9726a7ed510%3A%3A'
my_target_cos_url='cos://s3.us-south.objectstorage.softlayer.net/sqltempregional/'
sqlClient = ibmcloudsql.SQLQuery(my_bluemix_apikey, my_instance_crn, my_target_cos_url, client_info='ibmcloudsql test')

print("Running test with individual method invocation:")
sqlClient.logon()
jobId = sqlClient.submit_sql("SELECT * FROM cos://us-geo/sql/employees.parquet STORED AS PARQUET LIMIT 10")
sqlClient.wait_for_job(jobId)
result_df = sqlClient.get_result(jobId)
print("jobId {} restults are stored in {}. Result set is:".format(jobId, sqlClient.get_job(jobId)['resultset_location']))
result_df.head(200)

print("Running test with compound method invocation:")
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
print("Result set is:")
result_df.head(200)

print("SQL UI Link:")
sqlClient.sql_ui_link()

print("Job list:")
sqlClient.get_jobs().head(200)
