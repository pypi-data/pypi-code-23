from ftw.upgrade import UpgradeStep


class MakeAddableOnPloneSite(UpgradeStep):
    """Make addable on plone site.
    """

    def __call__(self):
        self.install_upgrade_profile()
