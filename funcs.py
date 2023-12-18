import os
import arcpy
import pandas as pd
import logging
import re
from subprocess import Popen, PIPE, STDOUT
import constants_and_names as cn

#TODO: Update process_annual_zonal_stats() so it calculates annual emissions from masked (0, 30, 75) tcl_clip rasters.
#TODO:
# Future Updates:
# Add Tree cover extent 2000 (ha), AGB stock (Mg), Emissions_soil_only_all gases (Mg CO2e), and TCL 2001-22(ha) stats

########################################################################################################################
# Functions to run modules
########################################################################################################################
def download_files():
    # Step 1: Checking to see if the AOIS folder exists and if it contains a shapefile
    print("Step 1.1: Checking to see if AOIS folder exists and contains a shapefile")
    check_aois(cn.aois_folder)

    # Step 2: Create Input folder and subfolder for each tile in tile_list
    print("Step 1.2: Creating Input folder structure")
    create_tile_folders(cn.tile_list, cn.input_folder)

    # Step 3: Create Mask folder with Inputs subfolder (gain, mangrove, pre-200 plantations, and tree cover density) and
            # Mask subfolder (folder for each tile in tile_list)
    print("Step 1.3: Creating Mask folder structure")
    create_subfolders([cn.mask_input_folder, cn.gain_folder, cn.mangrove_folder, cn.plantations_folder, cn.tcd_folder, cn.whrc_folder])
    create_tile_folders(cn.tile_list, cn.mask_output_folder)

    # Step 4: Create Output folder with Annual folder, CSV folder, and subfolder for each tile in tile_list
    print("Step 1.4: Creating Output folder structure")
    create_subfolders([cn.csv_folder, cn.annual_folder])
    create_tile_folders(cn.tile_list, cn.outputs_folder)

    # Step 5: Create TCL folder structure
    print("Step 1.5: Creating TCL folder structure")
    create_subfolders([cn.tcl_input_folder, cn.tcl_clip_folder, cn.tcl_mask_folder])

    # Step 6: Download emission/removal/netflux tiles (6 per tile) to Input folder
    print("Step 1.6: Downloading files for Input folder")
    s3_flexible_download(cn.tile_list, cn.gross_emis_forest_extent_s3_path, cn.gross_emis_forest_extent_s3_pattern, cn.input_folder)
    s3_flexible_download(cn.tile_list, cn.gross_emis_full_extent_s3_path, cn.gross_emis_full_extent_s3_pattern, cn.input_folder)
    s3_flexible_download(cn.tile_list, cn.gross_removals_forest_extent_s3_path, cn.gross_removals_forest_extent_s3_pattern, cn.input_folder)
    s3_flexible_download(cn.tile_list, cn.gross_removals_full_extent_s3_path, cn.gross_removals_full_extent_s3_pattern, cn.input_folder)
    s3_flexible_download(cn.tile_list, cn.netflux_forest_extent_s3_path, cn.netflux_forest_extent_s3_pattern, cn.input_folder)
    s3_flexible_download(cn.tile_list, cn.netflux_full_extent_s3_path, cn.netflux_full_extent_s3_pattern, cn.input_folder)

    # Step 7: Download Gain, Mangrove, Pre_2000_Plantations, TCD, and WHRC subfolders for each tile to Mask, Inputs subfolders
    print("Step 1.7: Downloading files for Mask/Inputs folder")
    s3_flexible_download(cn.tile_list, cn.gain_s3_path, cn.gain_s3_pattern, cn.gain_folder, cn.gain_local_pattern)
    s3_flexible_download(cn.tile_list, cn.mangrove_s3_path, cn.mangrove_s3_pattern, cn.mangrove_folder)
    s3_flexible_download(cn.tile_list, cn.plantation_s3_path, cn.plantation_s3_pattern, cn.plantations_folder)
    s3_flexible_download(cn.tile_list, cn.tcd_s3_path, cn.tcd_s3_pattern, cn.tcd_folder)
    s3_flexible_download(cn.tile_list, cn.whrc_s3_path, cn.whrc_s3_pattern, cn.whrc_folder)

    # Step 8: Download TCL tiles to TCL, Inputs folder
    print("Step 1.8: Downloading files for TCL/Inputs folder")
    s3_flexible_download(cn.tile_list, cn.loss_s3_path, cn.loss_s3_pattern, cn.tcl_input_folder)

