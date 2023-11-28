import arcpy
import os
import pandas as pd
from funcs import ZonalStatsAnnualized
arcpy.env.overwriteOutput = True

#TODO: Change workspace using working_directory

# Set the workspace and input/output folders
arcpy.env.workspace = r"C:\GIS\carbon_model\CarbonFlux_QA_2023"

ZonalStatsAnnualized(arcpy.env.workspace)

