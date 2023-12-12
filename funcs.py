import os
import arcpy
import pandas as pd
import logging
import re
from subprocess import Popen, PIPE, STDOUT
import constants_and_names as cn

def DownloadFiles():
    # Step 1: Checking to see if the AOIS folder exists and if it contains a shapefile
    print("Step 0.1: Checking to see if AOIS folder exists and contains a shapefile")
    if os.path.isdir(cn.aois_folder):
        print(f"    Success: {cn.aois_folder} exists.")
        # Checking to see if the AOIS folder has any shapefiles
        aoi_list = [os.path.join(cn.aois_folder, f) for f in os.listdir(cn.aois_folder) if f.endswith('.shp')]
        if len(aoi_list) >= 1:
            print(f"    Success: {cn.aois_folder} contains {len(aoi_list)} shapefiles.")
        else:
            raise Exception(f"  Failure: {cn.aois_folder} does not contain a shapefile.")
    else:
        raise Exception(f"  Failure: {cn.aois_folder} does not exist.")

    # Step 2: Create Input folder and subfolder for each tile in tile_list
    print("Step 0.2: Creating Input folder structure")
    for tile in cn.tile_list:
        tile_id_folder = os.path.join(cn.input_folder, tile)
        folder_check(tile_id_folder)

    # Step 3: Create Mask folder with Inputs folder (contains gain, mangrove, pre-200 plantations, and tree cover density subfolders) and Mask folder (contains subfolders for each tile in tile_list)
    print("Step 0.3: Creating Mask folder structure")
    for subfolder in [cn.mask_input_folder, cn.gain_folder, cn.mangrove_folder, cn.plantations_folder, cn.tcd_folder,
                      cn.whrc_folder]:
        folder_check(subfolder)
    for tile in cn.tile_list:
        tile_id_folder = os.path.join(cn.mask_output_folder, tile)
        folder_check(tile_id_folder)

    # Step 4: Create Output folder with Annual folder, CSV folder, and subfolder for each tile in tile_list
    print("Step 0.4: Creating Output folder structure")
    for subfolder in [cn.csv_folder, cn.annual_folder]:
        folder_check(subfolder)
    for tile in cn.tile_list:
        tile_id_folder = os.path.join(cn.outputs_folder, tile)
        folder_check(tile_id_folder)

    # Step 5: Create TCL folder structure
    print("Step 0.5: Creating TCL folder structure")
    folder_check(cn.tcl_folder)
    # TODO: Where are these clipped rasters coming from?

    # Step 6: Download emission/removal/netflux tiles (6 per tile) to Input folder
    print("Step 0.6: Downloading files for Input folder")
    s3_flexible_download(cn.tile_list, cn.gross_emis_forest_extent_s3_path, cn.gross_emis_forest_extent_s3_pattern,
                         cn.input_folder)
    s3_flexible_download(cn.tile_list, cn.gross_emis_full_extent_s3_path, cn.gross_emis_full_extent_s3_pattern,
                         cn.input_folder)
    s3_flexible_download(cn.tile_list, cn.gross_removals_forest_extent_s3_path,
                         cn.gross_removals_forest_extent_s3_pattern, cn.input_folder)
    s3_flexible_download(cn.tile_list, cn.gross_removals_full_extent_s3_path, cn.gross_removals_full_extent_s3_pattern,
                         cn.input_folder)
    s3_flexible_download(cn.tile_list, cn.netflux_forest_extent_s3_path, cn.netflux_forest_extent_s3_pattern,
                         cn.input_folder)
    s3_flexible_download(cn.tile_list, cn.netflux_full_extent_s3_path, cn.netflux_full_extent_s3_pattern,
                         cn.input_folder)

    # Step 7: Download Gain, Mangrove, Pre_2000_Plantations, TCD, and WHRC subfolders for each tile to Mask, Inputs subfolders
    print("Step 0.6: Downloading files for Mask/Inputs folder")
    s3_flexible_download(cn.tile_list, cn.gain_s3_path, cn.gain_s3_pattern, cn.gain_folder, cn.gain_local_pattern)
    s3_flexible_download(cn.tile_list, cn.mangrove_s3_path, cn.mangrove_s3_pattern, cn.mangrove_folder)
    s3_flexible_download(cn.tile_list, cn.plantation_s3_path, cn.plantation_s3_pattern, cn.plantations_folder)
    s3_flexible_download(cn.tile_list, cn.tcd_s3_path, cn.tcd_s3_pattern, cn.tcd_folder)
    s3_flexible_download(cn.tile_list, cn.whrc_s3_path, cn.whrc_s3_pattern, cn.whrc_folder)

    #TODO: Step 8: Download TCL folder tiles

