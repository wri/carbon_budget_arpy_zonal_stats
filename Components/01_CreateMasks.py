import arcpy
from funcs_new import CreateMasks

#TODO: Change workspace using working_directory

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\GIS\carbon_model\CarbonFlux_QA_2023"

CreateMasks(arcpy.env.workspace)