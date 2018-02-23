import itculate_sdk as itsdk

itsdk.init(role="cloudoscope")


#############################
# create topology
#############################

collector_id = "hello_world"

hello_vertex = itsdk.add_vertex(name="Hello",
                                vertex_type="type",
                                keys="hello-key",
                                collector_id=collector_id,
                                data={
                                    "estimated-cost": 3500
                                })

world_vertex = itsdk.add_vertex(name="World",
                                vertex_type="type",
                                keys="hello-key",
                                collector_id=collector_id,
                                data={
                                    "estimated-cost": 3500
                                })

itsdk.connect(source=hello_vertex, target="", topology="topology", collector_id=collector_id)


#############################
# publish health event
#############################


itsdk.vertex_unhealthy(vertex=world_vertex, message="Global Warming", collector_id=collector_id)


#############################
# publish metric
#############################


itsdk.add_sample(vertex=world_vertex, counter="latency", value=itsdk.LatencyDataType.value(1000))


itsdk.flush_all()
