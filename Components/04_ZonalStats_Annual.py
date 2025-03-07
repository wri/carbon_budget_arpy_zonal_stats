import constants_and_names as cn
from funcs import zonal_stats_annualized

# Calculate emissions for each year of tree cover loss using TCL rasters
zonal_stats_annualized(cn.tcl_clip_folder, cn.fluxes_folder, cn.mask_output_tcd_folder, cn.annual_folder)

