import datetime

from .core import SimpleField, FieldDescriptor, DatabaseObject, DatabaseObjectField, FieldGroup

from .core.enums import DocumentStatus, FieldKind, Language, OnixStyle, OnixStatus, PreviewDisplayMode, PreviewTOCVisible, BookBinding
from .core.enums import ProcessingType
from .prices.price_group import PriceGroup
from .misc import MiscGroup
from .authors import AuthorsList
from .provision import ProvisionRulesList
from .brands import BrandsField
from .imprint import ImprintField
from .catalog.catalog_field import CatalogField
from .files import Files
from .assets import AssetsGroup
from .isbns import IsbnGroup
from .publications import PublicationsField
from .dates import DatesGroup
from .audience import AudienceGroup
from .extendable_enum_field import ExtendableEnumField
from .object_events import ObjectEvents
from .user import User
from .archive import ArchiveField
from .distribution_availability import DistributionAvailabilityField
from .distribution_channels import DistributionChannelsField
from .search_tags import SearchTagsField
from .admin_search_tags import AdminSearchTagsField

class Document(DatabaseObject):
    _object_class = "document"

    def __init__(self,
                 context,
                 document_id):
        super(Document, self).__init__(context,
                                       document_id)

        self._fields["title"] = SimpleField(database_object=self,
                                            aspect=":basic",
                                            field_locator="title",
                                            dtype=str)


        self._fields["subtitle"] = SimpleField(database_object=self,
                                            aspect=":basic",
                                            field_locator="subtitle",
                                            dtype=str)


        self._fields["status"] = SimpleField(database_object=self,
                                             aspect=":basic",
                                             field_locator="status",
                                             dtype=DocumentStatus,
                                             kind=FieldKind.readonly)

        self._fields["created"] = SimpleField(database_object=self,
                                              aspect=":basic",
                                              field_locator="created",
                                              dtype=datetime.datetime)

        self._fields["abstract"] = SimpleField(database_object=self,
                                            aspect="abstract.*",
                                            field_locator="abstract.abstract",
                                            dtype=str)

        self._fields["self_publishing"] = SimpleField(database_object=self,
                                                      aspect="internal.*",
                                                      field_locator="internal.self_publishing",
                                                      dtype=bool)

        self._fields['language'] = ExtendableEnumField(database_object=self,
                                                       aspect=":basic",
                                                       field_locator="language_id",
                                                       dtype=Language,
                                                       nullable=True)

        self._fields["_page_count_technical"] = SimpleField(database_object=self,
                                                            aspect="ebook.*",
                                                            field_locator="ebook.page_count_technical",
                                                            dtype=int,
                                                            nullable=True,
                                                            kind=FieldKind.readonly)

        self._fields["_page_count_custom"] = SimpleField(database_object=self,
                                                         aspect="ebook.*",
                                                         field_locator="ebook.page_count_custom",
                                                         dtype=int,
                                                         nullable=True)

        self._fields["urls"] = URLsGroup(document=self)


        self._fields["excerpt"] = SimpleField(database_object=self,
                                              aspect="othertext_excerpt.*",
                                              field_locator="othertext_excerpt.text",
                                              dtype=str)

        self._fields["biographical_note"] = SimpleField(database_object=self,
                                                        aspect="othertext_biographical_note.*",
                                                        field_locator="othertext_biographical_note.text",
                                                        dtype=str)

        self._fields["suppliers"] = SimpleField(database_object=self,
                                                aspect="book.suppliers_in_stock",
                                                field_locator="book.suppliers_in_stock",
                                                dtype=set)

        
        self._fields["book"] = BookGroup(document=self)
        self._fields["prices"] = PriceGroup(document=self)
        self._fields["sales_rights"] = SalesRightsGroup(document=self)
        self._fields["misc"] = MiscGroup(document=self) 
        self._fields["authors"] = AuthorsList(document=self)
        self._fields["provision_rules"] = ProvisionRulesList(document=self)
        self._fields["brands"] = BrandsField(document=self)
        self._fields["upload_brand"] = UploadBrandField(document=self)
        self._fields["imprint"] = ImprintField(document=self)
        self._fields["catalog"] = CatalogField(document=self)
        self._fields["isbns"] = IsbnGroup(document=self)
        self._fields["publications"] = PublicationsField(document=self)
        self._fields["dates"] = DatesGroup(document=self)
        self._fields["audience"] = AudienceGroup(document=self)
        self._fields["owner"] = OwnerField(document=self)
        self._fields["archive"] = ArchiveField(document=self)
        self._fields["distribution"] = DistributionGroup(document=self)
        self._fields["edition"] = EditionGroup(document=self)
        self._fields["preview"] = PreviewGroup(document=self)
        self._fields["licenses"] = LicensesGroup(document=self)
        self._fields["tags"] = SearchTagsField(document=self)
        self._fields["admin_tags"] = AdminSearchTagsField(document=self)
        self._fields["assets"] = AssetsGroup(self)
        self._fields["processing"] = ProcessingGroup(self)
        self._fields["onix"] = DocumentOnix(self)

        self._files = Files(self)
        self._events = ObjectEvents(self)

    title = FieldDescriptor("title")
    subtitle = FieldDescriptor("subtitle")
    status = FieldDescriptor("status")
    created = FieldDescriptor("created")
    abstract = FieldDescriptor("abstract")
    self_publishing = FieldDescriptor("self_publishing")
    language = FieldDescriptor("language")
    _page_count_technical = FieldDescriptor("_page_count_technical")
    _page_count_custom = FieldDescriptor("_page_count_custom")
    urls = FieldDescriptor("urls")
    excerpt = FieldDescriptor("excerpt")
    biographical_note = FieldDescriptor("biographical_note")
    suppliers = FieldDescriptor("suppliers")

    book = FieldDescriptor("book")
    prices = FieldDescriptor("prices")
    sales_rights = FieldDescriptor("sales_rights")
    misc = FieldDescriptor("misc") #For testing purposes
    authors = FieldDescriptor("authors")
    provision_rules = FieldDescriptor("provision_rules")
    brands = FieldDescriptor("brands")
    upload_brand = FieldDescriptor("upload_brand")
    imprint = FieldDescriptor("imprint")
    catalog = FieldDescriptor("catalog")
    isbns = FieldDescriptor("isbns")
    publications = FieldDescriptor("publications")
    dates = FieldDescriptor("dates")
    audience = FieldDescriptor("audience")
    owner = FieldDescriptor("owner")
    archive = FieldDescriptor("archive")
    distribution = FieldDescriptor("distribution")
    edition = FieldDescriptor("edition")
    preview = FieldDescriptor("preview")
    licenses = FieldDescriptor("licenses")
    tags = FieldDescriptor("tags")
    admin_tags = FieldDescriptor("admin_tags")
    assets = FieldDescriptor("assets")
    processing = FieldDescriptor("processing")
    onix = FieldDescriptor("onix")

    @property
    def page_count(self):
        if self._page_count_custom is not None:
            return self._page_count_custom
        return self._page_count_technical

    @page_count.setter
    def page_count(self, value):
        self._page_count_custom = value

    @property
    def files(self):
        return self._files

    @property
    def events(self):
        return self._events

    @property
    def document_id(self):
        return self._object_id


    def flush(self):
        super(Document, self).flush()

    def publish(self):
        self.flush()
        self._context.gjp.publish_document(self.document_id)
        self._fields["status"].invalidate()
        
    def unpublish(self):
        self._context.gjp.unpublish_document(self.document_id)
        self._fields["status"].invalidate()

    def approve(self):
        self._context.gjp.final_check_ok(self.document_id)
        self._fields["status"].invalidate()

    def delete(self):
        self._context.gjp.delete_document(self.document_id)
        self._fields["status"].invalidate()

    def undelete(self):
        self._context.gjp.undelete_document(self.document_id)
        self._fields["status"].invalidate()
        
    def _on_changed(self):
        self._context.documents._add_to_changed(self)
        
    def _on_flush(self):
        self._context.documents._remove_from_changed(self)


