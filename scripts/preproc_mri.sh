#!/bin/bash
set -euo pipefail

# Preprocess the given sMRI using the following pipeline:
# 1. Bias Field Correction
# 2. Affine Registration
# 3. Skull Stripping
# 4. Intensity Normalization
# 5. Brain Segmentation and ROI Volume Extraction
# 6. 4D Mask Creation

N_WORKERS=$1
RAW="$2"
TEMPLATE="$3"
OUTDIR="$4"

MAT_PREFIX="t1_to_mni_"
T1_TO_MNI_MAT="${MAT_PREFIX}0GenericAffine.mat"
WARPED="${MAT_PREFIX}Warped.nii.gz"
CORRECTED="corrected.nii.gz"
SKULLSTRIP="skullstrip.nii.gz"
BRAIN_MASK="skullstrip_bet.nii.gz"
PREPROCESSED="preprocessed.nii.gz"
SYNTHSEG_IMG="synthseg.nii.gz"
SYNTHSEG_CSV="volumes.csv"
SYNTHSEG_4D="synthseg_4d.nii.gz"

UID_GID="$(id -u):$(id -g)"
VOLUMES_COMMON="-v $OUTDIR:/out -v $RAW:/input.nii.gz:ro -v $TEMPLATE:/template.nii.gz:ro"
CMD_ANTS="docker run --rm $VOLUMES_COMMON -u $UID_GID antsx/ants:2.6.2"
CMD_FREESURFER="docker run --rm $VOLUMES_COMMON -u $UID_GID freesurfer/freesurfer:7.4.1"
CMD_NEUROFLUX="docker run --rm $VOLUMES_COMMON -u $UID_GID antonioscardace/neuroflux:latest"

# To avoid redundant computation, check if preprocessing has already been completed for this scan.
# If so, exit the script successfully.

echo "🔍 [Step 0/6] Checking if preprocessing has already been completed..."
if [ -s "$OUTDIR/$SYNTHSEG_4D" ]; then
    echo "✅ Scan already preprocessed"
    exit 0
fi

# Step 1: Perform Bias Field Correction (ANTs - N4BiasFieldCorrection).
# Verify that the operation completed successfully.

echo "🧠 [Step 1/6] Running Bias Field Correction..."
$CMD_ANTS N4BiasFieldCorrection \
    -i /input.nii.gz \
    -o /out/$CORRECTED \
    -d 3 -s 3 > /dev/null

[ -s "$OUTDIR/$CORRECTED" ] || { echo "❌ Bias Field Correction failed"; exit 1; }

# Step 2: Perform Affine Registration (ANTs - antsRegistrationSyNQuick).
# Verify that the operation completed successfully.

echo "🧠 [Step 2/6] Running Affine Registration..."
$CMD_ANTS antsRegistrationSyNQuick.sh \
    -f /template.nii.gz \
    -m /out/$CORRECTED \
    -o /out/$MAT_PREFIX \
    -d 3 -t a > /dev/null 2>&1

[ -s "$OUTDIR/$WARPED" ] && [ -s "$OUTDIR/$T1_TO_MNI_MAT" ] || { echo "❌ Affine Registration failed"; exit 1; }

# Step 3: Perform Skull Stripping (HD-BET).
# Verify that the operation completed successfully.

echo "🧠 [Step 3/6] Running Skull Stripping..."
hd-bet -i "$OUTDIR/$WARPED" -o "$OUTDIR/$SKULLSTRIP" -device cpu --save_bet_mask > /dev/null 2>&1
[ -s "$OUTDIR/$SKULLSTRIP" ] && [ -s "$OUTDIR/$BRAIN_MASK" ] || { echo "❌ Skull Stripping failed"; exit 1; }

# Step 4: Perform Intensity Normalization (WhiteStripe).
# Verify that the operation completed successfully.

echo "🧠 [Step 4/6] Running Intensity Normalization..."
ws-normalize -mo t1 -m "$OUTDIR/$BRAIN_MASK" -o "$OUTDIR/$PREPROCESSED" "$OUTDIR/$SKULLSTRIP"
[ -s "$OUTDIR/$PREPROCESSED" ] || { echo "❌ Intensity Normalization failed"; exit 1; }

# Step 5: Automatic Segmentation and ROI Volume Extraction (SynthSeg 2.0 with parcellation).
# Verify that the operation completed successfully.

echo "🧠 [Step 5/6] Running Segmentation and Volume Extraction..."
$CMD_FREESURFER mri_synthseg \
    --i /out/$PREPROCESSED \
    --o /out/$SYNTHSEG_IMG \
    --vol /out/$SYNTHSEG_CSV \
    --parc --cpu --threads $N_WORKERS > /dev/null

$CMD_NEUROFLUX synthseg_tidy -p "/out/$SYNTHSEG_CSV"   
[ -s "$OUTDIR/$SYNTHSEG_IMG" ] && [ -s "$OUTDIR/$SYNTHSEG_CSV" ] || { echo "❌ SynthSeg failed"; exit 1; }

# Step 6: 4D Mask Creation
# Verify that the operation completed successfully.

echo "🧠 [Step 6/6] Running 4D Mask Creation..."
$CMD_NEUROFLUX synthseg_one_hot -i "/out/$SYNTHSEG_IMG" -o "/out/$SYNTHSEG_4D"
[ -s "$OUTDIR/$SYNTHSEG_4D" ] || { echo "❌ 4D Mask Creation failed"; exit 1; }

# Keep only useful preprocessed files.
# Remove intermediate files, keeping only the final files.

echo "🎉 Cleaning up intermediate files..."
find "$OUTDIR" -type f ! \( \
    -name "corrected.nii.gz" \
    -o -name "preprocessed.nii.gz" \
    -o -name "skullstrip_bet.nii.gz" \
    -o -name "synthseg.nii.gz" \
    -o -name "synthseg_4d.nii.gz" \
    -o -name "volumes.csv" \
    -o -name "t1_to_mni_0GenericAffine.mat" \
\) -exec rm {} +