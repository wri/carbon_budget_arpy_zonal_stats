import constants_and_names as cn
from funcs import create_masks

# Set input folders to the Mask, Inputs folders and tcd_threshold/ gain values
create_masks(cn.tcd_folder, cn.gain_folder, cn.whrc_folder, cn.mangrove_folder, cn.plantations_folder, cn.tcd_threshold, cn.gain)
