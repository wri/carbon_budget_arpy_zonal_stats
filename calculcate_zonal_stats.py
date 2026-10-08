import constants_and_names as cn
from funcs import download_files, create_masks, zonal_stats_drivers, zonal_stats_annualized, zonal_stats_fire_annualized, zonal_stats_clean

# Create folder structure and download files
print("Step 1: Downloading Files... \n")
download_files()

# Create model extent masks for specified TCD thresholds
print("Step 2: Creating TCD Masks... \n")
create_masks(cn.tcd_threshold)

# Calculate zonal stats by driver for all flux rasters at each TCD threshold value
print("Step 3: Calculating Gross Flux Zonal Stats with TCD Masks... \n")
zonal_stats_drivers(cn.drivers_clip_folder, cn.fluxes_folder, cn.mask_output_tcd_folder, cn.outputs_folder)

# Calculate annual emissions zonal stats using TCL rasters
print("Step 4: Calculating Annual Emissions Zonal Stats... \n")
zonal_stats_annualized(cn.tcl_clip_folder, cn.fluxes_folder, cn.mask_output_tcd_folder, cn.annual_folder)

# Calculate annual fire emissions zonal stats using TCLF rasters
print("Step 5: Calculating Annual Fire Emissions Zonal Stats... \n")
zonal_stats_fire_annualized(cn.tclf_clip_folder, cn.fluxes_folder, cn.mask_output_tcd_folder, cn.annual_folder)

# Combine and clean gross and annual zonal stats output into final csv
print("Step 6: Cleaning Zonal Stats... \n")
zonal_stats_clean()