def create_masks(tcd_tiles, gain_tiles, whrc_tiles, mangrove_tiles, plantation_tiles, tcd_threshold, gain, save_intermediates):
    # Get a list of tcd tiles in the tcd folder
    tcd_list = pathjoin_files_in_directory(tcd_tiles, '.tif')

    for tcd in tcd_list:
        raster_name = get_raster_name(tcd)
        tile_id = get_tile_id(raster_name)
        mask_tiles = os.path.join(cn.mask_output_folder, tile_id)

        process_raster(tile_id, tcd, gain_tiles, whrc_tiles, mangrove_tiles, plantation_tiles, mask_tiles, tcd_threshold, gain, save_intermediates)

def zonal_stats_masked(aois_folder, input_folder, outputs_folder, mask_outputs_folder):
    aoi_list = pathjoin_files_in_directory(aois_folder, '.shp')

    for aoi in aoi_list:
        aoi_name = get_raster_name(aoi)
        print(f"Now processing {aoi_name}: \n")

        country = get_country_id(aoi_name)
        tile_id = get_tile_id_from_country(country)

        raster_folder = os.path.join(input_folder, tile_id)
        mask_tiles = os.path.join(mask_outputs_folder, tile_id)
        output_folder = os.path.join(outputs_folder, tile_id)

        process_zonal_statistics(aoi, aoi_name, raster_folder, mask_tiles, output_folder)

def tcl_masked(tcl_clip_folder, mask_outputs_folder, tcl_mask_folder):
    print("Clipping TCL tiles to GADM boundaries")
    clip_tcl_to_gadm(cn.tcl_input_folder, cn.tcl_clip_folder)

    tcl_list = pathjoin_files_in_directory(tcl_clip_folder, '.tif')

    for tcl in tcl_list:
        tcl_name = get_raster_name(tcl)
        tcl_obj = arcpy.Raster(tcl)
        print(f"Now processing {tcl_name}.tif:")

        tile_id = get_tile_id(tcl)
        mask_folder = os.path.join(mask_outputs_folder, tile_id)
        mask_list = pathjoin_files_in_directory(mask_folder, '.tif')

        for mask in mask_list:
            mask_path = get_raster_name(mask)
            mask_name = mask_path.split("_", 2)[2]
            mask_obj = arcpy.Raster(mask)
            print(f'    Masking {tcl_name}.tif with mask: {mask_name}')

            # Check if spatial references and extents are the same
            if (tcl_obj.spatialReference.name == mask_obj.spatialReference.name):
                output_name = f'{tcl_name}_{mask_name}.tif'
                output_path = os.path.join(tcl_mask_folder, output_name)

                no_data_value = arcpy.Raster(mask_obj)
                mask_nodata = arcpy.sa.Mask(mask_obj, no_data_values=[no_data_value, 0])

                masked_raster = arcpy.sa.ExtractByMask(tcl_obj, mask_nodata, "INSIDE")
                masked_raster.save(output_path)
                print(f'    Successfully finished')

            else:
                print(f"    Spatial references do not match for {tcl_name}.tif and {mask_path}.tif")

def zonal_stats_annualized(tcl_folder, input_folder, annual_folder):
    tcl_list = pathjoin_files_in_directory(tcl_folder, '.tif')

    for tcl in tcl_list:
        tile_id = get_tile_id(tcl)
        tile_folder = os.path.join(input_folder, tile_id)

        tcl_name = get_raster_name(tcl)
        print(f"Now processing {tcl_name}:")

        process_annual_zonal_stats(tcl, tile_folder, annual_folder)

