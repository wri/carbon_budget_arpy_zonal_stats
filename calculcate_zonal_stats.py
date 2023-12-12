import os
import constants_and_names as cn
from funcs import DownloadFiles, create_masks, zonal_stats, zonal_stats_masked, zonal_stats_annualized, ZonalStatsClean

#Execute Download File...
print("Step 0: Downloading Files... \n")
DownloadFiles()

#Execute Create Masks...
print("Step 1: Creating Masks... \n")
create_masks(cn.tcd_folder, cn.gain_folder, cn.whrc_folder, cn.mangrove_folder, cn.plantations_folder, cn.tcd_threshold, cn.gain)

#Execute Calculate Zonal Stats...
print("Step 2: Calculating Zonal Stats... \n")
zonal_stats(cn.aois_folder)

#Execute Calculate Zonal Stats Masked...
print("Step 3: Calculating Zonal Stats with Masks... \n")
zonal_stats_masked(cn.aois_folder, cn.input_folder, cn.outputs_folder, cn.mask_output_folder)

#Execute Calculcate Zonal Stats Annualized...
print("Step 4: Calculating Zonal Stats Annualized... \n")
zonal_stats_annualized(cn.tcl_folder, cn.input_folder, cn.annual_folder)

#Execute Zonal Stats Clean...
print("Step 5: Cleaning Zonal Stats... \n")
input_folders = []
for tile in cn.tile_list:
    input_folders.append(os.path.join(cn.outputs_folder, tile))
ZonalStatsClean(input_folders, cn.csv_folder)

#TODO: Export dataframe for annualized results