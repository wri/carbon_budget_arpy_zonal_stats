import arcpy
import constants_and_names as cn
from funcs import zonal_stats_annualized

#Set the input folders
zonal_stats_annualized(cn.tcl_folder, cn.input_folder, cn.annual_folder)

