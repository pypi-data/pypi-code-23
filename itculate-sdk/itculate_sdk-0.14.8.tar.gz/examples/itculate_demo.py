import itculate_sdk as itsdk

server_url = "https://api.itculate.io/api/v1"
# server_url = "http://localhost:5000/api/v1"

itsdk.init(server_url=server_url)

# i-057f314180ab482dc
itsdk.vertex_unhealthy(
    vertex="i-07aca3d377c864d2a",
    message="Failed to process Tenant cloudoscope, Cassandra timeout")
itsdk.flush_all()


itsdk.vertex_healthy(
    collector_id="sdk",
    vertex="i-07aca3d377c864d2a",
    message="All is ok")
itsdk.flush_all()