import defcon
from fontParts.base import BasePoint, FontPartsError
from fontParts.nonelab.base import RBaseObject


class RPoint(RBaseObject, BasePoint):

    wrapClass = defcon.Point

    def _init(self, wrap=None):
        if wrap is None:
            wrap = self.wrapClass((0, 0))
        super(RPoint, self)._init(wrap=wrap)

    # ----------
    # Attributes
    # ----------

    # type

    def _get_type(self):
        value = self.naked().segmentType
        if value is None:
            value = "offcurve"
        return value

    def _set_type(self, value):
        if value == "offcurve":
            value = None
        self.naked().segmentType = value

    # smooth

    def _get_smooth(self):
        return self.naked().smooth

    def _set_smooth(self, value):
        self.naked().smooth = value

    # x

    def _get_x(self):
        return self.naked().x

    def _set_x(self, value):
        self.naked().x = value

    # y

    def _get_y(self):
        return self.naked().y

    def _set_y(self, value):
        self.naked().y = value

    # --------------
    # Identification
    # --------------

    # name

    def _get_name(self):
        return self.naked().name

    def _set_name(self, value):
        self.naked().name = value

    # identifier

    def _get_identifier(self):
        point = self.naked()
        return point.identifier

    def _getIdentifier(self):
        point = self.naked()
        value = point.identifier
        if value is not None:
            return value
        contour = self.contour.naked()
        if contour is not None:
            contour.generateIdentifierForPoint(point)
            value = point.identifier
        else:
            raise FontPartsError("An identifier can not be generated for this point because it does not belong to a contour.")
        return value
