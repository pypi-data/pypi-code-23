from SQSEngine import SQSEngine
import time

def integration_test():
    '''Test all functionality:
        Create a DS
        Attach it to a project
        Send it a metric
        Read the metric from the queue
        Detach from SNS topics and delete queue'''
    engine = SQSEngine()

    datasource = {
            "slug": "test-ds-slug",
            "name": "test-ds-name"
            }
    project = {
            "slug": "test-project-slug"
            }

    # Create the DS:
    topic_arn = engine.create_datasource(datasource)
    datasource['topic_arn'] = topic_arn

    print("Datasource created.")

    # Attach to project:
    queue_url, queue_arn, _ = engine.attach(project, datasource)

    print("Project attached.")

    # Send a metric:
    engine.send_metric(datasource['slug'], [project['slug']], "METRIC")

    print("Metric sent.")

    # Sleep, then get a metric:
    time.sleep(5)
    metro_subscription = {
            "queue_url": queue_url,
            "queue_arn": queue_arn,
            "topic_arn": topic_arn
            }
    metrics = engine.get_metrics(metro_subscription, 1)

    if(metrics == ['METRIC']):
        print("Metric received.")
    else:
        print("Incorrect metric received:")
        print(metrics)

    # Finally, detach everything:
    engine.detach(metro_subscription)

    print("Subscription removed.")

def test_get_metrics():
    '''Writes 11 metrics to a queue and pulls them all back.'''
    engine = SQSEngine()

    datasource = {
            "slug": "test-ds-letters",
            "name": "test-ds-name"
            }
    project = {
            "slug": "test-project-letters-slug"
            }

    # Create the DS:
    topic_arn = engine.create_datasource(datasource)
    datasource['topic_arn'] = topic_arn

    print("Datasource created.")

    # Attach to project:
    queue_url, queue_arn, _ = engine.attach(project, datasource)

    print("Project attached.")

    # Send a metric:
    for i in range(11):
        engine.send_metric(datasource['slug'], [project['slug']], str(i))

    print("Metrics sent.")

    # Sleep, then get a metric:
    time.sleep(5)
    metro_subscription = {
            "queue_url": queue_url,
            "queue_arn": queue_arn,
            "topic_arn": topic_arn
            }
    metrics = engine.get_metrics(metro_subscription)

    print("{} metrics received:".format(len(metrics)))
    print(metrics)

    # Finally, detach everything:
    time.sleep(5)
    engine.detach(metro_subscription)

    print("Subscription removed.")


#integration_test()
#print("---------------")
test_get_metrics()
