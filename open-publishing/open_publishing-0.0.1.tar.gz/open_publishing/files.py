from .core.enums import FileType, EBookFileType, PreviewFileType, ContentType, PreviewDisplayMode


class FilesBase(object):
    def __init__(self,
                 document):
        self._document = document

    def _upload(self,
                file_name,
                file_type):

        self._document.context.gjp.upload_asset( self._document.document_id, file_name, file_type)


class Files(FilesBase):
    def __init__(self,
                 document):
        super(Files, self).__init__(document)
        self._cover = SimpleFile(self._document, FileType.cover_marketing_jpg)
        self._storage = SimpleFile(self._document, FileType.other)
        self._ebook = EBookFiles(self._document)
        self._pod = PODFiles(self._document)
        self._preview = PreviewFiles(self._document)

    def upload(self,
               file_name,
               file_type):
        super(Files, self)._upload(file_name, file_type)


    @property
    def preview(self):
        return self._preview

    @property
    def cover(self):
        return self._cover

    @property
    def storage(self):
        return self._storage

    @property
    def ebook(self):
        return self._ebook

    @property
    def pod(self):
        return self._pod

class EBookFiles(FilesBase):
    def __init__(self,
                 document):
        super(EBookFiles, self).__init__(document)


    def upload_content(self,
                       file_name,
                       ebook_file_type):
        if ebook_file_type not in EBookFileType:
            raise ValueError('ebook_file_type must one of op.files.ebook_filetype, got {0}'.format(ebook_file_type))
        if ebook_file_type is EBookFileType.epub:
            super(EBookFiles, self)._upload(file_name, FileType.ebook_epub)
        elif ebook_file_type is EBookFileType.pdf:
            super(EBookFiles, self)._upload(file_name, FileType.ebook_pdf)
        elif ebook_file_type is EBookFileType.mobi:
            super(EBookFiles, self)._upload(file_name, FileType.ebook_mobi)
        else:
            raise RuntimeError("Unexpect ebook_file_type {0}".format(ebook_file_type))

    def upload_cover(self,
                     file_name):
        super(EBookFiles, self)._upload(file_name, FileType.cover_marketing_jpg)

class PODFiles(FilesBase):
    def __init__(self,
                 document):
        super(PODFiles, self).__init__(document)

    def upload_content(self,
                       file_name,
                       content_type):
        if content_type not in ContentType:
            raise ValueError('content_type must one of op.files.content_type, got {0}'.format(content_type))
        if content_type is ContentType.final:
            super(PODFiles, self)._upload(file_name, FileType.pod_pdf_final)
        elif content_type is ContentType.production:
            super(PODFiles, self)._upload(file_name, FileType.pod_pdf)
        else:
            raise RuntimeError("Unexpected content type {0}".format(content_type))

    def upload_cover(self,
                     file_name):
        super(PODFiles, self)._upload(file_name, FileType.cover_pod_pdf_final)

class SimpleFile(FilesBase):
    def __init__(self,
                 document,
                 file_type):
        super(SimpleFile, self).__init__(document)
        self._file_type = file_type

    def upload(self,
               file_name):
        super(SimpleFile, self)._upload(file_name, self._file_type)


class PreviewFiles(FilesBase):
    def __init__(self,
                 document):
        super(PreviewFiles, self).__init__(document) 

    def upload(self, file_name, preview_file_type):

        self._document.context.gjp.preview_upload( self._document.document_id, file_name, preview_file_type )


