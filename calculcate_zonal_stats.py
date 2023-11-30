import arcpy
import os
from funcs_new import create_masks, zonal_stats_clean, zonal_stats_masked, zonal_stats, zonal_stats_annualized
from constants_and_names import working_directory, overwrite_output, aois_folder

#TODO: Line 14 - Does overwrite option need to be overwritten to true there?
#TODO: Update input_folder/ mask_tiles with constants and names variables

"""
Set the workspace to the folder which contains carbon value rasters for both AOIs:
"""
arcpy.env.workspace = working_directory
arcpy.env.overwriteOutput = overwrite_output

#Execute Download File...
print("Step 0: Downloading Files... \n")

#Execute Create Masks...
print("Step 1: Creating Masks... \n")
#arcpy.env.overwriteOutput = True
create_masks()

#Execute Calculate Zonal Stats...
print("Step 2: Calculating Zonal Stats... \n")
input_folder = os.path.join(arcpy.env.workspace,"AOIS")
zonal_stats(input_folder)

#Execute Calculate Zonal Stats Masked...
print("Step 3: Calculating Zonal Stats with Masks... \n")
input_folder = os.path.join(arcpy.env.workspace,"AOIS")
zonal_stats_masked(input_folder)

#Execute Calculcate Zonal Stats Annualized...
print("Step 4: Calculating Zonal Stats Annualized... \n")
annual_input_folder = os.path.join(arcpy.env.workspace, "TCL")
zonal_stats_annualized(annual_input_folder)

#Execute Zonal Stats Clean...
print("Step 5: Cleaning Zonal Stats... \n")
input_folders = [
    os.path.join(arcpy.env.workspace, "Outputs", "00N_110E"),
    os.path.join(arcpy.env.workspace, "Outputs", "20N_20W"),
    os.path.join(arcpy.env.workspace, "Outputs", "Annual")
]
zonal_stats_clean(input_folders)