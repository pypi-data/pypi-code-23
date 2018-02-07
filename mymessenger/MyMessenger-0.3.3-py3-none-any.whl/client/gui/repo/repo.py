from .models import ClientInfo, Image


class Repo:
    """Client's repository."""

    def __init__(self, session):
        self.session = session

    def add(self, key, value):
        """Add record."""
        new_item = ClientInfo(key, value)
        self.session.add(new_item)
        self.session.commit()

    def get(self, key):
        """Get value by key."""
        clientInfo = self.session.query(ClientInfo).filter(ClientInfo.Key == key).first()
        return clientInfo.Value

    def add_image(self, bytes):
        """Add bytes of image in repo."""

        # Temporary
        image = self.session.query(Image).first()
        if image:
            self.session.delete(image)
        # ^^^^^^^^^^^^^

        image = Image(Data=bytes)
        self.session.add(image)
        self.session.commit()

    def del_image(self, image):
        """Delete image."""
        self.session.delete(image)
        self.session.commit()

    def get_image(self):
        """Get bytes of image from repo."""
        image = self.session.query(Image).first()
        if image:
            return image.Data
        else:
            return None

    def show_all(self):
        """Show all records."""
        for c in self.session.query(ClientInfo).all():
            print('{}: {}'.format(c.Key, c.Value))
