#this file imports a tif, then shows it.
import gdal
import matplotlib.pyplot as plt
from matplotlib import cm
import os


#Load .tif file
def show_tif(filename):
  print(filename[12:-4])
  raster = gdal.Open(filename)
  band = raster.GetRasterBand(1).ReadAsArray()
  plt.imshow(band, cmap = cm.Greys, vmin=0, vmax=8.5)
  plt.colorbar()
  #plt.title(filename[12:-4].replace('_', ' '))
  #plt.show()
  plt.savefig(filename[12:-4], bbox_inches='tight')
  plt.close()
  raster = None
  return

images = os.listdir('predictions')

for image in images:
  show_tif('predictions/' + image)
