__author__ = 'benjamin'
from PIL import Image, ImageDraw
import colorsys

class Sample:
    min_lat = min_lon = 10000
    max_lat = max_lon = -10000
    min_val = 10
    max_val = -10
    color1 = (46, 239, 67, 255) #green
    color2 = (147, 239, 67, 255)
    color3 = (199, 239, 67, 255)
    color4 = (224, 239, 67, 255) #yellow
    color5 = (224, 213, 67, 255)
    color6 = (224, 162, 67, 255)
    color7 = (224, 60, 67, 255) #red
    scale = (0.53, 0.54, 0.55, 0.56, 0.57, 0.62)
    classes = 7
    use_scale = False

    def __init__(self, lat, lon, val):
        """ Constructor method for the Sample class

        Note:
          Do not include the `self` parameter in the ``Args`` section.

        Args:
          lat (float): `lat` is the latitude where the sample was taken.
          lon (float): `lon` is the longitude where the sample was taken.
          val (float): `val` is the value of the taken sample.

        """
        self.lat = lat
        self.lon = lon
        self.val = val

    def get_color_from_val(self):
        #percent = (self.val - Sample.min_val) / (Sample.max_val - Sample.min_val)
        if self.val <= Sample.scale[0]:
            self.color = Sample.color7
        elif self.val <= Sample.scale[1]:
            self.color = Sample.color6
        elif self.val <= Sample.scale[2]:
            self.color = Sample.color5
        elif self.val <= Sample.scale[3]:
            self.color = Sample.color4
        elif self.val <= Sample.scale[4]:
            self.color = Sample.color3
        elif self.val <= Sample.scale[5]:
            self.color = Sample.color2
        else:
            self.color = Sample.color1
        return self.color

    @staticmethod
    def reset_values():
        Sample.min_lat = Sample.min_lon = 10000
        Sample.max_lat = Sample.max_lon = -10000
        Sample.min_val = 10
        Sample.max_val = -10

    @staticmethod
    def useScale(scale):
         Sample.scale = scale
         Sample.use_scale = True

    @staticmethod
    def useNaturalBreaks(classes):
         Sample.classes = classes
         Sample.use_scale = False
