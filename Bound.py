__author__ = 'benjamin'
class Bound:
    def __init__(self, coords):
        self.coords = coords

    def getCenter(self):
        min_x = 10000
        min_y = 10000
        max_x = -10000
        max_y = -10000
        for coord in self.coords:
            if coord[0] > max_x: max_x = coord[0]
            if coord[0] < min_x: min_x = coord[0]
            if coord[1] > max_y: max_y = coord[1]
            if coord[1] < min_y: min_y = coord[1]
        self.lat = (min_x + max_x)/2
        self.lon = (min_y + max_y)/2
        return (self.lat, self.lon)