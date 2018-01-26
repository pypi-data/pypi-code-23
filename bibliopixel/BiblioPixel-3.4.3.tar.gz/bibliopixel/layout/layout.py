import time
from .. import util
from .. project import attributes, data_maker, fields
from .. util.threads.update_threading import UpdateThreading


class Layout(object):
    pre_recursion = fields.default_converter

    @classmethod
    def construct(cls, project, **desc):
        """Construct a layout."""
        return cls(project.drivers, maker=project.maker, **desc)

    def __init__(self, drivers, threadedUpdate, brightness,
                 maker=data_maker.MAKER, **kwds):
        """Base LED class. Use Strip or Matrix instead!"""
        attributes.set_reserved(self, 'layout', **kwds)
        self.drivers = drivers if isinstance(drivers, list) else [drivers]
        self.maker = maker

        if not hasattr(self, 'numLEDs'):
            self.numLEDs = sum(d.numLEDs for d in self.drivers)

        # This buffer will always be the same list - i.e. is guaranteed to only
        # be changed by list surgery, never assignment.
        self._colors = maker.color_list(self.numLEDs)

        pos = 0
        for d in self.drivers:
            d.set_colors(self._colors, pos)
            pos += d.numLEDs

        self.frame_render_time = 0
        self.animation_sleep_time = None

        self.threading = UpdateThreading(threadedUpdate, self)
        self.brightness = brightness
        self.set_brightness(brightness)

    def set_pixel_positions(self, pixel_positions):
        for d in self.drivers:
            d.set_pixel_positions(pixel_positions)

    def update(self):
        """DEPRECATED - use self.push_to_driver()"""
        return self.push_to_driver()

    def start(self):
        for d in self.drivers:
            d.start()

    def cleanup_drivers(self):
        for d in self.drivers:
            d.cleanup()

    def cleanup(self):
        self.all_off()
        self.push_to_driver()
        self.threading.wait_for_update()

    @property
    def color_list(self):
        return self._colors

    @color_list.setter
    def color_list(self, cl):
        self._colors[:] = cl

    def _get_base(self, pixel):
        if pixel >= 0 and pixel < self.numLEDs:
            return self._colors[pixel]
        return 0, 0, 0  # don't go out of bounds

    def _set_base(self, pixel, color):
        if pixel >= 0 and pixel < self.numLEDs:
            if isinstance(color, str):
                color = util.colors.COLORS[color]
            else:
                color = tuple(color)
            self.color_list[pixel] = color

    def get_pixel_positions(self):
        result = []
        for x in range(len(self.numLEDs)):
            result.append([x, 0, 0])
        return result

    def push_to_driver(self):
        """Push the current pixel state to the driver"""
        # This is overridden elsewhere.
        self.threading.push_to_driver()

    # use with caution!
    def set_colors(self, buf):
        """Use with extreme caution!
        Directly sets the internal buffer and bypasses all brightness and rotation control.
        buf must also be in the exact format required by the display type.
        """
        if len(self._colors) != len(buf):
            raise IOError("Data buffer size incorrect! "
                          "Expected: {} bytes / Received: {} bytes"
                          .format(len(self._colors), len(buf)))
        self._colors[:] = buf

    def setBuffer(self, buf):
        """DEPRECATED!"""
        # https://stackoverflow.com/questions/1624883
        self.set_colors(buf=list(zip(*(iter(buf),) * 3)))

    def set_brightness(self, brightness):
        self.brightness = brightness
        for d in self.drivers:
            d.set_brightness(brightness)

    # Set single pixel to RGB value
    def setRGB(self, pixel, r, g, b):
        """Set single pixel using individual RGB values instead of tuple"""
        self._set_base(pixel, (r, g, b))

    def setHSV(self, pixel, hsv):
        """Set single pixel to HSV tuple"""
        color = util.colors.hsv2rgb(hsv)
        self._set_base(pixel, color)

    # turns off the desired pixel
    def setOff(self, pixel):
        """Set single pixel off"""
        self._set_base(pixel, (0, 0, 0))

    def all_off(self):
        """Set all pixels off"""
        self._colors[:] = [(0, 0, 0)] * self.numLEDs

    # Fill the strand (or a subset) with a single color using a Color object
    def fill(self, color, start=0, end=-1):
        """Fill the entire strip with RGB color tuple"""
        start = max(start, 0)
        if end < 0 or end >= self.numLEDs:
            end = self.numLEDs - 1
        for led in range(start, end + 1):  # since 0-index include end in range
            self._set_base(led, color)

    # Fill the strand (or a subset) with a single color using RGB values
    def fillRGB(self, r, g, b, start=0, end=-1):
        """Fill entire strip by giving individual RGB values instead of tuple"""
        self.fill((r, g, b), start, end)

    # Fill the strand (or a subset) with a single color using HSV values
    def fillHSV(self, hsv, start=0, end=-1):
        """Fill the entire strip with HSV color tuple"""
        self.fill(util.colors.hsv2rgb(hsv), start, end)


class MultiLayout(Layout):
    def __init__(self, *args, gen_coord_map=None, coord_map=None, **kwds):
        super().__init__(*args, **kwds)
        if gen_coord_map:
            if coord_map:
                util.log.warning('Cannot set both coord_map and gen_coord_map')
            elif isinstance(gen_coord_map, dict):
                coord_map = self.gen_multi(**gen_coord_map)
            else:
                coord_map = self.gen_multi(gen_coord_map)
        self.coord_map = coord_map

    def gen_multi(self, *args, **kwds):
        raise NotImplementedError
