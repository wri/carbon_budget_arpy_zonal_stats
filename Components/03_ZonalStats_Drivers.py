import constants_and_names as cn
from funcs import zonal_stats_drivers

# Calculate zonal stats for all input rasters at each tcd threshold value
zonal_stats_drivers(cn.drivers_clip_folder, cn.fluxes_folder, cn.mask_output_tcd_folder, cn.outputs_folder)
