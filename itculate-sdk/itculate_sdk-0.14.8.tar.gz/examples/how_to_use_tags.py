aws_resources = []



# When api_key and api_secret are None,
# the SDK will try to look for a 'credentials' file in '~/.itculate/'
api_key = None
api_secret = None

server_url = "https://api.itculate.io/api/v1"


import itculate_sdk as itsdk

itsdk.init(server_url=server_url)

# aws_resource can be ELB, RDS, EC2 etc.
for aws_resource in aws_resources:
    # AWS Product by Tag Name
    product_name = aws_resource.get_tag_value("Product")
    # AWS Microservice by Tag Name
    microservice_name = aws_resource.get_tag_value("Microservice")

    # Create product Vertex if already exit return it
    product = itsdk.add_vertex(collector_id="cid",
                               name=product_name,
                               vertex_type="Product",
                               keys=product_name)

    # Create Microservice Vertex if already exit return it
    service = itsdk.add_vertex(collector_id="cid",
                               name=microservice_name,
                               vertex_type="Microservice",
                               keys=microservice_name)

    # Connect the product vertex to the microservice
    itsdk.connect(collector_id="cid", source=product, target=service, topology="topology")

    # Connect the product Microservice to the aws_resource
    itsdk.connect(collector_id="cid", source=service, target=aws_resource, topology="`topology")


