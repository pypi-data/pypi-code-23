from open_publishing.core.enums import PublicationType, OnixStyle, OnixType, OnixStatus
from open_publishing.document import Document
from open_publishing.content import Content

class Onix(object):
    def __init__(self,
                 ctx):
        self._ctx = ctx

    def download(self,
                 guids=None,
                 documents_ids=None,
                 publication_type=None,
                 status=OnixStatus.current,
                 onix_style=OnixStyle.default,
                 onix_type=None,
                 codelist_issue=None,
                 subject_keyword_in_separate_tag=False):
        if onix_style not in OnixStyle:
            raise ValueError('expected one of op.onix.style, got: {0}'.format(onix_style))
        if (onix_type is not None) and (onix_type not in OnixType):
            raise ValueError('expected one of op.onix.type, got: {0}'.format(onix_type))
        if publication_type not in PublicationType:
            raise ValueError('expected one of op.publication, got: {0}'.format(publication_type))
        if guids is None and documents_ids is None:
            raise TypeError('Neither guids documents_ids specified')
        elif guids is not None and documents_ids is not None:
            raise TypeError('guids or documents_ids should be specified, nor both')
        elif guids is not None:
            documents_ids = [Document.id_from_guid(guid) for guid in guids]

        data, headers =  self._ctx.gjp.request_onix(documents_ids,
                                                       publication_type,
                                                       status=status,
                                                       onix_style=onix_style,
                                                       onix_type=onix_type,
                                                       codelist_issue=codelist_issue,
                                                       subject_keyword_in_separate_tag=subject_keyword_in_separate_tag)
        return Content(data, headers)
        
    def save(self,
             filename = None,
             **kwargs):
        content = self.download(**kwargs)
        with open(filename if filename else content.filename, 'wb') as f:
            f.write(content.data)
