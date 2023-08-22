import arcpy
from funcs import ZonalStats
import os

arcpy.env.overwriteOutput = True

# Set the workspace and input/output folders
arcpy.env.workspace = r"U:\eglen\Data\CarbonFlux_QA_2023"
print(arcpy.env.workspace)
input_folder = os.path.join(arcpy.env.workspace,"Input","AOIS")

ZonalStats(input_folder)


