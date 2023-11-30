import arcpy
from funcs_new import ZonalStats
import os

#TODO: Change workspace using working_directory

arcpy.env.overwriteOutput = True

# Set the workspace and input/output folders
arcpy.env.workspace = r"C:\GIS\carbon_model\CarbonFlux_QA_2023"
print(arcpy.env.workspace)
input_folder = os.path.join(arcpy.env.workspace, "AOIS")

ZonalStats(input_folder)


