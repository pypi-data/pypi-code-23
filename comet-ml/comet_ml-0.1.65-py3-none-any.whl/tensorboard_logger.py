import sys

from comet_ml import config


def extract_from_add_summary(file_writer, summary, global_step):
    from tensorflow.core.framework import summary_pb2

    extracted_values = {}

    if isinstance(summary, bytes):
        summ = summary_pb2.Summary()
        summ.ParseFromString(summary)
        summary = summ

    for value in summary.value:
        field = value.WhichOneof('value')

        if field == 'simple_value':
            extracted_values[value.tag] = value.simple_value

    return extracted_values, global_step


def add_summary_logger(real_add_summary):
    def wrapper(*args, **kwargs):
        ret_val = real_add_summary(*args, **kwargs)
        try:
            if config.experiment and config.experiment.disabled_monkey_patching is False:
                    params, step = extract_from_add_summary(*args, **kwargs)
                    config.experiment.log_multiple_metrics(params, step=step)
        except Exception as e:
            print("Failed to extract parameters from add_summary() %s" % e)
        finally:
            return ret_val

    return wrapper


ADD_SUMMARY = [("tensorflow.python.summary.writer.writer",
                "SummaryToEventTransformer.add_summary")]


def patch(module_finder):
    # Register the fit methods
    for module, object_name in ADD_SUMMARY:
        module_finder.register(module, object_name, add_summary_logger)


if "tensorboard" in sys.modules:
    raise SyntaxError(
        "Please import comet before importing any tensorboard modules")