class DocumentOnix(FieldGroup):
    def __init__(self,
                 document):
        super(DocumentOnix, self).__init__(document)
        self._fields["onix_references"] = OnixReferencesGroup(document)
        self._document = document

    references = FieldDescriptor("onix_references")

    def download(self,
                 publication_type,
                status=OnixStatus.current,
                 onix_style=OnixStyle.default,
                 onix_type=None,
                 codelist_issue=None,
                 subject_keyword_in_separate_tag=False):
        return self._document.context.onix.download(documents_ids=[self._document.document_id],
                                                    publication_type=publication_type,
                                                    status=status,
                                                    onix_style=onix_style,
                                                    onix_type=onix_type,
                                                    codelist_issue=codelist_issue,
                                                    subject_keyword_in_separate_tag=subject_keyword_in_separate_tag)

    def save(self,
             publication_type,
             filename=None,
             status=OnixStatus.current,
             onix_style=OnixStyle.default,
             onix_type=None,
             codelist_issue=None,
             subject_keyword_in_separate_tag=False):
        self._document.context.onix.save(filename=filename,
                                         documents_ids=[self._document.document_id],
                                         publication_type=publication_type,
                                         status=status,
                                         onix_style=onix_style,
                                         onix_type=onix_type,
                                         codelist_issue=codelist_issue,
                                         subject_keyword_in_separate_tag=subject_keyword_in_separate_tag)

        