def process_annual_zonal_stats(tcl, raster_folder, output_folder):
    raster_list = [os.path.join(raster_folder, f) for f in os.listdir(raster_folder) if "emis" in f and f.endswith('tif')]

    for raster in raster_list:
        tcl_name = get_raster_name(tcl)
        raster_name = get_raster_name(raster)
        print(f'    Calculating zonal statistics for {raster_name}:')

        output_name = f"{tcl_name}_{raster_name}.dbf"
        output_path = os.path.join(output_folder, output_name)

        arcpy.gp.ZonalStatisticsAsTable_sa(tcl, "Value", raster, output_path, "DATA", "SUM")
        csv_file = f"{tcl_name}_{raster_name}.csv"
        arcpy.TableToTable_conversion(output_path, output_folder, csv_file)

def zonal_stats_clean(input_folders, csv_folder) -> object:
    # Initialize an empty data frame to store the data
    df = pd.DataFrame()
    for folder in input_folders:
        # Loop through the files in each folder
        for file in os.listdir(folder):
            if file.endswith(".csv"):
                # Load the csv file into a pandas data frame
                csv_df = pd.read_csv(os.path.join(folder, file))

                # Rename the "sum" field to the name of the file
                csv_df["Name"] = file

                #Define type of calc
                if "emis" in file:
                    type = "gross emissions"
                elif "removals" in file:
                    type = "gross removals"
                else:
                    type = "net flux"
                csv_df["Type"] = type

                #Define extent of calc
                if "forest_extent" in file:
                    extent = "forest extent"
                else:
                    extent = "full extent"
                csv_df["Extent"] = extent

                #Define tcd threshold
                tcd = re.match(r'.*tcd([0-9]+).*', file)
                if tcd is not None:
                    csv_df["Density"] = tcd.group(1)
                else:
                    csv_df["Density"] = 'NA'

                # Define mask of calc
                if "mangrove" in file:
                    mask = "tcd, gain, mangrove"
                elif "gain" in file:
                    mask = "tcd, gain"
                elif "tcd" in file:
                    mask = "tcd"
                else:
                    mask = "no mask"

                if "notPlantation" in file:
                    mask = f'{mask}, NOT plantation'

                csv_df["Mask"] = mask

                # Drop all other fields
                assert isinstance(csv_df, object)
                csv_df.drop([ 'OID_', 'COUNT', 'AREA'], axis=1, inplace=True)

                # Append the data to the main data frame
                df = pd.concat([df, csv_df], axis=0)

        # Print the resulting data frame to check the data
        print(df)

        # define the output location
        output_path = os.path.join(csv_folder,"final_output.csv")

        # Export the data frame as a CSV file
        df.to_csv(output_path, index=False)

    #TODO: Export dataframe for annualized results

#######################################################################################################################
# Utility functions
#######################################################################################################################
def check_aois(aois_folder):
    # Checking to see if the AOIS folder exists
    if os.path.isdir(aois_folder):
        print(f"    Success: {aois_folder} exists.")
        # Checking to see if the AOIS folder has any shapefiles
        aoi_list = pathjoin_files_in_directory(aois_folder, ".shp")
        if len(aoi_list) >= 1:
            print(f"    Success: {aois_folder} contains {len(aoi_list)} shapefiles.")
        else:
            raise Exception(f"  Failure: {aois_folder} does not contain a shapefile.")
    else:
        raise Exception(f"  Failure: {aois_folder} does not exist.")

def folder_check(folder):
    if os.path.isdir(folder):
        print(f"    Option 1 success: {folder} exists.")
    else:
        os.makedirs(folder)
        if os.path.isdir(folder):
            print(f"    Option 2 success: {folder} successfully created.")
        else:
            raise Exception(f"  Option 2 failure: {folder} could not be created.")

def create_tile_folders(tile_list, input_folder):
    for tile in tile_list:
        tile_id_folder = os.path.join(input_folder, tile)
        folder_check(tile_id_folder)

def create_subfolders(folder_list):
    for subfolder in folder_list:
        folder_check(subfolder)

