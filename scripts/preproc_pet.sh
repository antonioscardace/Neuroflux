#!/bin/bash
set -euo pipefail

# Preprocess the given PET scan using the following pipeline:
# 1. Motion Correction and Mean Image Calculation (if it is 4D)
# 2. PET to sMRI (preprocessed) Registration
# 3. Spatial Normalisation
# 4. Skull Stripping and Artifact Removal
# 5. Partial Volume Correction (PVC)
# 6. SUVR Normalisation 
# 7. Feature Extraction

PET_RAW="$1"
T1_DIR="$2"
TEMPLATE="$3"
OUTDIR="$4"

T1_CORRECTED="corrected.nii.gz"
T1_BRAINMASK="skullstrip_bet.nii.gz"
T1_SYNTHSEG="synthseg.nii.gz"
T1_4D="synthseg_4d.nii.gz"
T1_TO_MNI_MAT="t1_to_mni_0GenericAffine.mat"

MAT_PREFIX="pet_to_t1_"
PET_TO_T1_MAT="${MAT_PREFIX}0GenericAffine.mat"
PET_STATIC="static.nii.gz"
PET_WARPED="warped.nii.gz"
PET_CLEAN="skullstrip.nii.gz"
PET_PVC="pvc.nii.gz"
PET_SUVR="suvr_norm.nii.gz"
PET_FEATURES="features.csv"

UID_GID="$(id -u):$(id -g)"
VOLUMES_COMMON="-v $T1_DIR:/t1 -v $OUTDIR:/out -v $PET_RAW:/input.nii.gz -v $TEMPLATE:/template.nii.gz"
CMD_ANTS="docker run --rm $VOLUMES_COMMON -u $UID_GID antsx/ants:2.6.2"
CMD_PVC="docker run --rm $VOLUMES_COMMON -u $UID_GID benthomas1984/petpvc:v1.2.2"
CMD_NEUROFLUX="docker run --rm $VOLUMES_COMMON -u $UID_GID antonioscardace/neuroflux:latest"

# To avoid redundant computation, check if preprocessing has already been completed for this scan.
# If so, exit the script successfully.

echo "🔍 [Step 0/7] Checking if preprocessing has already been completed..."
if [ -s "$OUTDIR/$PET_FEATURES" ]; then
    echo "✅ Scan already preprocessed"
    exit 0
fi

# Step 1: Motion Correction and Mean Image Calculation (ANTs - antsMotionCorr)
# Verify that the operation completed successfully.

echo "🧠 [Step 1/7] Running Motion Correction and Mean Image Calculation..."
NDIMS=$($CMD_ANTS PrintHeader /input.nii.gz | grep "dim\[0\]" | awk '{print $3}' | head -n 1)
[ "$NDIMS" -eq 4 ] && $CMD_ANTS antsMotionCorr -d 3 -o "[/out/$PET_STATIC]" -a /input.nii.gz
[ "$NDIMS" -eq 3 ] && cp "$PET_RAW" "$OUTDIR/$PET_STATIC"
[ -s "$OUTDIR/$PET_STATIC" ] || { echo "❌ Motion Correction failed"; exit 1; }

# Step 2: PET to sMRI Registration (ANTs - antsRegistrationSyNQuick)
# Verify that the operation completed successfully.

echo "🧠 [Step 2/7] Running PET to sMRI Registration..."
$CMD_ANTS antsRegistrationSyNQuick.sh \
    -d 3 \
    -f "/t1/$T1_CORRECTED" \
    -m "/out/$PET_STATIC" \
    -o "/out/$MAT_PREFIX" \
    -t a -x "/t1/$T1_BRAINMASK" > /dev/null 2>&1

[ -s "$OUTDIR/$PET_TO_T1_MAT" ] || { echo "❌ PET-MRI registration failed"; exit 1; }

# Step 3: Spatial Normalisation (ANTs - antsApplyTransforms)
# Verify that the operation completed successfully.

echo "🧠 [Step 3/7] Running Spatial Normalization..."
$CMD_ANTS antsApplyTransforms \
    -d 3 \
    --float \
    -n Linear \
    -i "/out/$PET_STATIC" \
    -r "/template.nii.gz" \
    -o "/out/$PET_WARPED" \
    -t "/t1/$T1_TO_MNI_MAT" \
    -t "/out/$PET_TO_T1_MAT" > /dev/null

[ -s "$OUTDIR/$PET_WARPED" ] || { echo "❌ Spatial Normalisation failed"; exit 1; }

# Step 4: Skull Stripping and Artifact Removal (Python).
# Verify that the operation completed successfully.

echo "🧠 [Step 4/7] Running Skull Stripping and Artifact Removal..."
$CMD_NEUROFLUX skullstrip_and_clean -i "/out/$PET_WARPED" -m "/t1/$T1_BRAINMASK" -o "/out/$PET_CLEAN"
[ -s "$OUTDIR/$PET_CLEAN" ] || { echo "❌ Cleaning failed"; exit 1; }

# Step 5: Partial Volume Correction (PETPVC)
# Verify that the operation completed successfully.

echo "🧠 [Step 5/7] Running Partial Volume Correction..."
$CMD_PVC petpvc \
    -i "/out/$PET_CLEAN" \
    -m "/t1/$T1_4D" \
    -o "/out/$PET_PVC" \
    -x 6.0 -y 6.0 -z 6.0 \
    --pvc IY > /dev/null 2>&1

[ -s "$OUTDIR/$PET_PVC" ] || { echo "❌ PVC failed"; exit 1; }

# Step 6: SUVR Normalization (Python).
# Verify that the operation completed successfully.

echo "🧠 [Step 6/7] Running SUVR Normalization..."
$CMD_NEUROFLUX pet_normalize_suvr -i "/out/$PET_PVC" -m "/t1/$T1_SYNTHSEG" -o "/out/$PET_SUVR"
[ -s "$OUTDIR/$PET_SUVR" ] || { echo "❌ SUVR Normalization failed"; exit 1; }

# Step 7: Feature Extraction (Python).
# Verify that the operation completed successfully.

echo "🧠 [Step 7/7] Running Feature Extraction..."
$CMD_NEUROFLUX pet_extract_roi_features -i "/out/$PET_SUVR" -m "/t1/$T1_SYNTHSEG" -o "/out/$PET_FEATURES"
[ -s "$OUTDIR/$PET_FEATURES" ] || { echo "❌ Feature Extraction failed"; exit 1; }

# Keep only useful preprocessed files.
# Remove intermediate files, keeping only the final files.

echo "🎉 Cleaning up intermediate files..."
find "$OUTDIR" -type f ! \( \
    -name "warped.nii.gz" \
    -o -name "skullstrip.nii.gz" \
    -o -name "pvc.nii.gz" \
    -o -name "suvr_norm.nii.gz" \
    -o -name "features.csv" \
    -o -name "pet_to_t1_0GenericAffine.mat" \
\) -exec rm {} +