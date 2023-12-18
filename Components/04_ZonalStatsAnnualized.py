import constants_and_names as cn
from funcs import zonal_stats_annualized

#Set the tcl_clip folder, input folders with per pixel removal/emissions/netflux rasters, and annual output folder
zonal_stats_annualized(cn.tcl_mask_folder, cn.input_folder, cn.annual_folder)

