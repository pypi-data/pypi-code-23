from ftw.upgrade import UpgradeStep


class RemoveICSExportDocumentAction(UpgradeStep):
    """Remove ics export document action.
    """

    def __call__(self):
        self.install_upgrade_profile()
