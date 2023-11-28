import arcpy
import os
from funcs import ZonalStats, ZonalStatsClean, ZonalStatsAnnualized, ZonalStatsMasked, create_masks, zonal_stats_clean, \
    zonal_stats_masked, zonal_stats

"""
Set the workspace to the folder which contains carbon value rasters for both AOIs:
"""
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\GIS\Data\Carbon\CarbonFlux_QA_2023"

#Execute Create Masks...
print("Step 1: Creating Masks... \n")
arcpy.env.overwriteOutput = True
create_masks()

#Execute Calculate Zonal Stats...
print("Step 2: Calculating Zonal Stats... \n")
input_folder = os.path.join(arcpy.env.workspace,"Input","AOIS")
zonal_stats(input_folder)

#Execute Calculate Zonal Stats Masked...
print("Step 3: Calculating Zonal Stats with Masks... \n")
input_folder = os.path.join(arcpy.env.workspace,"Input","AOIS")
zonal_stats_masked(input_folder)

#Execute Calculcate Zonal Stats Annualized...
print("Step 3: Calculating Zonal Stats Annualized... \n")
input_folder = os.path.join(arcpy.env.workspace,"TCL")
ZonalStatsAnnualized(input_folder)

#Execute Zonal Stats Clean...
print("Step 3: Cleaning Zonal Stats... \n")
input_folders = [
    os.path.join(arcpy.env.workspace, "Outputs", "00N_110E"),
    os.path.join(arcpy.env.workspace, "Outputs", "20N_20W"),
    os.path.join(arcpy.env.workspace, "Outputs", "Annual")
]
zonal_stats_clean(input_folders)