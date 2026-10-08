import constants_and_names as cn
from funcs import create_masks

# Create model extent masks for specified TCD thresholds
print("Step 2: Creating TCD Masks... \n")
create_masks(cn.tcd_threshold)

# Other options:
# create_masks([0, 75])
# create_masks([30])