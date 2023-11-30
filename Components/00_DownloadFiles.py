import arcpy
import os
import constants_and_names as cn
from funcs import DownloadFiles

#TODO: DOWNLOAD GADM BOUNDARY SHAPEFILES TO AOIS FOLDER?

arcpy.env.workspace = cn.working_directory
arcpy.env.overwriteOutput = cn.overwrite_output

DownloadFiles(arcpy.env.workspace)