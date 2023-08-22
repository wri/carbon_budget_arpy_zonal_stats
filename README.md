### Purpose

    The purpose of this tool is to automate the zonal statistics portion of the QAQC process for the
    Annual Carbon Flux Model (Harris, 2021) Update. Each year, the Carbon Flux Model is run with updated activity data
    for tree cover loss (Hansen, 2013) and auxiliary inputs. Before the data is launched on Global Forest Watch, the
    outputs are compared across platforms and methods including the GeoTrellis Tool, GFW Dashboard download spreadsheets,
    the GFW API, and ArcGIS Zonal Statistics calculations. 

### Inputs

#### Areas of Interest:
    
    This tool is set up to run statistics for two areas (Indonesia and Gambia), although it could be expanded to other 
    areas of interest. The inputs for these areas are derived from the GADM 3.6 Dataset, available for download here:
    [](https://gadm.org/download_country_v3.html).

    The Indonesia boundary is IND.14.13 and the Gambia Boundary is GMB.2. 

    These inputs will need to be updated if and when GFW switches to a newer version of GADM. 

#### Carbon Flux Model Data:

    Three separate outputs from the Carbon Flux Model, each at two different extents, are used in as inputs in 
    this tool. This is a total of six different inouts. Inputs include gross emissions (all gasses), gross removals
    (CO2), and net flux (CO2e). All are in inuts Mg / pixel. Calculations are run using both the forest extent and
    full extent outputs. 

| AOI | Extent | Type            | Units         | Tile     |
|-----|--------|-----------------|---------------|----------|
| IDN | Forest | Gross Emissions | Mg CO2e/pixel | 00N_110E |
| IDN | Forest | Gross Removals  | Mg CO2/pixel  | 00N_110E |
| IDN | Forest | Net Flux        | Mg CO2e/pixel | 00N_110E |
| IDN | Full   | Gross Emissions | Mg CO2e/pixel | 00N_110E |
| IDN | Full   | Gross Removals  | Mg CO2/pixel  | 00N_110E |
| IDN | Full   | Net Flux        | Mg CO2e/pixel | 00N_110E |
| GMB | Forest | Gross Emissions | Mg CO2/pixel  | 20N_020W |
| GMB | Forest | Gross Removals  | Mg CO2e/pixel | 20N_020W |
| GMB | Forest | Net Flux        | Mg CO2/pixel  | 20N_020W |
| GMB | Full   | Gross Emissions | Mg CO2e/pixel | 20N_020W |
| GMB | Full   | Gross Removals  | Mg CO2/pixel  | 20N_020W |
| GMB | Full   | Net Flux        | Mg CO2e/pixel | 20N_020W |


#### Auxiliary Datasets:

    Other auxiliary inputs for this tool include:

| Dataset              | Use Description                                                                         |
|----------------------|-----------------------------------------------------------------------------------------|
| Tree Cover Loss      | Used to calculate annual emissions.                                                     |
| Tree Cover Density   | Used to create density threshold mask. Default set to 30> or greater                    |
| Tree Cover Gain      | Used to create tree cover gain mask. Areas of tree cover gain included in mask          |
| Mangrove Extent      | Used to create Mangrove mask. Areas of mangrove included in mask.                       |
| Pre-2000 Plantations | Used to create Pre-2000 plantations mask. Pre-2000 plantations masked from calculations |


### Outputs:

    The final outputs include one csv file summarizing results for each entry described in the "Carbon Flux Model 
    Inputs" table. Additionally, separate csv files for annual emissions are produced. 

### Code Summary

#### calculate_zonal_statistics
    This file is for running the code in its entirety. The only input necessary from the user is the environemnt 
    path. Assuming all input datasets and subfolders are organized in the workspace correctly, this script will 
    execute all functions in the repository and produce output csvs.

#### funcs
    This file stores all of the functions used in the tool. Any edits to functions would be made in this file.

#### components

    This folder houses individual scripts for running separate functions. The only input necessary in these scripts
    is the workspace environemnt path. These can be useful for running particular functions separately and testing edits 
    / troubleshootins. Each function is described below. 

##### 01 Create Masks
    This script uses data on tree cover density, tree cover gain, mangrove extent, WHRC biomass, and pre-2000 plantations
    to replicate the masks that are used in GFW data processing. This facilitates direct comparison with results from the GFW 
    dashboard, geotrellis client, and GFW API. The script creates masks based on criteria for each input dataset and saves these
    masks in a sub directory. These masks are used later as extent inputs in the Zonal Statistics Masked script.

##### 02 Zonal Stats
    This script calulates zonal statistics for each area of interest and carbon dataset combination without applying any 
    additional masking.

##### 03 Zonal Stats Masked
    This script calculates zonal statistics for each area of interest and carbon dataset combination and applies each of 
    two masks:
    
    _tcd: considers tree cover density > 30 
    _tcd_gain: considers tree cover density > 30 or gain = 1

##### 04 Zonal Stats Annualized

##### 05 Zonal Stats Cleaned

### Running the Code

### Other Notes
    Updates in progress include...
    
    A data download / prep script that will automatically download new data inputs from 
    s3 and build out the correct folder structure within a given workspace. 

    Additional functions to clean and export annualized results

#### Contact Info
    Erin Glen - erin.glen@wri.org