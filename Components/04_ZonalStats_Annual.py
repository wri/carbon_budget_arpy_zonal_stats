import constants_and_names as cn
from funcs import zonal_stats_annualized

# Calculate annual emissions zonal stats using TCL rasters
print("Step 4: Calculating Annual Emissions Zonal Stats... \n")
zonal_stats_annualized(cn.tcl_clip_folder, cn.fluxes_folder, cn.mask_output_tcd_folder, cn.annual_folder)

