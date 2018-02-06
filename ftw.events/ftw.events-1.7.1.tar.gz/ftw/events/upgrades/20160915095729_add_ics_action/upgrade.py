from ftw.upgrade import UpgradeStep


class AddIcsAction(UpgradeStep):
    """Add ics action.
    """

    def __call__(self):
        self.install_upgrade_profile()
