import shelve, base64
import requests

image_db = shelve.open('.kooki_images')


def get_image(image_path):
    image_result = ''
    try:
        image_result = image_db[str(image_path)]
    except KeyError:
        try:
            response = requests.get(image_path)
            image_file = response.content
            image_result = convert_image(image_file)
            image_db[str(image_path)] = image_result
        except requests.exceptions.MissingSchema:
            image_result = get_local_image(image_path)
    return image_result


def get_local_image(image_path):
    with open(image_path, 'rb') as image_file:
        return convert_image(image_file.read())


def convert_image(image_file):
    image_content_base64 = base64.b64encode(image_file)
    return 'data:image/png;base64,' + image_content_base64.decode('utf-8')
