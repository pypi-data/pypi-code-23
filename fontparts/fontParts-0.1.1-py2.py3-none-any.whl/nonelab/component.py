import defcon
from fontParts.base import BaseComponent, FontPartsError
from fontParts.nonelab.base import RBaseObject


class RComponent(RBaseObject, BaseComponent):

    wrapClass = defcon.Component

    # ----------
    # Attributes
    # ----------

    # baseGlyph

    def _get_baseGlyph(self):
        return self.naked().baseGlyph

    def _set_baseGlyph(self, value):
        self.naked().baseGlyph = value

    # transformation

    def _get_transformation(self):
        return self.naked().transformation

    def _set_transformation(self, value):
        self.naked().transformation = value

    # --------------
    # Identification
    # --------------

    # index

    def _set_index(self, value):
        component = self.naked()
        glyph = component.glyph
        if value > glyph.component.index(component):
            value -= 1
        glyph.removeComponent(component)
        glyph.insertComponent(value, component)

    # identifier

    def _get_identifier(self):
        component = self.naked()
        return component.identifier

    def _getIdentifier(self):
        component = self.naked()
        return component.generateIdentifier()

    # -------------
    # Normalization
    # -------------

    def _decompose(self):
        component = self.naked()
        glyph = component.glyph
        glyph.decomposeComponent(component)
