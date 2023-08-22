import arcpy
from funcs import CreateMasks

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"U:\eglen\Data\CarbonFlux_QA_2023"

CreateMasks(arcpy.env.workspace)