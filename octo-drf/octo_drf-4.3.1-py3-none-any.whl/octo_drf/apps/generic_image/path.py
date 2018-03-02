import os
import uuid


def image_upload_path(field, instance, filename):

    app = instance._meta.app_label
    model = instance._meta.model_name
    ext = filename.split('.')[-1]
    path = 'images/{}/{}/{}'.format(
        app, model, field
    )
    filename = '{}.{}'.format(uuid.uuid4(), ext)
    return os.path.join(path, filename.lower())
