# -*- coding: utf-8 -*-
"""
Created on March 2017
@author: S. Gaitan & E. Cristiano
"""
#%%
#importing some needed libraries
from shapely.geometry import Polygon, Point, shape
from shapely.ops import unary_union
import fiona
import os
import pandas as pd
import numpy as np
#%%
#Define the selected thresholds
Thresholds = [0.000001, 0.546, 7.097, 22.022] #thresholds in mm/h
#moving to folder where the data is
my_dir = 'O:\Data_and_results\Cluster\PerSantiago_E1\catchement'
#my_dir = 'D:\ecristiano\Desktop\PerSantiago_E1\catchement'
os.chdir(my_dir)
### The function storm_loader consider the shape file containing the needed data, it opens it as a collection and estract all the record and the projection (crs)
def storm_loader(a_shp):
    '''To be properly documented afterward
    '''
    collection = fiona.open(a_shp, 'r') #with fiona it the shape file is open
    crs = collection.crs #the projection is estracted
    records = [] # empty list for records
    for i in range(len(collection)):
        records.append( next(collection))
    collection.close()
    return records, crs
###
##
#%%
#The geoDF_loader function build a pandas DataFrame containing the records read with fiona
def geoDF_loader(records):
    '''To be properly documented afterward
    '''
    # the DataFrame contains the type of geometry ("type"), the properties, the geometry (needed for the plot) and rainfall values (each colum represents a time step). The index is the name of the rainfall pixel considered.
    geoDF = pd.DataFrame({'type': [i['geometry']['type'] for i in records],
                          'properties': [i['properties'] for i in records],
                          'geometry': [i['geometry'] for i in records],
                          'Pixel' : [i['properties']['PROFILE'] for i in records]
                          })
    geoDF['sequence'] = np.arange(len(geoDF))
    keys = records[0]['properties'].keys()[2:]
    #This for cicle is needed to have a colum fro eac time step:
    for j in keys:
        column_vect = []
        for i in records:
            rainfall_values = i['properties'][j]
            column_vect.append(rainfall_values)
        geoDF[j] = column_vect
    return geoDF, keys
###
###
#%%
#This function produces the geometry of the records considered
def geometries_producer(some_records):
    a_geom = [shape(i['geometry']) for i in some_records]
    return a_geom
###
###
    #%%
# this function filters the pixels that are above a certain threshold and merges neighbours in one poligon and return the area of this poligon
def filtrare(a_geoDF, a_threshold, a_timestep):
    #Getting mask of raincells above the threshold:
    mask = a_geoDF[a_timestep] >= a_threshold
    #Get a dissolve multipolygon rainfall cluster:
    a_dissolved = unary_union([shape(i) for i in a_geoDF['geometry'][mask].values])
    some_results = pd.DataFrame(columns=['timestep','subpolygon', 'area', 'perimeter', 'P/M'])
    #consider to add "shape"
    if type(a_dissolved) == Polygon:
        some_results=some_results.append({'timestep':a_timestep,'subpolygon':1, 'area':a_dissolved.area, 'perimeter':a_dissolved.length, 'P/M':'P'},ignore_index=True)
    else:
        for j in range(len(a_dissolved)):
            if a_dissolved[j].area>85100:
                some_results=some_results.append(pd.DataFrame({'timestep':a_timestep,'subpolygon':j, 'area':a_dissolved[j].area, 'perimeter':a_dissolved[j].length, 'P/M':'M'},index=[j]))
            else:
                some_results=some_results.append(pd.DataFrame({'timestep':a_timestep,'subpolygon':j, 'area':0, 'perimeter':a_dissolved[j].length, 'P/M':'M'},index=[j]))
    some_results['ratio'] = some_results['area'] / some_results['perimeter']
    return some_results
###
#%%
#Raggio_av = []
#AreaAv = []
#for event in range(1):
#    my_records, my_crs = storm_loader('E'+str(event+1)+'.shp')
#    my_geoDF, my_keys = geoDF_loader(my_records)
#    my_geom = geometries_producer(my_records)
#    for Threshold in Thresholds:
#        Time_step=[]
#        Area=[]
#        length = []
#        Raggio = []
#        for t in range(len(my_keys)):
#            my_mask, timestep_plot= filtrare(my_geoDF,Threshold,my_keys[t])
#            area_at_timestep = timestep_plot.area
#            perimeter_at_timestep = timestep_plot.length
#            Time_step.append(t)
#            Area.append(area_at_timestep)
#            length.append(perimeter_at_timestep)
#            if perimeter_at_timestep >0:
#                raggio_at_timestep  = area_at_timestep/perimeter_at_timestep
#                Raggio.append(raggio_at_timestep)
#            else:
#                Raggio.append(0)
#        Raggio_average = np.mean(Raggio)
#        Raggio_av.append(Raggio_average)
#        AreaAvVal  = np.mean(Area)
#        AreaAv.append(AreaAvVal)
#AreaDF=pd.DataFrame(AreaAv)
#AreaDF.to_csv("Area.csv")



#%%
if __name__ == '__main__':
    for ev in range(9):
        Thresholds = [0.000001, 0.546, 7.097, 22.022]
        my_shape = 'Ev_ShapeFiles\E'+str(ev+1)+'.shp'
        records, crs = storm_loader(my_shape)
        my_geoDF, my_keys = geoDF_loader(records)
        my_geom = geometries_producer(records)
        for threshold in Thresholds:
            Results = pd.DataFrame(columns=['timestep','subpolygon', 'area', 'perimeter', 'shape'])
            for timestep in my_keys:
                my_threshold, my_timestep = threshold, timestep
                my_results = filtrare(my_geoDF, my_threshold, my_timestep)
                Results=Results.append(my_results,ignore_index=True)
            Results.to_csv("2E"+str(ev+1)+"_T"+str(threshold)+"_output.csv")
