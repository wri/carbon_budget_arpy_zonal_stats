import constants_and_names as cn
from funcs import zonal_stats_drivers

# Calculate zonal stats by driver for all flux rasters at each TCD threshold value
print("Step 3: Calculating Gross Flux Zonal Stats with TCD Masks... \n")
zonal_stats_drivers(cn.drivers_clip_folder, cn.fluxes_folder, cn.mask_output_tcd_folder, cn.outputs_folder)
