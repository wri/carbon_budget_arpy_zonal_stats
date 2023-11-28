import os
import arcpy
import pandas as pd

TCD_THRESHOLD = 30
GAIN_FLAG = True
MASK_PATHS = {"IDN": "00N_110E", "GMB": "20N_20W"}

def get_tile_id(raster_name):
    return raster_name.split("_", 3)[3]

def get_mask_tiles(tile_id):
    if "00N_110E" in tile_id:
        return os.path.join(arcpy.env.workspace, "Mask", "Mask", "00N_110E")
    else:
        return os.path.join(arcpy.env.workspace, "Mask", "Mask", "20N_20W")

def process_raster(raster, gain_tiles, mangrove_tiles, whrc_tiles, mask_tiles):
    tile_id = get_tile_id(os.path.splitext(os.path.basename(raster))[0])

    gain_raster_path = os.path.join(gain_tiles, f'{tile_id}_gain.tif')
    mangrove_raster_path = os.path.join(mangrove_tiles, f'{tile_id}_mangrove_agb_t_ha_2000_rewindow.tif')
    whrc_raster_path = os.path.join(whrc_tiles, f'{tile_id}_t_aboveground_biomass_ha_2000.tif')

    mask_path_tcd_gain = os.path.join(mask_tiles, f'{tile_id}_tcd_gain.tif')
    print(f'Creating masks for {tile_id}: \n')

    tcd_raster = arcpy.sa.Con(arcpy.Raster(raster) > TCD_THRESHOLD, 1, 0)
    gain_raster = arcpy.sa.Con(arcpy.Raster(gain_raster_path) > 0, 1, 0)
    whrc_raster = arcpy.sa.Con(arcpy.Raster(whrc_raster_path) > 0, 1, 0)
    mangrove_raster = arcpy.sa.Con(arcpy.Raster(mangrove_raster_path) > 0, 1, 0)

    output_raster = arcpy.sa.Times(tcd_raster, whrc_raster)
    output_raster = arcpy.sa.Plus(output_raster, gain_raster)
    output_raster = arcpy.sa.Plus(output_raster, mangrove_raster)
    output_raster = arcpy.sa.Con(output_raster > 0, 1, 0)

    output_raster.save(mask_path_tcd_gain)

def create_masks():
    mask_inputs = os.path.join(arcpy.env.workspace, "Mask", "Inputs")

    tcd_tiles = os.path.join(mask_inputs, "TCD")
    gain_tiles = os.path.join(mask_inputs, "Gain")
    whrc_tiles = os.path.join(mask_inputs, "WHRC")
    mangrove_tiles = os.path.join(mask_inputs, "Mangrove")

    tcd_list = [os.path.join(tcd_tiles, f) for f in os.listdir(tcd_tiles) if f.endswith('.tif')]
    print(tcd_list)

    for raster in tcd_list:
        tile_id = get_tile_id(os.path.splitext(os.path.basename(raster))[0])
        mask_tiles = get_mask_tiles(tile_id)
        process_raster(raster, gain_tiles, mangrove_tiles, whrc_tiles, mask_tiles)

def list_files_in_directory(directory, file_extension):
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(file_extension)]

def process_zonal_statistics(aoi, raster_folder, output_folder):
    raster_list = list_files_in_directory(raster_folder, '.tif')

    for raster in raster_list:
        raster_name = os.path.splitext(os.path.basename(raster))[0]
        print(f'Calculating zonal statistics for {raster_name}: \n')

        output_name = f"{os.path.splitext(os.path.basename(aoi))[0]}_{raster_name}.dbf"
        output_path = os.path.join(output_folder, output_name)

        arcpy.gp.ZonalStatisticsAsTable_sa(aoi, "GID_0", raster, output_path, "DATA", "SUM")
        csv_file = f"{os.path.splitext(os.path.basename(aoi))[0]}_{raster_name}.csv"
        arcpy.TableToTable_conversion(output_path, output_folder, csv_file)

def zonal_stats(input_folder):
    aoi_list = list_files_in_directory(input_folder, '.shp')

    for aoi in aoi_list:
        aoi_name = os.path.splitext(os.path.basename(aoi))[0]
        print(f"Now processing {aoi_name}: \n")

        if "IDN" in aoi_name:
            raster_folder = os.path.join(arcpy.env.workspace, "Input", "00N_110E")
            output_folder = os.path.join(arcpy.env.workspace, "Outputs", "00N_110E")
        else:
            raster_folder = os.path.join(arcpy.env.workspace, "Input", "20N_20W")
            output_folder = os.path.join(arcpy.env.workspace, "Outputs", "20N_20W")

        process_zonal_statistics(aoi, raster_folder, output_folder)