def create_masks(tcd_tiles, gain_tiles, whrc_tiles, mangrove_tiles, plantation_tiles, tcd_threshold, gain):
    # Get a list of rasters in the raster folder
    tcd_list = [os.path.join(tcd_tiles, f) for f in os.listdir(tcd_tiles) if f.endswith('.tif')]

    for raster in tcd_list:
        raster_name = os.path.splitext(os.path.basename(raster))[0]
        tile_id = get_tile_id(raster_name)
        mask_tiles = os.path.join(cn.mask_output_folder, tile_id)

        process_raster(raster, gain_tiles, whrc_tiles, mangrove_tiles, plantation_tiles, mask_tiles, tcd_threshold, gain)

def get_tile_id(raster_name):
    return raster_name.split("_", 3)[3]

def process_raster(raster, gain_tiles, whrc_tiles, mangrove_tiles, plantation_tiles, mask_tiles, tcd_threshold, gain):
    tile_id = get_tile_id(os.path.splitext(os.path.basename(raster))[0])

    #Paths to Mask, Input files
    gain_raster_path = os.path.join(gain_tiles, f'{tile_id}_{cn.gain_local_pattern}.tif')
    whrc_raster_path = os.path.join(whrc_tiles, f'{tile_id}_{cn.whrc_s3_pattern}.tif')
    mangrove_raster_path = os.path.join(mangrove_tiles, f'{tile_id}_{cn.mangrove_s3_pattern}.tif')
    plantation_raster_path = os.path.join(plantation_tiles, f'{tile_id}_{cn.plantation_s3_pattern}.tif')

    print(f'Creating masks for {tile_id}: \n')

    for tcd_val in tcd_threshold:
        # Conditional logic for where TCD AND biomass
        tcd_raster = arcpy.sa.Con(arcpy.Raster(raster) > tcd_val, 1, 0) #TODO: Should this be greater than or equal to threshold?
        whrc_raster = arcpy.sa.Con(arcpy.Raster(whrc_raster_path) > 0, 1, 0)
        tcd_whrc_raster = arcpy.sa.Times(tcd_raster, whrc_raster)
        tcd_whrc_mask = arcpy.sa.Con(arcpy.Raster(tcd_whrc_raster) > 0, 1, 0)

        #Saving tcd_whrc mask
        mask_path_tcd = os.path.join(mask_tiles, f'{tile_id}_tcd{tcd_val}')
        print(f'Saving {mask_path_tcd}.tif')
        tcd_whrc_mask.save(f'{mask_path_tcd}.tif')

        # Conditional logic for TCD OR gain
        if gain == True:
            gain_raster = arcpy.sa.Con(arcpy.Raster(gain_raster_path) > 0, 1, 0)
            tcd_gain_raster = arcpy.ia.Merge([tcd_whrc_mask, gain_raster], "SUM")
            tcd_gain_mask = arcpy.sa.Con(arcpy.Raster(tcd_gain_raster) > 0, 1, 0)

            # Saving tcd_gain mask
            mask_path_tcd_gain = f'{mask_path_tcd}_gain'
            print(f'Saving {mask_path_tcd_gain}.tif')
            tcd_gain_mask.save(f'{mask_path_tcd_gain}.tif')
        else:
            mask_path_tcd_gain = mask_path_tcd
            tcd_gain_mask = tcd_whrc_mask

        # Conditional logic for TCD, gain, OR mangrove
        if os.path.exists(mangrove_raster_path):
            mangrove_raster = arcpy.sa.Con(arcpy.Raster(mangrove_raster_path) > 0, 1, 0)
            tcd_gain_mangrove_raster = arcpy.ia.Merge([tcd_gain_mask, mangrove_raster], "SUM")
            tcd_gain_mangrove_mask = arcpy.sa.Con(arcpy.Raster(tcd_gain_mangrove_raster) > 0, 1, 0)

            # Saving tcd_gain_mangrove mask
            mask_path_tcd_gain_mangrove = f'{mask_path_tcd_gain}_mangrove'
            print(f'Saving {mask_path_tcd_gain_mangrove}.tif')
            tcd_gain_mangrove_mask.save(f'{mask_path_tcd_gain_mangrove}.tif')
        else:
            mask_path_tcd_gain_mangrove = mask_path_tcd_gain
            tcd_gain_mangrove_mask = tcd_gain_mask

        # Conditional logic for TCD, gain, mangrove, OR plantations
        if os.path.exists(plantation_raster_path):
            plantation_raster = arcpy.sa.Con(arcpy.Raster(plantation_raster_path) > 0, 1, 0)
            tcd_gain_mangrove_plantation_raster = arcpy.ia.Merge([tcd_gain_mangrove_mask, plantation_raster], "SUM")
            tcd_gain_mangrove_plantation_mask = arcpy.sa.Con(arcpy.Raster(tcd_gain_mangrove_plantation_raster) > 0, 1, 0)

            # Saving tcd_gain_mangrove_plantation mask
            mask_path_tcd_gain_mangrove_plantation = f'{mask_path_tcd_gain_mangrove}_plantation'
            print(f'Saving {mask_path_tcd_gain_mangrove_plantation}.tif')
            tcd_gain_mangrove_plantation_mask.save(f'{mask_path_tcd_gain_mangrove_plantation}.tif')

