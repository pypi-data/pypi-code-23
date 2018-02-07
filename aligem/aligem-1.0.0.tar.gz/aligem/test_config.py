import json


# loading JSON data
with open("../config.json") as json_config :
    data = json.load(json_config)

print data



# writing/updating JSON data
test_out = data
test_out['grid']['user'] = 'test'

with open("../json_test_out.json","w") as json_out :
    json.dump(test_out,json_out)