def zonal_stats_masked(input_folder):
    aoi_list = list_files_in_directory(input_folder, '.shp')

    for aoi in aoi_list:
        aoi_name = os.path.splitext(os.path.basename(aoi))[0]
        print(f"Now processing {aoi_name}: \n")

        if "IDN" in aoi_name:
            raster_folder = os.path.join(arcpy.env.workspace, "Input", "00N_110E")
            output_folder = os.path.join(arcpy.env.workspace, "Outputs", "00N_110E")
            mask_tiles = os.path.join(arcpy.env.workspace, "Mask", "Mask", "00N_110E")
        else:
            raster_folder = os.path.join(arcpy.env.workspace, "Input", "20N_20W")
            output_folder = os.path.join(arcpy.env.workspace, "Outputs", "20N_20W")
            mask_tiles = os.path.join(arcpy.env.workspace, "Mask", "Mask", "20N_20W")

        raster_list = list_files_in_directory(raster_folder, '.tif')
        mask_list = list_files_in_directory(mask_tiles, '.tif')

        for raster in raster_list:
            raster_obj = arcpy.Raster(raster)

            for mask in mask_list:
                mask_obj = arcpy.Raster(mask)

                # Check if spatial references and extents are the same
                if (raster_obj.extent == mask_obj.extent and
                        raster_obj.spatialReference.name == mask_obj.spatialReference.name):

                    masked_raster = arcpy.sa.Times(raster_obj, mask_obj)
                    # ... [rest of your code] ...
                else:
                    print(f"Spatial references or extents do not match for {raster} and {mask}")

def process_annual_zonal_stats(aoi, raster_folder, output_folder):
    raster_list = list_files_in_directory(raster_folder, 'emis.tif')

    for raster in raster_list:
        raster_name = os.path.splitext(os.path.basename(raster))[0]
        print(f'Calculating zonal statistics for {raster_name}: \n')

        output_name = f"{os.path.splitext(os.path.basename(aoi))[0]}_{raster_name}.dbf"
        output_path = os.path.join(output_folder, output_name)

        arcpy.gp.ZonalStatisticsAsTable_sa(aoi, "Value", raster, output_path, "DATA", "SUM")
        csv_file = f"{os.path.splitext(os.path.basename(aoi))[0]}_{raster_name}.csv"
        arcpy.TableToTable_conversion(output_path, output_folder, csv_file)

def zonal_stats_annualized(input_folder):
    aoi_list = list_files_in_directory(input_folder, 'clip.tif')

    for aoi in aoi_list:
        aoi_name = os.path.splitext(os.path.basename(aoi))[0]
        print(f"Now processing {aoi_name}: \n")

        if "IDN" in aoi_name:
            raster_folder = os.path.join(arcpy.env.workspace, "Input", "00N_110E")
            output_folder = os.path.join(arcpy.env.workspace, "Outputs", "Annual")
        else:
            raster_folder = os.path.join(arcpy.env.workspace, "Input", "20N_20W")
            output_folder = os.path.join(arcpy.env.workspace, "Outputs", "Annual")

        process_annual_zonal_stats(aoi, raster_folder, output_folder)

def load_and_process_csv(file_path, file_name):
    csv_df = pd.read_csv(file_path)

    # Assigning attributes based on file name
    csv_df["Name"] = file_name
    csv_df["Type"] = "gross emissions" if "emis" in file_name else "gross removals" if "removals" in file_name else "net flux"
    csv_df["Extent"] = "forest extent" if "forest" in file_name else "full extent"
    csv_df["Mask"] = "tcd and gain" if "tcd_gain" in file_name else "tcd" if "_tcd." in file_name else "no mask"

    # Dropping unnecessary columns
    csv_df.drop(['OID_', 'COUNT', 'AREA'], axis=1, inplace=True)
    return csv_df

def zonal_stats_clean(input_folders):
    df = pd.DataFrame()

    for folder in input_folders:
        for file in os.listdir(folder):
            if file.endswith(".csv"):
                file_path = os.path.join(folder, file)
                csv_df = load_and_process_csv(file_path, file)
                df = pd.concat([df, csv_df], axis=0)

    print(df)

    output_path = os.path.join(arcpy.env.workspace, "Outputs", "CSV", "output.csv")
    df.to_csv(output_path, index=False)