def zonal_stats(input_folder):
    aoi_list = list_files_in_directory(input_folder, '.shp')

    for aoi in aoi_list:
        aoi_name = os.path.splitext(os.path.basename(aoi))[0]
        print(f"Now processing {aoi_name}: \n")

        if "IDN" in aoi_name:
            raster_folder = os.path.join(arcpy.env.workspace, "Input", "00N_110E")
            output_folder = os.path.join(arcpy.env.workspace, "Outputs", "00N_110E")
        else:
            raster_folder = os.path.join(arcpy.env.workspace, "Input", "20N_020W")
            output_folder = os.path.join(arcpy.env.workspace, "Outputs", "20N_020W")
        #TODO: Update cross-reference of tiles and gadm countries to process (dictionary) (MASK_PATHS = {"IDN": "00N_110E", "GMB": "20N_20W"})

        process_zonal_statistics(aoi, raster_folder, output_folder)

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

def list_files_in_directory(directory, file_extension):
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(file_extension)]

def zonal_stats_masked(aois_folder, input_folder, outputs_folder, mask_outputs_folder):
    aoi_list = list_files_in_directory(aois_folder, '.shp')

    for aoi in aoi_list:
        aoi_name = os.path.splitext(os.path.basename(aoi))[0]
        print(f"Now processing {aoi_name}: \n")

        if "IDN" in aoi_name:
            raster_folder = os.path.join(input_folder, "00N_110E")
            output_folder = os.path.join(outputs_folder, "00N_110E")
            mask_tiles = os.path.join(mask_outputs_folder, "00N_110E")
        else:
            raster_folder = os.path.join(input_folder, "20N_020W")
            output_folder = os.path.join(outputs_folder, "20N_020W")
            mask_tiles = os.path.join(mask_outputs_folder, "20N_020W")
        # TODO: Update cross-reference of tiles and gadm countries to process (dictionary) (MASK_PATHS = {"IDN": "00N_110E", "GMB": "20N_20W"})

        raster_list = list_files_in_directory(raster_folder, '.tif')
        mask_list = list_files_in_directory(mask_tiles, '.tif')

        for raster in raster_list:
            raster_obj = arcpy.Raster(raster)
            print(f'Calculating zonal statistics for {raster}')

            for mask in mask_list:
                mask_obj = arcpy.Raster(mask)

                # Check if spatial references and extents are the same
                if (raster_obj.extent == mask_obj.extent and raster_obj.spatialReference.name == mask_obj.spatialReference.name):
                    raster_name = os.path.splitext(os.path.basename(raster))[0]

                    mask_path = os.path.splitext(os.path.basename(mask))[0]
                    mask_name = mask_path.split("_", 2)[2]

                    # Create a name for the output table by concatenating the AOI name and raster name
                    output_name = "{}_{}.dbf".format(aoi_name, str(raster_name) + "_" + str(mask_name))
                    output_path = os.path.join(output_folder, output_name)

                    masked_raster = arcpy.sa.Times(raster_obj, mask_obj)
                    arcpy.gp.ZonalStatisticsAsTable_sa(aoi, "GID_0", masked_raster, output_path, "DATA", "SUM")
                    print(f'Masking {raster} by {mask}')

                    # Convert each output to csv
                    csv_file = "{}_{}.csv".format(aoi_name, str(raster_name) + "_" + str(mask_name))
                    arcpy.TableToTable_conversion(output_path, output_folder, csv_file)
                    print(f'{output_path} successfully finished')

                else:
                    print(f"Spatial references or extents do not match for {raster} and {mask}")

