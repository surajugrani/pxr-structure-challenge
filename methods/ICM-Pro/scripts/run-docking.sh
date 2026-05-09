#!/bin/bash
module load icm

for state_dir in 184folders/*/; do
    echo "Processing $state_dir"
    abs_lig=$(realpath $(ls "$state_dir"*V200*.sdf))
    abs_rec=$(realpath $(ls "$state_dir"*rec*.pdb))
    abs_lig_base="${abs_lig%.sdf}"

    cat > /tmp/dock.icm << EOF
call _startup
read pdb "${abs_rec}" name="rec"
read mol "${abs_lig}" name="lig"
move a_lig. a_rec.
convertObject a_rec. no no no no no no no ""
write object "complex.ob" a_rec_1.
list object
quit
EOF

    cd "$state_dir"
    icm64 -vlscluster -s /tmp/dock.icm
    icm64 -vlscluster _dockBatch complex.ob ligmol=m -R -u
    cd ../..
done