msg = {}
for result in consul_response.get("Results", []):
    full_key = result["KV"]["Key"] #  "<scn>:policies/event"
    value = base64.b64decode(result["Value"]).decode("utf-8")
    try:
        if value:
            value = json.loads(value)
    except (ValueError, TypeError) as err:
        pass

    if ":" in full_key:
        field_names = full_key.split(":", 1)[1].split("/") # ["policies", "event"]
        if field_names:
            parent = msg
            for field_name in field_names[: -1]:
                if field_name not in parent:
                    parent[field_name] = {}
                parent = parent[field_name]

            parent[field_names[-1:][0]] = value

if "policies" in msg and "items" in msg["policies"]:
    msg["policies"]["items"] = msg["policies"]["items"].values()