def zonal_stats_annualized(tcl_folder, input_folder, annual_folder):
    aoi_list = list_files_in_directory(tcl_folder, 'clip.tif')

    for aoi in aoi_list:
        aoi_name = os.path.splitext(os.path.basename(aoi))[0]
        print(f"Now processing {aoi_name}: \n")

        if "IDN" in aoi_name:
            raster_folder = os.path.join(input_folder, "00N_110E")
            output_folder = annual_folder
        else:
            raster_folder = os.path.join(input_folder, "20N_020W")
            output_folder = annual_folder
            # TODO: Update cross-reference of tiles and gadm countries to process (dictionary) (MASK_PATHS = {"IDN": "00N_110E", "GMB": "20N_20W"})

        process_annual_zonal_stats(aoi, raster_folder, output_folder)

def process_annual_zonal_stats(aoi, raster_folder, output_folder):
    raster_list = [os.path.join(raster_folder, f) for f in os.listdir(raster_folder) if "emis" in f and f.endswith('tif')]
    print(raster_list)

    for raster in raster_list:
        raster_name = os.path.splitext(os.path.basename(raster))[0]
        print(f'Calculating zonal statistics for {raster_name}: \n')

        output_name = f"{os.path.splitext(os.path.basename(aoi))[0]}_{raster_name}.dbf"
        output_path = os.path.join(output_folder, output_name)

        arcpy.gp.ZonalStatisticsAsTable_sa(aoi, "Value", raster, output_path, "DATA", "SUM")
        csv_file = f"{os.path.splitext(os.path.basename(aoi))[0]}_{raster_name}.csv"
        arcpy.TableToTable_conversion(output_path, output_folder, csv_file)

