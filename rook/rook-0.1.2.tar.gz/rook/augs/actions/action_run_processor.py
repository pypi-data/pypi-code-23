
from rook.lib.processor.namespaces.container_namespace import ContainerNamespace
from rook.lib.processor.namespaces.python_utils_namespace import PythonUtilsNamespace
from rook.lib.processor.namespaces.frame_namespace import FrameNamespace
from rook.lib.processor.namespaces.stack_namespace import StackNamespace


class ActionRunProcessor(object):

    NAME = 'script'

    def __init__(self, configuration, processor_factory):
        self.processor = processor_factory.get_processor(configuration['operations'])

        if 'post_operations' in configuration:
            self.post_processor = processor_factory.get_processor(configuration['post_operations'])
        else:
            self.post_processor = None

    def execute(self, aug_id, frame, extracted_namespace, output):
        if not extracted_namespace:
            extracted_namespace = ContainerNamespace({})

        store = ContainerNamespace({})

        namespace = ContainerNamespace({
            'frame': FrameNamespace(frame),
            'stack': StackNamespace(frame),
            'extracted': extracted_namespace,
            'store': store,
            'temp': ContainerNamespace({}),
            'python': PythonUtilsNamespace(),
            'utils': PythonUtilsNamespace()
        })

        self.processor.process(namespace)
        output.send_user_message(aug_id, store)

        if self.post_processor:
            output.flush_messages()
            self.post_processor.process(namespace)
