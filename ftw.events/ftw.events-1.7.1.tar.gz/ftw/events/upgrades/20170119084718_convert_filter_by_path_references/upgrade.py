from ftw.upgrade import UpgradeStep


class ConvertFilterByPathReferences(UpgradeStep):
    """Convert "filter_by_path" references.
    """

    def __call__(self):
        objs = self.objects(
            {'portal_type': 'ftw.events.EventListingBlock'},
            message='Convert filter_by_path references'
        )
        for obj in objs:
            if obj.filter_by_path:
                paths = []
                for path in obj.filter_by_path:
                    if not hasattr(path, 'getPhysicalPath'):
                        # Has already been converted.
                        paths.append(path)
                    else:
                        paths.append(
                            u'/'.join(path.getPhysicalPath())
                        )
                obj.filter_by_path = paths
