import os
import constants_and_names as cn
from funcs import zonal_stats_clean, zonal_stats_clean

#TODO: Export dataframe for annualized results

#Set the input folders and output csv folder
input_folders = []
for tile in cn.tile_list:
    input_folders.append(os.path.join(cn.outputs_folder, tile))
#input_folders.append(cn.annual_folder)

zonal_stats_clean(input_folders, cn.csv_folder)