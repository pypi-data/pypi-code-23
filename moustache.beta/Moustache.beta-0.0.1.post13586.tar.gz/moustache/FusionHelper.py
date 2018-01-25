import os
import uno
import time
from wand.color import Color
from wand.image import Image


class FusionHelper:
    @staticmethod
    def create_uno_service(service_name):
        sm = uno.getComponentContext().ServiceManager
        return sm.createInstanceWithContext(service_name, uno.getComponentContext())

    @staticmethod
    def urlify(path):
        return uno.systemPathToFileUrl(os.path.realpath(path))

    def __init__(self, port, filepath):
        # get the uno component context from the PyUNO runtime
        local_context = uno.getComponentContext()
        # create the UnoUrlResolver
        resolver = local_context.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", local_context)
        # connect to the running office
        self.ctx = resolver.resolve(
            "uno:socket,host=localhost,port={0};urp;StarOffice.ComponentContext".format(str(port)))
        smgr = self.ctx.ServiceManager
        # get the central desktop object
        desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", self.ctx)
        self.comp = desktop.loadComponentFromURL(self.urlify(filepath), "_blank", 0, ())
        # access the current writer document
        self.model = desktop.getCurrentComponent()
        self.document = self.model.getCurrentController().getFrame()
        self.dispatcher = self.create_uno_service("com.sun.star.frame.DispatchHelper")

    @staticmethod
    def create_property_value(name, value):
        prop = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
        prop.Name = name
        prop.Value = value
        return prop

    def search_and_select(self, text):
        properties = (
            self.create_property_value('SearchItem.SearchString', text),
        )
        self.dispatcher.executeDispatch(self.document, ".uno:ExecuteSearch", "", 0, properties)
        return not self.get_cursor().isCollapsed()

    def search_and_replace(self, text, replace):
        properties = (
            self.create_property_value('SearchItem.SearchString', text),
            self.create_property_value('SearchItem.ReplaceString', replace),
            self.create_property_value('SearchItem.Command', 3),
        )
        self.dispatcher.executeDispatch(self.document, ".uno:ExecuteSearch", "", 0, properties)

    def insert_odt(self, path):
        properties = (
            self.create_property_value('Name', self.urlify(path)),
        )
        self.dispatcher.executeDispatch(self.document, ".uno:InsertDoc", "", 0, properties)

    def insert_txt(self, txt):
        properties = (
            self.create_property_value('Text', txt),
        )
        self.dispatcher.executeDispatch(self.document, ".uno:InsertText", "", 0, properties)

    def _file2istream(self, fbytes):
        istream = self.ctx.ServiceManager.createInstanceWithContext("com.sun.star.io.SequenceInputStream", self.ctx)
        istream.initialize((uno.ByteSequence(fbytes),))
        return istream

    def load_graphic_context(self, img_data):
        graphic_provider = self.ctx.ServiceManager.createInstanceWithContext("com.sun.star.graphic.GraphicProvider",
                                                                             self.ctx)
        properties = (
            self.create_property_value('InputStream', self._file2istream(img_data)),
        )
        return graphic_provider.queryGraphic(properties)

    def insert_pdf(self, filename, watermark):
        # TAG for search and replace multiple PDF
        self.insert_txt("++-=0=-++")
        all_pages = Image(blob=open(filename, 'rb').read())  # PDF will have several pages.
        basename = os.path.basename(filename)
        for index, image in enumerate(all_pages.sequence):
            with Image(image) as img:
                img.background_color = Color('white')
                img.alpha_channel = 'remove'
                if watermark:
                    img.watermark(image=watermark, transparency=0.75, left=160, top=275)
                self.search_and_select("++-={0}=-++".format(str(index)))
                self.execute("InsertPagebreak")
                self.insert_txt("§§{0}§§{1}§§".format(basename, str(index + 1)))
                self.insert_txt("++-={0}=-++".format(str(index + 1)))
                self.insert_img(img.make_blob('png'))
                self.execute("SetAnchorToPage")

        self.search_and_replace("++-={0}=-++".format(str(len(all_pages.sequence))), "")

    def insert_img(self, img_data):
        img = self.comp.createInstance('com.sun.star.text.TextGraphicObject')

        img.Graphic = self.load_graphic_context(img_data)
        img.Surround = uno.Enum("com.sun.star.text.WrapTextMode", "THROUGHT")
        img.Width = 21000
        img.Height = 29700

        text = self.comp.Text
        cursor = self.get_cursor()
        text.insertTextContent(cursor, img, False)

    def execute(self, cmd):
        self.dispatcher.executeDispatch(self.document, ".uno:{0}".format(cmd), "", 0, ())

    def get_cursor(self):
        return self.model.getCurrentController().getViewCursor()

    def save_and_close(self, path):
        self.model.storeToURL(self.urlify(path), ())
        # close the document
        self.model.dispose()


# Pour exemple, le code suivant ajoute des annexes après avoir détécté le tag "ANNEXES" sur un document odt
if __name__ == '__main__':
    helper = FusionHelper(2002, "test.odt")
    if helper.search_and_select("ANNEXES"):
        # Pas de watermark
        helper.insert_pdf("test.pdf", None)
        # Watermark "working.jpg"
        helper.insert_pdf("99_DC-034-213401425-20171218-CM_171205_16_2-CC-1-1_1__1_.pdf", Image(filename='working.jpg'))

    helper.save_and_close("saved.odt")