class OnixReferencesGroup(FieldGroup):
    def __init__(self,
                 document):
        super(OnixReferencesGroup, self).__init__(document)
        self._fields["epub"] = SimpleField(database_object=document,
                                           aspect='onix.*',
                                           dtype=str,
                                           field_locator='onix.record_references.epub',
                                           nullable=True)
        self._fields["mobi"] = SimpleField(database_object=document,
                                           aspect='onix',
                                           dtype=str,
                                           field_locator='onix.record_references.mobi',
                                           nullable=True)
        self._fields["pdf"] = SimpleField(database_object=document,
                                          aspect='onix',
                                          dtype=str,
                                          field_locator='onix.record_references.pdf',
                                          nullable=True)
        self._fields["pod"] = SimpleField(database_object=document,
                                          aspect='onix',
                                          dtype=str,
                                          field_locator='onix.record_references.pod',
                                          nullable=True)
                                          

    epub = FieldDescriptor("epub")
    mobi = FieldDescriptor("mobi")
    pdf = FieldDescriptor("pdf")
    pod = FieldDescriptor("pod")

class OwnerField(DatabaseObjectField):
    def __init__(self,
                 document):
        super(OwnerField, self).__init__(parent=document,
                                         aspect=":basic",
                                         field_locator="user_id",
                                         dtype=User,
                                         nullable=True)

class DistributionGroup(FieldGroup):
    def __init__(self,
                 document):
        super(DistributionGroup, self).__init__(document)
        self._fields["distribution_availability"] = DistributionAvailabilityField(document)
        self._fields["distribution_channels"] = DistributionChannelsField(document)
        self._fields["distribution_blocked"] = SimpleField(database_object=document,
                                                           aspect='distribution_channels.*',
                                                           dtype=bool,
                                                           field_locator='distribution_channels.blocked')
        self._document = document

    availability = FieldDescriptor("distribution_availability")
    channels = FieldDescriptor("distribution_channels")
    blocked = FieldDescriptor("distribution_blocked")

    def set_external_availability(self,
                                 name,
                                 country_code,
                                 publication_type,
                                 availability_status,
                                 availability,
                                 in_stock_quantity,
                                 price_cent,
                                 currency_code,
                                 shop_url):
        self._document.context.gjp.set_document_external_availability(name,
                                                                      country_code,
                                                                      self._document.document_id,
                                                                      publication_type,
                                                                      availability_status,
                                                                      availability,
                                                                      in_stock_quantity,
                                                                      price_cent,
                                                                      currency_code,
                                                                      shop_url)

    def set_external_salesrank(self,
                               name,
                               country_code,
                               publication_type,
                               salesrank):
        self._document.context.gjp.set_document_external_salesrank(name,
                                                                   country_code,
                                                                   self._document.document_id,
                                                                   publication_type,
                                                                   salesrank)

    def set_external_rating(self,
                            name,
                            country_code,
                            publication_type,
                            average_rating,
                            review_count,
                            shop_review_url):
        self._document.context.gjp.set_document_external_rating(name,
                                                                country_code,
                                                                self._document.document_id,
                                                                publication_type,
                                                                average_rating,
                                                                review_count,
                                                                shop_review_url)


class EditionGroup(FieldGroup):
    def __init__(self,
                 document):
        super(EditionGroup, self).__init__(document)
        self._fields["ebook"] = SimpleField(database_object=document,
                                            aspect="ebook.*",
                                            field_locator="ebook.type_of_edition",
                                            dtype=str)

        self._fields["book"] = SimpleField(database_object=document,
                                           aspect="book.*",
                                           field_locator="book.type_of_edition",
                                           dtype=str)

    ebook = FieldDescriptor("ebook")
    book = FieldDescriptor("book")

