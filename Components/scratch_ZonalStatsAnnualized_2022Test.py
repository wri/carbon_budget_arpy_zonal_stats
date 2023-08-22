import arcpy
import os
import pandas as pd
from funcs import ZonalStatsAnnualized
arcpy.env.overwriteOutput = True

# Set the workspace and input/output folders
arcpy.env.workspace = r"U:\eglen\Data\CarbonFlux_QA_2023"
input_folder = r"U:\eglen\Data\CarbonFlux_QA_2023\TCL"


ZonalStatsAnnualized(input_folder)