def list_files_in_directory(directory, file_extension):
    return [f for f in os.listdir(directory) if f.endswith(file_extension)]

def pathjoin_files_in_directory(directory, file_extension):
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(file_extension)]

def get_tile_id(tile_name):
    tile_id = re.search("[0-9]{2}[A-Z][_][0-9]{3}[A-Z]", tile_name).group()
    return tile_id

def get_country_id(tile_name):
    country = re.search("[_][A-Z]{3}[_]", tile_name).group()
    country_id = country.split("_")[1]
    return country_id

def get_country_id_from_tile_id(tile_id):
    for key, value in cn.tile_dictionary.items():
        if value == tile_id:
            return key

def get_tile_id_from_country(country):
    for key, value in cn.tile_dictionary.items():
        if key == country:
            return value

def get_raster_name(raster):
    return os.path.splitext(os.path.basename(raster))[0]

def get_gadm_boundary(country):
    for f in pathjoin_files_in_directory(cn.aois_folder, ".shp"):
        if country in f:
            return f

def clip_to_gadm(country, input_raster, output_raster):
    clip_feature = get_gadm_boundary(country)
    no_data_value = arcpy.Raster(input_raster).noDataValue
    arcpy.management.Clip(input_raster, "#", output_raster, clip_feature, no_data_value, "ClippingGeometry")#, "MAINTAIN_EXTENT")
    print(f'    Saving {output_raster}')

def clip_tcl_to_gadm(input_folder, output_folder):
    print(f'    Option 1: Checking if clipped TCL tiles already exist...')
    tcl_list = list_files_in_directory(input_folder, ".tif")
    if len(tcl_list) >= 1:
        for raster in tcl_list:
            raster_name = get_raster_name(raster)
            tile_id = get_tile_id(raster)
            country = get_country_id_from_tile_id(tile_id)

            input_raster = os.path.join(input_folder, raster)
            output_raster = os.path.join(output_folder, f'{raster_name}_{country}_clip.tif')

            if os.path.exists(output_raster):
                print(f"    Option 1 success: Tile {output_raster} already exists.")
            else:
                print(f' Option 1 failure: Tile {output_raster} does not already exists."')
                print(f' Option 2: Clipping TCL tile to GADM boundary')
                clip_to_gadm(country, input_raster, output_raster)
                if os.path.exists(output_raster):
                    print(f'  Option 2 success: Tile {output_raster} successfully created')
                else:
                    print(f'  Option 2 failure: Tile {output_raster} was not successfully created')
    else:
        print(f' Option 1 failure: {input_folder} does not contain any TCL tiles. Make sure TCL tiles have been downloaded.')


def or_mask_logic(raster1, raster2, raster1_value=None, raster2_value=None):
    if raster1_value:
        raster1_mask = arcpy.sa.Con(arcpy.Raster(raster1) > raster1_value, 1, 0)
    else:
        raster1_mask = raster1
    if raster2_value:
        raster2_mask = arcpy.sa.Con(arcpy.Raster(raster2) > raster2_value, 1, 0)
    else:
        raster2_mask = raster2
    r1_and_r2_mask = arcpy.ia.Merge([raster2_mask, raster1_mask], "SUM")
    output_mask = arcpy.sa.Con(arcpy.Raster(r1_and_r2_mask) > 0, 1, 0)
    return output_mask


def and_mask_logic(raster1, raster2, raster1_value=None, raster2_value=None):
    if raster1_value:
        raster1_mask = arcpy.sa.Con(arcpy.Raster(raster1) > raster1_value, 1, 0)
    else:
        raster1_mask = raster1
    if raster2_value:
        raster2_mask = arcpy.sa.Con(arcpy.Raster(raster2) > raster2_value, 1, 0)
    else:
        raster2_mask = raster2
    r1_and_r2_mask = arcpy.sa.Times(raster1_mask, raster2_mask)
    output_mask = arcpy.sa.Con(arcpy.Raster(r1_and_r2_mask) > 0, 1, 0)
    return output_mask

