import arcpy
import os

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"U:\eglen\Data\CarbonFlux_QA_2023"

tcd_tiles = r"U:\eglen\Data\CarbonFlux_QA_2023\Mask\TCD"
gain_tiles = r"U:\eglen\Data\CarbonFlux_QA_2023\Mask\Gain"
whrc_tiles = r"U:\eglen\Data\CarbonFlux_QA_2023\Mask\WHRC"
mangrove_tiles = r"U:\eglen\Data\CarbonFlux_QA_2023\Mask\Mangrove"
mask_tiles = r"U:\eglen\Data\CarbonFlux_QA_2023\Mask\Mask"

TDC_threshold = 30
gain = True

# Get a list of rasters in the raster folder
tcd_list = [os.path.join(tcd_tiles, f) for f in os.listdir(tcd_tiles) if f.endswith('.tif')]
print(tcd_list)

# Loop through each raster and calculate zonal statistics as table
for raster in tcd_list:
    # Extract the name of the raster from the file path
    raster_name = os.path.splitext(os.path.basename(raster))[0]
    # print(raster_name)
    tile_id = raster_name.split("_", 3)[3]
    # print(tile_id)
    gain_raster = os.path.join(gain_tiles, str(tile_id + '_gain.tif'))
    mask_path_tcd = os.path.join(mask_tiles, str(tile_id + '_tcd.tif'))
    mask_path_tcd_gain = os.path.join(mask_tiles, str(tile_id + '_tcd_gain.tif'))
    print('Creating masks for ' + tile_id + ": \n")

    # Conditional logic for TCD
    tcd_raster = arcpy.sa.Con(arcpy.Raster(raster) > 30, 1, 0)
    # tcd_raster.save(mask_path_tcd)

    # Conditional logic for Gain
    gain_raster: object = arcpy.sa.Con(arcpy.Raster(gain_raster) > 0, 1, 0)

    # Add raster calculator logic...
    output_plus = arcpy.sa.Plus(gain_raster, tcd_raster)
    output_raster = arcpy.sa.Con(arcpy.Raster(output_plus) > 0, 1, 0)

    output_raster.save(mask_path_tcd_gain)

TDC_threshold = 30
gain = False

# Get a list of rasters in the raster folder
tcd_list = [os.path.join(tcd_tiles, f) for f in os.listdir(tcd_tiles) if f.endswith('.tif')]
print(tcd_list)

# Loop through each raster and calculate zonal statistics as table
for raster in tcd_list:
    # Extract the name of the raster from the file path
    raster_name = os.path.splitext(os.path.basename(raster))[0]
    # print(raster_name)
    tile_id = raster_name.split("_", 3)[3]
    # print(tile_id)
    gain_raster = os.path.join(gain_tiles, str(tile_id + '_gain.tif'))
    mangrove_raster = os.path.join(mangrove_tiles, str(tile_id + '_mangrove_agb_t_ha_2000_rewindow.tif'))
    whrc_raster = os.path.join(whrc_tiles, str(tile_id + '_t_aboveground_biomass_ha_2000.tif'))

    mask_path_tcd = os.path.join(mask_tiles, str(tile_id + '_tcd.tif'))
    mask_path_tcd_gain = os.path.join(mask_tiles, str(tile_id + '_tcd_gain.tif'))
    print('Creating masks for ' + tile_id + ": \n")

    # Conditional logic for TCD
    tcd_raster = arcpy.sa.Con(arcpy.Raster(raster) > 30, 1, 0)
    # tcd_raster.save(mask_path_tcd)

    tcd_raster.save(mask_path_tcd)


