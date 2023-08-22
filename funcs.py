import os
import arcpy
import pandas as pd

def CreateMasks(input_folder):
    mask_inputs = os.path.join(arcpy.env.workspace, "Mask", "Inputs")
    mask_tiles = os.path.join(arcpy.env.workspace, "Mask","Mask")

    tcd_tiles = os.path.join(mask_inputs, "TCD")
    gain_tiles = os.path.join(mask_inputs, "Gain")
    whrc_tiles = os.path.join(mask_inputs, "WHRC")
    mangrove_tiles = os.path.join(mask_inputs, "Mangrove")

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
        mangrove_raster = os.path.join(mangrove_tiles, str(tile_id + '_mangrove_agb_t_ha_2000_rewindow.tif'))
        whrc_raster = os.path.join(whrc_tiles, str(tile_id + '_t_aboveground_biomass_ha_2000.tif'))

        mask_path_tcd = os.path.join(mask_tiles, str(tile_id + '_tcd.tif'))
        mask_path_tcd_gain = os.path.join(mask_tiles, str(tile_id + '_tcd_gain.tif'))
        print('Creating masks for ' + tile_id + ": \n")

        # Conditional logic for TCD
        tcd_raster = arcpy.sa.Con(arcpy.Raster(raster) > 30, 1, 0)
        # tcd_raster.save(mask_path_tcd)

        # Conditional logic for Gain
        gain_raster: object = arcpy.sa.Con(arcpy.Raster(gain_raster) > 0, 1, 0)

        # Conditional logic for WHRC
        whrc_raster = arcpy.sa.Con(arcpy.Raster(whrc_raster) > 0, 1, 0)

        # Conditional logic for Mangrove
        mangrove_raster = arcpy.sa.Con(arcpy.Raster(mangrove_raster) > 0, 1, 0)

        # Add raster calculator logic...
        output_times = arcpy.sa.Times(tcd_raster, whrc_raster)
        output_plus = arcpy.sa.Plus(output_times, gain_raster)
        output_plus_2 = arcpy.sa.Plus(output_plus, mangrove_raster)
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

        # Conditional logic for Gain
        gain_raster: object = arcpy.sa.Con(arcpy.Raster(gain_raster) > 0, 0, 0)

        # Conditional logic for WHRC
        whrc_raster = arcpy.sa.Con(arcpy.Raster(whrc_raster) > 0, 1, 0)

        # Conditional logic for Mangrove
        mangrove_raster = arcpy.sa.Con(arcpy.Raster(mangrove_raster) > 0, 1, 0)

        # Add raster calculator logic...
        output_times = arcpy.sa.Times(tcd_raster, whrc_raster)
        output_plus = arcpy.sa.Plus(output_times, gain_raster)
        output_plus_2 = arcpy.sa.Plus(output_plus, mangrove_raster)
        output_raster = arcpy.sa.Con(arcpy.Raster(output_plus) > 0, 1, 0)

        output_raster.save(mask_path_tcd)

def ZonalStats(input_folder: object) -> object:
    # Get a list of shapefiles in the input folder
    aoi_list = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.shp')]

    print(aoi_list)
    # Loop through each area of interest
    for aoi in aoi_list:
        # Extract the name of the AOI from the file path
        aoi_name = os.path.splitext(os.path.basename(aoi))[0]
        print("Now processing " + aoi_name + ": \n")

        if "IDN" in aoi_name:
            raster_folder = os.path.join(arcpy.env.workspace,"Input","00N_110E")
            output_folder = os.path.join(arcpy.env.workspace, "Outputs", "00N_110E")
        else:
            raster_folder = os.path.join(arcpy.env.workspace, "Input", "20N_20W")
            output_folder = os.path.join(arcpy.env.workspace, "Outputs", "20N_20W")

        # Get a list of rasters in the raster folder
        raster_list = [os.path.join(raster_folder, f) for f in os.listdir(raster_folder) if f.endswith('.tif')]

        # Loop through each raster and calculate zonal statistics as table
        for raster in raster_list:
            # Extract the name of the raster from the file path
            raster_name = os.path.splitext(os.path.basename(raster))[0]
            print('Calculating zonal statistics for ' + raster_name + ": \n")

            # Create a name for the output table by concatenating the AOI name and raster name
            output_name = "{}_{}.dbf".format(aoi_name, raster_name)
            output_path = os.path.join(output_folder, output_name)

            # Calculate zonal statistics as table for the current raster and AOI
            arcpy.gp.ZonalStatisticsAsTable_sa(aoi, "GID_0", raster, output_path, "DATA", "SUM")

            # convert each output to csv
            csv_file = "{}_{}.csv".format(aoi_name, raster_name)
            arcpy.TableToTable_conversion(output_path, output_folder, csv_file)