class PreviewGroup(FieldGroup):
    def __init__(self,
                 document):
        super(PreviewGroup, self).__init__(document)
        self._fields["display_mode"] = SimpleField(database_object=document,
                                                   aspect="document_preview.*",
                                                   field_locator="document_preview.display_mode",
                                                   dtype=PreviewDisplayMode,
                                                   kind=FieldKind.readonly)

        self._fields["toc_visible"] = SimpleField(database_object=document,
                                                  aspect="document_preview.*",
                                                  field_locator="document_preview.toc_visible",
                                                  dtype=PreviewTOCVisible,
                                                  kind=FieldKind.readonly)
                                                  

    _display_mode = FieldDescriptor("display_mode")
    _toc_visible = FieldDescriptor("toc_visible")

    @property
    def display_mode(self):
        return self._display_mode

    @display_mode.setter
    def display_mode(self, value):
        if value not in PreviewDisplayMode:
            raise ValueError('Expected on of op.preview.display_mode, got {0}'.format(value))
        self.database_object.context.gjp.set_display_mode(self.database_object.document_id,
                                                          value)
        self._fields["display_mode"].invalidate()

    @property
    def toc_visible(self):
        return self._toc_visible

    @toc_visible.setter
    def toc_visible(self, value):
        if value not in PreviewTOCVisible:
            raise ValueError('Expected on of op.preview.toc_visible, got {0}'.format(value))
        self.database_object.context.gjp.set_toc_visible(self.database_object.document_id,
                                                         value)
        self._fields["toc_visible"].invalidate()
        

class LicensesGroup(FieldGroup):
    def __init__(self,
                 document):
        super(LicensesGroup, self).__init__(document)
        self._document = document

    def accept(self,
               short_name,
               ip,
               option):
        self._document.flush()
        self._document.context.gjp.accept_license(self._document.document_id,
                                                  self._document.owner.user_id,
                                                  short_name,
                                                  ip,
                                                  option)



class UploadBrandField(SimpleField):
    def __init__(self,
                 document):
        super(UploadBrandField,self).__init__(database_object=document,
                                              aspect="upload_brand.*",
                                              field_locator="upload_brand",
                                              dtype=str,
                                              nullable=True)

    def _serialize_value(self,
                         value):
        if value is None and self._nullable:
            return self._serialized_null
        else:
            return {'name' : value}
    
    def _parse_value(self,
                     value):
        if value == self._serialized_null and self._nullable:
            return None
        else :
            return value['name']
        
    def _value_validation(self,
                          value):
        if value is None and self._nullable:
            return value
        elif isinstance(value, str):
            if value in self.database_object.context.brands:
                return str(value)
            else:
                raise ValueError("upload_brand should be one of ctx.brands")
        else:
            raise TypeError("expected instance of {0}, got instance of {1}".format(self._dtype,
                                                                                    type(value)))



class SalesRightsGroup(FieldGroup):
    def __init__(self,
                 document):
        super(SalesRightsGroup, self).__init__(document)
        self._fields['exclusive'] = SalesRightsField(document=document,
                                                     sales_rights_type='exclusive')

        self._fields['non_exclusive'] = SalesRightsField(document=document,
                                                         sales_rights_type='non_exclusive')

        self._fields['not_for_sale'] = SalesRightsField(document=document,
                                                        sales_rights_type='not_for_sale')

    exclusive = FieldDescriptor('exclusive')
    non_exclusive = FieldDescriptor('non_exclusive')
    not_for_sale = FieldDescriptor('not_for_sale')


class SalesRightsField(SimpleField):
    def __init__(self,
                 document,
                 sales_rights_type):
        super(SalesRightsField,self).__init__(database_object=document,
                                              aspect="sales_rights",
                                              field_locator="sales_rights." + sales_rights_type)

    def _serialize_value(self,
                         value):
        return list(value)
    
    def _parse_value(self,
                     value):
        return set(value)
        
    def _value_validation(self,
                          value):
        if isinstance(value, set):
            if ('WORLD' in value)  and  (value != {'WORLD'}):
                raise ValueError("Overlapping territories")
            if value.difference(self.database_object.context.territories):
                raise ValueError("Unexpected territory codes: {0}".format(value.difference(self.database_object.context.territories)))
            return value
        else:
            raise TypeError("expected instance of {0}, got instance of {1}".format(type(set),
                                                                                   type(value)))



