from ftw.upgrade import UpgradeStep


class ImplementFtwReferencewidget(UpgradeStep):
    """Implement ftw referencewidget.
    """

    def __call__(self):
        self.install_upgrade_profile()