def process_raster(tile_id, tcd, gain_tiles, whrc_tiles, mangrove_tiles, plantation_tiles, mask_tiles, tcd_threshold, gain, save_intermediates):
    #Paths to Mask, Input files
    gain_raster_path = os.path.join(gain_tiles, f'{tile_id}_{cn.gain_local_pattern}.tif')
    whrc_raster_path = os.path.join(whrc_tiles, f'{tile_id}_{cn.whrc_s3_pattern}.tif')
    mangrove_raster_path = os.path.join(mangrove_tiles, f'{tile_id}_{cn.mangrove_s3_pattern}.tif')
    plantation_raster_path = os.path.join(plantation_tiles, f'{tile_id}_{cn.plantation_s3_pattern}.tif')

    print(f'Creating masks for {tile_id}:')

    for tcd_val in tcd_threshold:
        # Conditional logic for where TCD AND biomass
        tcd_whrc_mask = and_mask_logic(tcd, whrc_raster_path, tcd_val, 0)
        mask_path_tcd = os.path.join(mask_tiles, f'{tile_id}_tcd{tcd_val}')

        if gain == True:
            # Conditional logic for TCD AND biomass OR gain
            tcd_gain_mask = or_mask_logic(gain_raster_path, tcd_whrc_mask, 0)
            mask_path_tcd_gain = f'{mask_path_tcd}_gain'
        else:
            tcd_gain_mask = tcd_whrc_mask
            mask_path_tcd_gain = mask_path_tcd

        if os.path.exists(mangrove_raster_path):
            # Conditional logic for TCD AND biomass OR gain OR mangrove
            tcd_gain_mangrove_mask = or_mask_logic(mangrove_raster_path, tcd_gain_mask, 0)
            mask_path_tcd_gain_mangrove = f'{mask_path_tcd_gain}_mangrove'
        else:
            tcd_gain_mangrove_mask = tcd_gain_mask
            mask_path_tcd_gain_mangrove = mask_path_tcd_gain

        if os.path.exists(plantation_raster_path):
            # Read in the plantation raster and mask before saving each intermediate
            plantation_raster = arcpy.sa.IsNull(arcpy.Raster(plantation_raster_path))

            if save_intermediates == True:

                # Conditional logic for TCD AND biomass NOT Pre-2000 Plantation
                tcd_noplantation_mask = and_mask_logic(tcd_whrc_mask, plantation_raster)
                mask_path_tcd_noplantation = f'{mask_path_tcd}_notPlantation'

                # Saving the tcd_noplantation mask
                print(f'    Saving {mask_path_tcd_noplantation}.tif')
                tcd_noplantation_mask.save(f'{mask_path_tcd_noplantation}.tif')

                # Conditional logic for TCD AND biomass OR gain NOT Pre-2000 Plantation
                tcd_gain_noplantation_mask = and_mask_logic(tcd_gain_mask, plantation_raster)
                mask_path_tcd_gain_noplantation = f'{mask_path_tcd_gain}_notPlantation'

                # Saving the tcd_gain_noplantation mask
                print(f'    Saving {mask_path_tcd_gain_noplantation}.tif')
                tcd_gain_noplantation_mask.save(f'{mask_path_tcd_gain_noplantation}.tif')

            # Conditional logic for TCD AND biomass OR gain OR mangrove NOT Pre-2000 Plantation
            tcd_gain_mangrove_noplantation_mask = and_mask_logic(tcd_gain_mangrove_mask, plantation_raster)
            mask_path_tcd_gain_mangrove_noplantation = f'{mask_path_tcd_gain_mangrove}_notPlantation'

            # Saving the tcd_gain_mangrove_noplantation mask
            print(f'    Saving {mask_path_tcd_gain_mangrove_noplantation}.tif')
            tcd_gain_mangrove_noplantation_mask.save(f'{mask_path_tcd_gain_mangrove_noplantation}.tif')

        else:
            if save_intermediates == True:
                # Saving the tcd mask
                print(f'    Saving {mask_path_tcd}.tif')
                tcd_whrc_mask.save(f'{mask_path_tcd}.tif')

                # Saving the tcd_gain mask
                print(f'    Saving {mask_path_tcd_gain}.tif')
                tcd_gain_mask.save(f'{mask_path_tcd_gain}.tif')

            # Saving tcd_gain_mangrove mask
            print(f'    Saving {mask_path_tcd_gain_mangrove}.tif')
            tcd_gain_mangrove_mask.save(f'{mask_path_tcd_gain_mangrove}.tif')

