import arcpy
import os
from funcs import ZonalStats, ZonalStatsClean, ZonalStatsAnnualized, ZonalStatsMasked, CreateMasks
from constants_and_names import working_directory, overwrite_output, aois_folder

#TODO: Line 14 - Does overwrite option need to be overwritten to true there?
#TODO: Update input_folder/ mask_tiles with constants and names variables

arcpy.env.workspace = working_directory
arcpy.env.overwriteOutput = overwrite_output

#Execute Download File...
print("Step 0: Downloading Files... \n")

#Execute Create Masks...
print("Step 1: Creating Masks... \n")
#arcpy.env.overwriteOutput = True
CreateMasks(arcpy.env.workspace)

#Execute Calculate Zonal Stats...
print("Step 2: Calculating Zonal Stats... \n")
input_folder = os.path.join(arcpy.env.workspace, "AOIS")
ZonalStats(input_folder)

#Execute Calculate Zonal Stats Masked...
print("Step 3: Calculating Zonal Stats with Masks... \n")
input_folder = os.path.join(arcpy.env.workspace, "AOIS")
mask_tiles = os.path.join(arcpy.env.workspace,"Mask","Mask")
ZonalStatsMasked(input_folder)

#Execute Calculcate Zonal Stats Annualized...
print("Step 4: Calculating Zonal Stats Annualized... \n")
input_folder = os.path.join(arcpy.env.workspace,"TCL")
ZonalStatsAnnualized(input_folder)

#Execute Zonal Stats Clean...
print("Step 5: Cleaning Zonal Stats... \n")
ZonalStatsClean(arcpy.env.workspace)