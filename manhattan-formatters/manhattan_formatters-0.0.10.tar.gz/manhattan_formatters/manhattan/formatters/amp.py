from bs4 import BeautifulSoup

__all__ = [
    'amped'
]


def amped(html, snippet=None):
    """Convert a HTML string to an AMP HTML string"""

    # Parse the HTML string
    soup = BeautifulSoup(html, 'html.parser')

    # Build a map of images (assets) stored against the snippet
    assets_map = {}
    if snippet:
        if snippet.scope == 'local':
            assets_map = {a[0]: a[1]
                    for a in snippet.local_contents.get('__assets__', [])}
        else:
            contents = snippet.global_snippet.contents
            assets_map = {
                    a[0]: a[1] for a in contents.get('__assets__', [])}

    # Ensure images have width and height attributes
    for tag in soup.select('[data-mh-asset-key]'):
        asset = assets_map.get(tag['data-mh-asset-key'])
        if asset:
            variations = asset.get('variations')
            image_size = variations['image']['core_meta']['image']['size']
            image = tag.find('img')
            if image:
                image['width'] = image_size[0]
                image['height'] = image_size[1]

    # Remove image fixtures
    for tag in soup.select('[data-ce-tag="img-fixture"]'):
        image = tag.find('img')
        if image:
            tag.previous_element.insert_after(image)
            tag.extract()

    # Convert images to amp images
    for tag in soup.select('img'):
        if not tag.get('src'):
            tag.extract()
        tag.name = 'amp-img'
        tag['layout'] = 'responsive'

    # Ensure images within amp-iframes are set as placeholders
    for tag in soup.select('amp-iframe'):
        image = tag.find('amp-img')
        if image:
            image['layout'] = 'fill'
            image['placeholder'] = True
            del image['width']
            del image['height']

    # Remove any inline styles
    for tag in soup.select('style'):
        tag.extract()

    for tag in soup.select('[style]'):
        del tag['style']

    return soup.prettify()
