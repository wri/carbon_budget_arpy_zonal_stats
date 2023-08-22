import arcpy
import os
from funcs import ZonalStats, ZonalStatsClean, ZonalStatsAnnualized, ZonalStatsMasked, CreateMasks

"""
Set the workspace to the folder which contains carbon value rasters for both AOIs:
"""
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"U:\eglen\Data\CarbonFlux_QA_2023"

#Execute Create Masks...
print("Step 1: Creating Masks... \n")
arcpy.env.overwriteOutput = True
CreateMasks(arcpy.env.workspace)

#Execute Calculate Zonal Stats...
print("Step 2: Calculating Zonal Stats... \n")
input_folder = os.path.join(arcpy.env.workspace,"Input","AOIS")
ZonalStats(input_folder)

#Execute Calculate Zonal Stats Masked...
print("Step 3: Calculating Zonal Stats with Masks... \n")
input_folder = os.path.join(arcpy.env.workspace,"Input","AOIS")
mask_tiles = os.path.join(arcpy.env.workspace,"Mask","Mask")
ZonalStatsMasked(input_folder)

#Execute Calculcate Zonal Stats Annualized...
print("Step 3: Calculating Zonal Stats Annualized... \n")
input_folder = os.path.join(arcpy.env.workspace,"TCL")
ZonalStatsAnnualized(input_folder)

#Execute Zonal Stats Clean...
print("Step 3: Cleaning Zonal Stats... \n")
ZonalStatsClean(arcpy.env.workspace)