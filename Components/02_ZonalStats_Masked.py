import constants_and_names as cn
from funcs import zonal_stats_masked

#Set the input folders
zonal_stats_masked(cn.aois_folder, cn.input_folder, cn.outputs_folder, cn.mask_output_folder)