def ZonalStatsMasked(input_folder: str) -> object:
    """

    :rtype: object
    """
    input_folder = os.path.join(arcpy.env.workspace, "Input", "AOIS")

    # Get a list of shapefiles in the input folder
    aoi_list = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.shp')]
    print(aoi_list)

    # Loop through each area of interest
    for aoi in aoi_list:
        # Extract the name of the AOI from the file path
        aoi_name = os.path.splitext(os.path.basename(aoi))[0]
        print("Now processing " + aoi_name + ": \n")

        if "IDN" in aoi_name:
            raster_folder = os.path.join(arcpy.env.workspace,"Input","00N_110E")
            output_folder = os.path.join(arcpy.env.workspace, "Outputs", "00N_110E")
            mask_tiles = os.path.join(arcpy.env.workspace, "Mask","Mask","00N_110E")
        else:
            raster_folder = os.path.join(arcpy.env.workspace, "Input", "20N_20W")
            output_folder = os.path.join(arcpy.env.workspace, "Outputs", "20N_20W")
            mask_tiles = os.path.join(arcpy.env.workspace, "Mask", "Mask","20N_20W")

        # Get a list of rasters in the raster folder
        raster_list = [os.path.join(raster_folder, f) for f in os.listdir(raster_folder) if f.endswith('.tif')]

        # Loop through each raster and calculate zonal statistics as table
        for raster in raster_list:
            # Extract the name of the raster from the file path
            raster_name = os.path.splitext(os.path.basename(raster))[0]
            #tile_id = str(raster_name.split("_", 1)[0]) + "_" + str(raster_name.split("_", 2)[1])

            print('Calculating zonal statistics for ' + raster_name + ": \n")

            mask_list = [os.path.join(mask_tiles, f) for f in os.listdir(mask_tiles) if f.endswith('.tif')]
            for mask in mask_list:
                mask_path = os.path.splitext(os.path.basename(mask))[0]
                mask_name = mask_path.split("_", 2)[2]

                # # Create a name for the output table by concatenating the AOI name and raster name
                output_name = "{}_{}.dbf".format(aoi_name, str(raster_name) + "_" + str(mask_name))
                output_path = os.path.join(output_folder, output_name)

                masked_raster = arcpy.sa.Times(raster, mask)
                arcpy.gp.ZonalStatisticsAsTable_sa(aoi, "GID_0", masked_raster, output_path, "DATA", "SUM")

                # convert each output to csv
                csv_file = "{}_{}.csv".format(aoi_name, str(raster_name) + "_" + str(mask_name))
                arcpy.TableToTable_conversion(output_path, output_folder, csv_file)

def ZonalStatsAnnualized(input_folder):
    # Get a list of shapefiles in the input folder
    input_folder = os.path.join(arcpy.env.workspace, "TCL")
    aoi_list = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('clip.tif')]

    print(aoi_list)

    # Loop through each area of interest
    for aoi in aoi_list:
        # Extract the name of the AOI from the file path
        aoi_name = os.path.splitext(os.path.basename(aoi))[0]
        print("Now processing " + aoi_name + ": \n")

        if "IDN" in aoi_name:
            raster_folder = os.path.join(arcpy.env.workspace,"Input","00N_110E")
            output_folder = os.path.join(arcpy.env.workspace, "Outputs", "Annual")
        else:
            raster_folder = os.path.join(arcpy.env.workspace, "Input", "20N_20W")
            output_folder = os.path.join(arcpy.env.workspace, "Outputs","Annual")

        # Get a list of rasters in the raster folder
        raster_list = [os.path.join(raster_folder, f) for f in os.listdir(raster_folder) if "emis" in f and f.endswith('tif')]

        # Loop through each raster and calculate zonal statistics as table
        for raster in raster_list:
            # Extract the name of the raster from the file path
            raster_name = os.path.splitext(os.path.basename(raster))[0]
            print('Calculating zonal statistics for ' + raster_name + ": \n")

            # Create a name for the output table by concatenating the AOI name and raster name
            output_name = "{}_{}.dbf".format(aoi_name, raster_name)
            output_path = os.path.join(output_folder, output_name)

            # Calculate zonal statistics as table for the current raster and AOI
            arcpy.gp.ZonalStatisticsAsTable_sa(aoi, "Value", raster, output_path, "DATA", "SUM")

            # convert each output to csv
            csv_file = "{}_{}.csv".format(aoi_name, raster_name)
            arcpy.TableToTable_conversion(output_path, output_folder, csv_file)

def ZonalStatsClean(input_folder) -> object:
    # Initialize an empty data frame to store the data


    folder1 = os.path.join(arcpy.env.workspace,"Outputs","00N_110E")
    folder2 = os.path.join(arcpy.env.workspace,"Outputs","20N_20W")
    folder3 = os.path.join(arcpy.env.workspace,"Outputs","Annual")

    df = pd.DataFrame()

    # Loop through the files in folder1
    for file in os.listdir(folder1):
        if file.endswith(".csv"):
            # Load the csv file into a pandas data frame
            csv_df = pd.read_csv(os.path.join(folder1, file))

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
            if "forest" in file:
                extent = "forest extent"
            else:
                extent = "full extent"
            csv_df["Extent"] = extent

            # Define mask of calc
            if "tcd_gain" in file:
                mask = "tcd and gain"
            elif "_tcd." in file:
                mask = "tcd"
            else:
                mask = "no mask"
            csv_df["Mask"] = mask

            # Drop all other fields
            assert isinstance(csv_df, object)
            csv_df.drop([ 'OID_', 'COUNT', 'AREA'], axis=1, inplace=True)

            # Append the data to the main data frame
            df = pd.concat([df, csv_df], axis=0)

    # Loop through the files in folder2
    for file in os.listdir(folder2):
        if file.endswith(".csv"):
            # Load the csv file into a pandas data frame
            csv_df = pd.read_csv(os.path.join(folder2, file))

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
            if "forest" in file:
                extent = "forest extent"
            else:
                extent = "full extent"
            csv_df["Extent"] = extent

            # Define mask of calc
            if "tcd_gain" in file:
                mask = "tcd and gain"
            elif "_tcd." in file:
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
    output_path = os.path.join(arcpy.env.workspace, "Outputs", "CSV","output.csv")

    # Export the data frame as a CSV file
    df.to_csv(output_path, index=False)

#Export dataframe for annualized results