def process_zonal_statistics(aoi, aoi_name, raster_folder, mask_tiles, output_folder):
    raster_list = pathjoin_files_in_directory(raster_folder, '.tif')
    mask_list = pathjoin_files_in_directory(mask_tiles, '.tif')

    for raster in raster_list:
        raster_name = get_raster_name(raster)
        raster_obj = arcpy.Raster(raster)
        print(f'Calculating zonal statistics for {raster_name}.tif')

        for mask in mask_list:
            mask_path = get_raster_name(mask)
            mask_name = mask_path.split("_", 2)[2]
            mask_obj = arcpy.Raster(mask)

            # Check if spatial references and extents are the same
            if (raster_obj.extent == mask_obj.extent and raster_obj.spatialReference.name == mask_obj.spatialReference.name):
                # Create a name for the output table by concatenating the AOI name and raster name
                output_name = "{}_{}.dbf".format(aoi_name, str(raster_name) + "_" + str(mask_name))
                output_path = os.path.join(output_folder, output_name)

                print(f'    Masking {raster_name}.tif with {mask_name}.tif')
                masked_raster = arcpy.sa.Times(raster_obj, mask_obj)
                arcpy.gp.ZonalStatisticsAsTable_sa(aoi, "GID_0", masked_raster, output_path, "DATA", "SUM")

                # Convert each output to csv
                csv_file = "{}_{}.csv".format(aoi_name, str(raster_name) + "_" + str(mask_name))
                arcpy.TableToTable_conversion(output_path, output_folder, csv_file)
                print(f'    Successfully finished')

            else:
                print(f"Spatial references or extents do not match for {raster} and {mask_name}")

def load_and_process_csv(file_path, file_name):
    csv_df = pd.read_csv(file_path)

#######################################################################################################################
# AWS S3 file download utilities
#######################################################################################################################

def s3_flexible_download(tile_id_list, s3_dir, s3_pattern, local_dir, local_pattern = ''):

    # Creates a full download name (path and file)
    for tile_id in tile_id_list:
        if s3_pattern in [cn.tcd_s3_pattern, cn.loss_s3_pattern]:
            source = f'{s3_dir}{s3_pattern}_{tile_id}.tif'
        elif s3_pattern in [cn.gain_s3_pattern]:
            source = f'{s3_dir}{tile_id}.tif'
        else:  # For every other type of tile
            source = f'{s3_dir}{tile_id}_{s3_pattern}.tif'

        if s3_pattern in [cn.gross_emis_forest_extent_s3_pattern, cn.gross_emis_full_extent_s3_pattern, cn.gross_removals_forest_extent_s3_pattern, cn.gross_removals_full_extent_s3_pattern, cn.netflux_forest_extent_s3_pattern, cn.netflux_full_extent_s3_pattern]:
            dir = os.path.join(local_dir, tile_id)
        else:
            dir = local_dir

        s3_file_download(source, dir, local_pattern)