class BookGroup(FieldGroup):
    def __init__(self,
                 document):
        super(BookGroup, self).__init__(document)
        self._fields["height"] = SimpleField(database_object=document,
                                             aspect="book.*",
                                             field_locator="book.height",
                                             dtype=int,
                                             nullable=True,
                                             kind=FieldKind.readonly)
                                             

        self._fields["width"] = SimpleField(database_object=document,
                                            aspect="book.*",
                                            field_locator="book.width",
                                            dtype=int,
                                            nullable=True,
                                            kind=FieldKind.readonly)

        self._fields["binding"] = SimpleField(database_object=document,
                                              aspect="book.*",
                                              field_locator="book.binding",
                                              dtype=BookBinding,
                                              kind=FieldKind.readonly)
                                            

        self._fields["page_count"] = SimpleField(database_object=document,
                                                 aspect="book_bod.*",
                                                 field_locator="book_bod.page_count",
                                                 dtype=int,
                                                 kind=FieldKind.readonly)

        self._fields["weight"] = SimpleField(database_object=document,
                                             aspect="book.*",
                                             field_locator="book.weight",
                                             dtype=int,
                                             nullable=True,
                                             kind=FieldKind.readonly)
        
        self._fields["weight_technical"] = SimpleField(database_object=document,
                                                       aspect="book.*",
                                                       field_locator="book.weight_technical",
                                                       dtype=int,
                                                       nullable=True,
                                                       kind=FieldKind.readonly)
        
        self._fields["weight_custom"] = SimpleField(database_object=document,
                                                    aspect="book.*",
                                                    field_locator="book.weight_custom",
                                                    dtype=int,
                                                    nullable=True)
        

    height = FieldDescriptor('height')
    width = FieldDescriptor('width')
    binding = FieldDescriptor('binding')
    page_count = FieldDescriptor('page_count')
    weight = FieldDescriptor('weight')
    weight_technical = FieldDescriptor('weight_technical')
    weight_custom = FieldDescriptor('weight_custom')

class URLsGroup(FieldGroup):
    def __init__(self,
                 document):
        super(URLsGroup, self).__init__(document)

        self._fields["storefront"] = SimpleField(database_object=document,
                                           aspect=":basic",
                                           field_locator="grin_url",
                                           dtype=str,
                                           kind=FieldKind.readonly,
                                           nullable=True)

        self._fields["covers"] = CoverURLsGroup(document=document)
                                                 

    storefront = FieldDescriptor('storefront')
    covers = FieldDescriptor('covers')

class CoverURLsGroup(FieldGroup):
    def __init__(self,
                 document):
        super(CoverURLsGroup, self).__init__(document)

        self._fields["big"] = SimpleField(database_object=document,
                                          aspect="cover_urls",
                                          field_locator="cover_urls.big",
                                          dtype=str,
                                          kind=FieldKind.readonly,
                                          nullable=True)
        self._fields["thumb"] = SimpleField(database_object=document,
                                            aspect="cover_urls",
                                            field_locator="cover_urls.thumb",
                                            dtype=str,
                                            kind=FieldKind.readonly,
                                            nullable=True)
        self._fields["original"] = SimpleField(database_object=document,
                                               aspect="cover_urls",
                                               field_locator="cover_urls.original",
                                               dtype=str,
                                               kind=FieldKind.readonly,
                                               nullable=True)
        self._fields["marketing"] = SimpleField(database_object=document,
                                                aspect="cover_urls",
                                                field_locator="cover_urls.marketing",
                                                dtype=str,
                                                kind=FieldKind.readonly,
                                                nullable=True)

    big = FieldDescriptor('big')
    thumb = FieldDescriptor('thumb')
    original = FieldDescriptor('original')
    marketing = FieldDescriptor('marketing')
    

class ProcessingGroup(FieldGroup):
    def __init__(self,
                 document):
        super(ProcessingGroup, self).__init__(document)

        self._fields["epub"] = SimpleField(database_object=document,
                                           aspect="production_configuration.*",
                                           field_locator="production_configuration.epub_processing",
                                           dtype=ProcessingType)
    
        self._fields["pdf"] = SimpleField(database_object=document,
                                          aspect="production_configuration.*",
                                          field_locator="production_configuration.pdf_processing",
                                          dtype=ProcessingType)
    
    epub = FieldDescriptor('epub')
    pdf = FieldDescriptor('pdf')
    
