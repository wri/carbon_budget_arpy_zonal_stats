import arcpy
import os
import pandas
from funcs import ZonalStatsMasked

arcpy.env.overwriteOutput = True

# Set the workspace and input/output folders
arcpy.env.workspace = r"U:\eglen\Data\CarbonFlux_QA_2023"

ZonalStatsMasked(arcpy.env.workspace)

