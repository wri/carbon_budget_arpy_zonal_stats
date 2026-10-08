import constants_and_names as cn
from funcs import zonal_stats_fire_annualized

# Calculate annual fire emissions zonal stats using TCLF rasters
print("Step 5: Calculating Annual Fire Emissions Zonal Stats... \n")
zonal_stats_fire_annualized(cn.tclf_clip_folder, cn.fluxes_folder, cn.mask_output_tcd_folder, cn.annual_folder)