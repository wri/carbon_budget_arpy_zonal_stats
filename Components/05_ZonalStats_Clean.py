"""
This section of code is for organizing the outputs into one csv for clarity. It uses pandas to loop through the dbf
outputs and write the sum fields to a new dataframe, then export this dataframe to a csv. Comment out if not necessary
"""
import os
import pandas as pd
import arcpy
from funcs import ZonalStatsClean

#TODO: Change workspace using working_directory

arcpy.env.workspace = r"C:\GIS\carbon_model\CarbonFlux_QA_2023"
arcpy.env.overwriteOutput = True

ZonalStatsClean(arcpy.env.workspace)