def ZonalStatsClean(input_folders, csv_folder) -> object:
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
                if "plantation." in file:
                    mask = "tcd, gain, mangrove, plantation"
                elif "mangrove." in file:
                    mask = "tcd, gain, mangrove"
                elif "gain." in file:
                    mask = "tcd, gain"
                elif "tcd" in file:
                    mask = "tcd"
                else:
                    mask = "no mask"
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
def zonal_stats_clean(input_folders, csv_folder):
    df = pd.DataFrame()

    for folder in input_folders:
        for file in os.listdir(folder):
            if file.endswith(".csv"):
                file_path = os.path.join(folder, file)
                csv_df = load_and_process_csv(file_path, file)
                df = pd.concat([df, csv_df], axis=0)

    print(df)

    output_path = os.path.join(csv_folder, "output.csv")
    df.to_csv(output_path, index=False)

def load_and_process_csv(file_path, file_name):
    csv_df = pd.read_csv(file_path)

# Downloads individual tiles from s3
    # source = source file on s3
    # dest = where to download
    # pattern = pattern for file name
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
        print(f'Option 1: Checking if {local_file_name} is already downloaded...')
        if os.path.exists(os.path.join(dest, local_file_name)):
            print(f'Option 1 success: {os.path.join(dest, local_file_name)} already downloaded', "\n")
            return
        else:
            print(f'Option 1 failure: {local_file_name} is not already downloaded.')
            print(f'Option 2: Checking for tile {source} on s3...')

            # If the tile isn't already downloaded, download is attempted
            # source = os.path.join(dir, file_name)
            source = f'{dir}/{file_name}'
            local_folder = os.path.join(dest, local_file_name)

            # cmd = ['aws', 's3', 'cp', source, dest, '--no-sign-request', '--only-show-errors']
            cmd = ['aws', 's3', 'cp', source, local_folder,
                   '--request-payer', 'requester', '--only-show-errors']
            log_subprocess_output_full(cmd)

            if os.path.exists(os.path.join(dest, local_file_name)):
                print_log(f'  Option 2 success: Tile {source} found on s3 and downloaded', "\n")
                return
            else:
                print_log(
                    f'  Option 2 failure: Tile {source} not found on s3. Tile not found but it seems it should be. Check file paths and names.', "\n")

    # All other tiles besides tree cover gain
    else:
        print_log(f'Option 1: Checking if {file_name} is already downloaded...')
        if os.path.exists(os.path.join(dest, file_name)):
            print_log(f'  Option 1 success: {os.path.join(dest, file_name)} already downloaded', "\n")
            return
        else:
            print_log(f'Option 1 failure: {file_name} is not already downloaded.')
            print_log(f'Option 2: Checking for tile {source} on s3...')

            # If the tile isn't already downloaded, download is attempted
            #source = os.path.join(dir, file_name)
            source = f'{dir}/{file_name}'

            # cmd = ['aws', 's3', 'cp', source, dest, '--no-sign-request', '--only-show-errors']
            cmd = ['aws', 's3', 'cp', source, dest, '--only-show-errors']
            log_subprocess_output_full(cmd)
            if os.path.exists(os.path.join(dest, file_name)):
                print_log(f'Option 2 success: Tile {source} found on s3 and downloaded', "\n")
                return
            else:
                print_log(f'Option 2 failure: Tile {source} not found on s3. Tile not found but it seems it should be. Check file paths and names.', "\n")

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

# Gets the directory of the tile
def get_tile_dir(tile):
    tile_dir = os.path.split(tile)[0]
    return tile_dir

def get_tile_name(tile):
    tile_name = os.path.split(tile)[1]
    return tile_name

# Gets the tile id from the full tile name using a regular expression
def get_tile_id(tile_name):
    tile_id = re.search("[0-9]{2}[A-Z][_][0-9]{3}[A-Z]", tile_name).group()
    return tile_id

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

def folder_check(folder):
        if os.path.isdir(folder):
            print(f"    Option 1 success: {folder} exists.")
        else:
            os.makedirs(folder)
            if os.path.isdir(folder):
                print(f"    Option 2 success: {folder} successfully created.")
            else:
                raise Exception(f"  Option 2 failure: {folder} could not be created.")