from aospy.swagger.indexer import Indexer

class Templates(Indexer):
    def __init__(self, aos):
        rqst = aos.request.design.get_api_design_templates
        super(Templates, self).__init__(rqst, name_from='display_name')
        self.run()
