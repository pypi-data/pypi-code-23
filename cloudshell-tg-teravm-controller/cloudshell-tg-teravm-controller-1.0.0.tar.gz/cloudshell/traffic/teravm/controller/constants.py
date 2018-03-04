CLI_CONNECTION_TYPE = "SSH"
CLI_TCP_PORT = 22
SESSIONS_CONCURRENCY_LIMIT = 1

TEST_GROUP_NAME = "CS_TEST_GROUP"
TEST_GROUP_FILE = "/home/cli/cs_test_group_{}.xml"  # todo: remove "cli" from path, it may differ
TEST_RESULTS_FILE = "/home/cli/cs_test_result_{}.zip"
TEST_AGENT_NUMBER = "1"  # todo: clarify hardcode it or add another resource

CS_TEST_RESULTS_ATTACHMENTS_FILE = "Test Group Results.zip"

CHASSIS_MODEL_1G = "TeraVM Chassis"
CHASSIS_MODEL_2G = "Traffic TeraVM 2G"
CHASSIS_MODELS = [CHASSIS_MODEL_1G, CHASSIS_MODEL_2G]

PORT_MODEL_1G = "TeraVM Virtual Traffic Generator Port"
PORT_MODEL_2G = "Traffic TeraVM 2G.GenericTrafficGeneratorPort"
PORT_MODELS = [PORT_MODEL_1G, PORT_MODEL_2G]

PORT_LOGICAL_NAME_ATTR_1G = "Logical Name"
PORT_LOGICAL_NAME_ATTR_2G = "CS_TrafficGeneratorPort.Logical Name"
