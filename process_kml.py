from PIL import Image, ImageDraw
import json

from Sample import *
from Bound import *
from geopy.distance import vincenty

# code from http://danieljlewis.org/files/2010/06/Jenks.pdf
# described at http://danieljlewis.org/2010/06/07/jenks-natural-breaks-algorithm-in-python/

def getJenksBreaks( dataList, numClass ):
  dataList.sort()
  mat1 = []
  for i in range(0,len(dataList)+1):
    temp = []
    for j in range(0,numClass+1):
      temp.append(0)
    mat1.append(temp)
  mat2 = []
  for i in range(0,len(dataList)+1):
    temp = []
    for j in range(0,numClass+1):
      temp.append(0)
    mat2.append(temp)
  for i in range(1,numClass+1):
    mat1[1][i] = 1
    mat2[1][i] = 0
    for j in range(2,len(dataList)+1):
      mat2[j][i] = float('inf')
  v = 0.0
  for l in range(2,len(dataList)+1):
    s1 = 0.0
    s2 = 0.0
    w = 0.0
    for m in range(1,l+1):
      i3 = l - m + 1
      val = float(dataList[i3-1])
      s2 += val * val
      s1 += val
      w += 1
      v = s2 - (s1 * s1) / w
      i4 = i3 - 1
      if i4 != 0:
        for j in range(2,numClass+1):
          if mat2[l][j] >= (v + mat2[i4][j - 1]):
            mat1[l][j] = i3
            mat2[l][j] = v + mat2[i4][j - 1]
    mat1[l][1] = 1
    mat2[l][1] = v
  k = len(dataList)
  kclass = []
  for i in range(0,numClass+1):
    kclass.append(0)
  kclass[numClass] = float(dataList[len(dataList) - 1])
  countNum = numClass
  while countNum >= 2:
    id = int((mat1[k][countNum]) - 2)

    kclass[countNum - 1] = dataList[id]
    k = int((mat1[k][countNum] - 1))
    countNum -= 1
  return kclass

def getGVF( dataList, numClass ):
  """
  The Goodness of Variance Fit (GVF) is found by taking the
  difference between the squared deviations
  from the array mean (SDAM) and the squared deviations from the
  class means (SDCM), and dividing by the SDAM
  """
  breaks = getJenksBreaks(dataList, numClass)
  dataList.sort()
  listMean = sum(dataList)/len(dataList)
  print listMean
  SDAM = 0.0
  for i in range(0,len(dataList)):
    sqDev = (dataList[i] - listMean)**2
    SDAM += sqDev
  SDCM = 0.0
  for i in range(0,numClass):
    if breaks[i] == 0:
      classStart = 0
    else:
      classStart = dataList.index(breaks[i])
      classStart += 1
    classEnd = dataList.index(breaks[i+1])
    classList = dataList[classStart:classEnd+1]
    classMean = sum(classList)/len(classList)
    print classMean
    preSDCM = 0.0
    for j in range(0,len(classList)):
      sqDev2 = (classList[j] - classMean)**2
      preSDCM += sqDev2
    SDCM += preSDCM
  return (SDAM - SDCM)/SDAM

# written by Drew
# used after running getJenksBreaks()
def classify(value, breaks):
  for i in range(1, len(breaks)):
    if value < breaks[i]:
      return i
  return len(breaks) - 1

def generate(filename):
    with open(filename + '.json') as data_file:
        data = json.load(data_file)
    samples = []
    ndvi = []
    for line in data['features']:
        if line['geometry']['type'] == 'Polygon' and float(line['properties']['name']) < 1:
            coords = []
            for coord in line['geometry']['coordinates'][0]:
                coords.append((coord[1], coord[0]))
            center = Bound(coords).getCenter()
            s = Sample(center[0], center[1], float(line['properties']['name']))
            samples.append(s)
            ndvi.append(s.val)
            if s.lat > Sample.max_lat:
                Sample.max_lat = s.lat
            if s.lat < Sample.min_lat:
                Sample.min_lat = s.lat
            if s.lon > Sample.max_lon:
                Sample.max_lon = s.lon
            if s.lon < Sample.min_lon:
                Sample.min_lon = s.lon
            if s.val < Sample.min_val:
                Sample.min_val = s.val
            if s.val > Sample.max_val:
                Sample.max_val = s.val
    if not Sample.use_scale:
        classes = getJenksBreaks(ndvi, Sample.classes)
        Sample.scale = classes[1:]

    print(str(Sample.scale))
    print('SouthWest: ' + str(Sample.min_lat) + ', ' + str(Sample.min_lon))
    print('NorthEast: ' + str(Sample.max_lat) + ', ' + str(Sample.max_lon))
    hdist = vincenty((Sample.max_lat, Sample.min_lon),
                     (Sample.max_lat, Sample.max_lon)).meters
    vdist = vincenty((Sample.max_lat, Sample.min_lon),
                     (Sample.min_lat, Sample.min_lon)).meters
    print('Horizontal Distance: ' + str(hdist))
    print('Vertical Distance: ' + str(vdist))
    multiplier = 2000/max((hdist,vdist)) #2000 will be the size of our picture
    width = int((hdist + 6) * multiplier)
    height = int((vdist + 6) * multiplier)
    print('Desired Size: ' + str(width) + 'x' + str(height))

    img = Image.new('RGBA', (width, height))

    draw = ImageDraw.Draw(img)
    print(len(samples))
    for samp in samples:
        x_dist = int(vincenty((Sample.max_lat, Sample.min_lon),
                              (Sample.max_lat, samp.lon)).meters)
        y_dist = int(vincenty((Sample.max_lat, Sample.min_lon),
                              (samp.lat, Sample.min_lon)).meters)
        color = samp.get_color_from_val()
        draw.rectangle([int((x_dist) * multiplier), int((y_dist) * multiplier), int((x_dist + 5) * multiplier),
                        int((y_dist + 5) * multiplier)], fill=color,
                       outline=(0, 0, 0, 255))
    #comment out this if/else if you want the original size
    if width > height:
        img = img.resize((600, height*600/width), Image.LANCZOS)
    else:
        img = img.resize((width*600/height, 600), Image.LANCZOS)
    img.save(filename + '.png', 'PNG')


#Sample.useScale((0.53, 0.54, 0.55, 0.56, 0.57, 0.62)) #comment out next line to use this
Sample.useNaturalBreaks(7)
Sample.reset_values()
generate('kiwi')
print("-----------------")
#Sample.scale = (0.58, 0.59, 0.60, 0.61, 0.64, 0.77)
Sample.useNaturalBreaks(7)
Sample.reset_values()
generate('apples')
print("-----------------")
Sample.reset_values()