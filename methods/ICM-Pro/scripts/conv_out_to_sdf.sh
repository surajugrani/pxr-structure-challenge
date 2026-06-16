#!/bin/bash
module load icm
for state_dir in 3_plainAF3_redocking/184folders/*/; do
#for state_dir in 1f1t/; do
    echo "Processing $state_dir"
    out_obj=$(ls "$state_dir"*lig1.ob)
    folder=$(basename "${state_dir%/}")
    sdf_nam="${state_dir}${folder}_docked.sdf"
    cat > /tmp/convert.icm << EOF
call _startup
read object "${out_obj}"
load conf a_1. 1
write mol "${sdf_nam}" a_1.
#load conf a_1. 2
#write mol "${sdf_nam}" a_1. append
#load conf a_1. 3
#write mol "${sdf_nam}" a_1. append
quit
EOF
    icm64 -vlscluster -s /tmp/convert.icm
done