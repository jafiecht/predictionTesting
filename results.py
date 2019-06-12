#This file evaluates the performance of predictions

#Imports
#######################################################################
import shutil
import os
import subprocess
import geopandas as gpd
import rasterio
from rasterio import features
import numpy as np
import metrics


#Evaluate Performance
#######################################################################
def evaluate(fileName):
  print('\n    ' + fileName)
  
  #Create a directory for the rasterized testing points
  subprocess.call('mkdir rasterized', shell=True)
  
  #Make a geodataframe, then create an ID column
  points = gpd.read_file('testData/testingPoints.shp')
  points = points.to_crs({'init': 'epsg:26916'})
  points['Point_ID'] = points.index

  #Open the template raster for template information
  template = rasterio.open('predictions/' + fileName)
  meta = template.meta.copy()
  meta['nodata'] = 9999
  
  #Create an individual file for each point
  for index, row in points.iterrows():
    
    #Create a new raster for writing.
    with rasterio.open('rasterized/'+str(row.Point_ID)+'.tif', 'w', **meta) as out:
      out_arr = out.read(1)
     
      #Transform and rasterize shape data
      shapes = ((geom, value) for geom, value in zip([row.geometry], [row['OM']]))
      burned = features.rasterize(shapes = shapes, fill=0, out=out_arr, transform=out.transform)
      
      #Write the data out as a raster
      out.write_band(1, burned)
      out.close()
 
 
  #Get the filenames for each individual raster
  individuals = os.listdir('rasterized')

  #Get the index and value of each individual rasterized point
  point_data = {}
  for individual in individuals:
    #Open the input raster
    raster = rasterio.open('rasterized/' + individual)
    array = raster.read(1)

    #Get the index for the min value (the datapoint)
    flat_index = np.argmin(array)
    index = np.unravel_index(flat_index, array.shape)

    #Write the data to the dictionary
    key = os.path.splitext(individual)[0]
    point_data[key] = {'index': index, 'value': array[index]}


  #Read the prediction file in as an array
  raster = rasterio.open('predictions/' + fileName) 
  prediction = raster.read(1) 

  #Get the actual and predicted values
  value_pairs = []
  for point in list(point_data.keys()):
    value_pairs.append([point_data[point]['value'], prediction[point_data[point]['index'][0], point_data[point]['index'][1]]])


  #Get performance metrics
  scores = metrics.generate_metrics(value_pairs)

  print('     R2 Score: ' + str(scores[0]))
  print('     RMSE: ' + str(scores[1]))
  print('     ME: ' + str(scores[2]))
  print('     MAE: ' + str(scores[3]))

  #Remove the individual rasters
  shutil.rmtree('rasterized/')


#Evaluate all predictions
#######################################################################
predictions = os.listdir('predictions')

for prediction in predictions:
  evaluate(prediction)


