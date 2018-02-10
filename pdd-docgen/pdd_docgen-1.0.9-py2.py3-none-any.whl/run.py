import docgen
import itertools
import json
import unittest


def run(test_dir, description, dest_path):
    suite = unittest.TestLoader().discover(test_dir)
    test_results = docgen.TestRunner().run(suite)
    routes = _process_routes(test_results)

    doc = {
        "name": description.name,
        "introduction": description.introduction,
        "routes": routes
    }

    with open(dest_path, "w") as f:
        contents = json.dump(doc, f, sort_keys=True)


def _process_routes(test_results):
    routes = {}
    for result in test_results:
        route, method, status = \
            result["route"], result["method"], result["status"]

        if route not in routes:
            routes[route] = {}

        if method not in routes[route]:
            routes[route][method] = {
                "statuses": {}
            }

        if status not in routes[route][method]["statuses"]:
            routes[route][method]["statuses"][status] = []

        if "summary" in result:
            if "summary" in routes[route][method]:
                raise Exception(
                    "The summary for %s %s is set multiple times." % (
                        method, route))

            routes[route][method]["summary"] = result["summary"]

        if "variables" in result:
            if "variables" in routes[route][method]:
                raise Exception(
                    "The summary for %s %s is set multiple times." % (
                        method, route))

            routes[route][method]["variables"] = result["variables"]

        explanation = result.get("explanation")
        error_code = result.get("error-code")
        example = result.get("example")

        if explanation or error_code or example:
            routes[route][method]["statuses"][status].append({
                "explanation": result.get("explanation"),
                "error-code": result.get("error-code"),
                "example": result.get("example")
            })

    return routes