def s3_file_download(source, dest, pattern=''):
    # Retrieves the s3 directory and name of the tile from the full path name
    dir = get_tile_dir(source)
    file_name = get_tile_name(source)

    try:
        tile_id = get_tile_id(file_name)
    except:
        pass

    # Special download procedures for tree cover gain because the tiles have no pattern, just an ID.
    # Tree cover gain tiles are renamed as their downloaded to get a pattern added to them.
    if dir == cn.gain_s3_path[:-1]: # Delete last character of gain_dir because it has the terminal / while dir does not have terminal /
        local_file_name = f'{tile_id}_{pattern}.tif'
        print(f'    Option 1: Checking if {local_file_name} is already downloaded...')
        if os.path.exists(os.path.join(dest, local_file_name)):
            print(f'    Option 1 success: {os.path.join(dest, local_file_name)} already downloaded', "\n")
            return
        else:
            print(f'    Option 1 failure: {local_file_name} is not already downloaded.')
            print(f'    Option 2: Checking for tile {source} on s3...')

            # If the tile isn't already downloaded, download is attempted
            # source = os.path.join(dir, file_name)
            source = f'{dir}/{file_name}'
            local_folder = os.path.join(dest, local_file_name)

            # cmd = ['aws', 's3', 'cp', source, dest, '--no-sign-request', '--only-show-errors']
            cmd = ['aws', 's3', 'cp', source, local_folder,
                   '--request-payer', 'requester', '--only-show-errors']
            log_subprocess_output_full(cmd)

            if os.path.exists(os.path.join(dest, local_file_name)):
                print_log(f'    Option 2 success: Tile {source} found on s3 and downloaded', "\n")
                return
            else:
                print_log(
                    f'  Option 2 failure: Tile {source} not found on s3. Tile not found but it seems it should be. Check file paths and names.', "\n")

    # All other tiles besides tree cover gain
    else:
        print_log(f'    Option 1: Checking if {file_name} is already downloaded...')
        if os.path.exists(os.path.join(dest, file_name)):
            print_log(f'    Option 1 success: {os.path.join(dest, file_name)} already downloaded', "\n")
            return
        else:
            print_log(f'    Option 1 failure: {file_name} is not already downloaded.')
            print_log(f'    Option 2: Checking for tile {source} on s3...')

            # If the tile isn't already downloaded, download is attempted
            #source = os.path.join(dir, file_name)
            source = f'{dir}/{file_name}'

            # cmd = ['aws', 's3', 'cp', source, dest, '--no-sign-request', '--only-show-errors']
            cmd = ['aws', 's3', 'cp', source, dest, '--only-show-errors']
            log_subprocess_output_full(cmd)
            if os.path.exists(os.path.join(dest, file_name)):
                print_log(f'    Option 2 success: Tile {source} found on s3 and downloaded', "\n")
                return
            else:
                print_log(f'    Option 2 failure: Tile {source} not found on s3. Tile not found but it seems it should be. Check file paths and names.', "\n")

# Gets the directory of the tile
def get_tile_dir(tile):
    tile_dir = os.path.split(tile)[0]
    return tile_dir

def get_tile_name(tile):
    tile_name = os.path.split(tile)[1]
    return tile_name

def log_subprocess_output_full(cmd):
    # Solution for adding subprocess output to log is from https://stackoverflow.com/questions/21953835/run-subprocess-and-print-output-to-logging
    process = Popen(cmd, stdout=PIPE, stderr=STDOUT)
    pipe = process.stdout
    with pipe:
        # Reads all the output into a string
        for full_out in iter(pipe.readline, b''):  # b"\n"-separated lines
            # Separates the string into an array, where each entry is one line of output
            line_array = full_out.splitlines()
            # For reasons I don't know, the array is backwards, so this prints it out in reverse (i.e. correct) order
            for line in reversed(line_array):
                logging.info(line.decode(
                    "utf-8"))  # https://stackoverflow.com/questions/37016946/remove-b-character-do-in-front-of-a-string-literal-in-python-3, answer by krock
                print(line.decode(
                    "utf-8"))  # https://stackoverflow.com/questions/37016946/remove-b-character-do-in-front-of-a-string-literal-in-python-3, answer by krock

def print_log(*args):
    # Empty string
    full_statement = str(object='')
    # Concatenates all individuals strings to the complete line to print
    for arg in args:
        full_statement = full_statement + str(arg) + " "
    logging.info(full_statement)
    # Prints to console
    print("LOG: " + full_statement)

