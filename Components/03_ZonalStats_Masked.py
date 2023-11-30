import arcpy
import os
import pandas
from funcs_new import ZonalStatsMasked

#TODO: Change workspace using working_directory

arcpy.env.overwriteOutput = True

# Set the workspace and input/output folders
arcpy.env.workspace = r"C:\GIS\carbon_model\CarbonFlux_QA_2023"

ZonalStatsMasked(arcpy.env.workspace)

