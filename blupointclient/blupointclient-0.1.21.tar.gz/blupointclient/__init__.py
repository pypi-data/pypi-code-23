class module_base():
    def __get_api_token(self):
        return self.cache_manager.cache('api_token')

    def __get_settings(self):
        return self.settings

class cms(module_base):

    BASE_API = None
    DOMAIN_ID = None

    def __init__(self, settings):
        from blupointclient.cms.content import BlupointCmsContent
        from blupointclient.cms.contents import BlupointCmsContents
        from blupointclient.cms.subject import BlupointCmsSubject
        from blupointclient.cms.subjects import BlupointCmsSubjects
        from blupointclient.cms.search import BlupointCmsSearch

        self.content =  BlupointCmsContent(settings)
        self.contents = BlupointCmsContents(settings)
        self.subject = BlupointCmsSubject(settings)
        self.subjects = BlupointCmsSubjects(settings)
        self.search = BlupointCmsSearch(settings)


        """
            TODO :
            interaction_module
            interactions_module
            notification_module
            notifications_module
            user_module
            users_module
            user_form_module
            user_forms_module

        """



