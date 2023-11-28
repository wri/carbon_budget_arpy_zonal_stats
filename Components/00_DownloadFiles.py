import arcpy
import os
from funcs import s3_file_download
#TODO: DOWNLOAD GADM BOUNDARY SHAPEFILES TO AOIS FOLDER?

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\GIS\carbon_model\CarbonFlux_QA_2023"




#Step 1: Create Input folder if it does not exist

#Step 2: Create a subfolder in Input folder for each tile in tile_list

#Step 3: Create Mask folder and Inputs and Mask subfolders

#Step 4: Create Gain, Mangrove, Pre_2000_Plantations, TCD, and WHRC subfolders in Mask, Inputs subfolder

#Step 5: Create a subfolder in Mask, Mask subfolder for each tile in tile_list

#TODO: Update code so that the mask output gets written to the tile folder rather than the Mask, Mask folder

#Step 6: Create Outputs folder and CSV subfolder

#TODO: Add annual subfolder to outputs folder?

#Step 7: Create a subfolder in Outputs folder for each tile in tile_list

#Step 8: Create TCL folder

#TODO: Where are these clipped rasters coming from?

#Step 9: Download emission/removal/netflux tiles (6 per tile) to Input folder

#Step 10: Download Gain, Mangrove, Pre_2000_Plantations, TCD, and WHRC subfolders for each tile to Mask, Inputs subfolder

