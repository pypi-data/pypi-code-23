from ftw.upgrade import UpgradeStep


class UseFtwKeywordwidgetOnTheEventListingBlock(UpgradeStep):
    """Use ftw.keywordwidget on the event listing block.
    """

    def __call__(self):
        self.setup_install_profile('profile-ftw.keywordwidget:default')
        self.install_upgrade_profile()
