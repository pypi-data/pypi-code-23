import libcloud


class BaseCloudIntegration(object):
    """Base class for all inheriting SwMain integrations"""

    provider = None
    driver_type = None

    def __init__(self, context):
        if self.provider is None:
            raise NotImplementedError(
                'Must set {}.provider attribute to target libcloud Provider.<type> constant.'.format(
                    self.__class__.__name__
                )
            )
        if self.driver_type is None:
            raise NotImplementedError(
                'Must set {}.driver_type attribute to target libcloud.DriverType.<type> constant'.format(
                    self.__class__.__name__
                )
            )

        self.asset = context.asset
        self.inputs = context.inputs

        self.driver = self.build_driver()

    def build_driver(self):
        """Instantiate a driver_type instance using the target provider and asset details"""
        cls = libcloud.get_driver(self.driver_type, self.provider)
        return cls(**self.asset)

    def execute(self):
        raise NotImplementedError('Must define {}.execute() method'.format(self.__class__.__name__))
