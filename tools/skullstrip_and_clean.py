#!/usr/bin/env python3

import argparse
import numpy as np
import nibabel as nib

from scipy import ndimage

# This function applies skull stripping and cleaning to a neuroimaging scan based on a given brain mask.
# Keeps only non-zero voxels in scan and mask, removing background.
# Removes small isolated voxels (noise) that might remain after masking.
# Saves the cleaned scan to the output path.
# Author: Antonio Scardace

def skullstrip_and_clean(scan_path: str, mask_path: str, out_path: str) -> None:

    scan = nib.load(scan_path)
    scan_data = scan.get_fdata()
    mask_data = nib.load(mask_path).get_fdata()

    voxel_intersection = ((mask_data > 0) & (scan_data > 0)).astype(np.uint8)
    cleaned_mask = ndimage.binary_opening(voxel_intersection, np.ones((3, 3, 3)), 1).astype(np.uint8)
    cleaned_scan_data = (scan_data * cleaned_mask).astype(scan.get_data_dtype())
    cleaned_scan = nib.Nifti1Image(cleaned_scan_data, scan.affine, scan.header)
    nib.save(cleaned_scan, out_path)

# CLI for skull stripping and artifact removal on neuroimaging scans.
# Requires: input scan (NIfTI), brain mask (NIfTI), and output path.
# Author: Antonio Scardace

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_path',  type=str, required=True)
    parser.add_argument('-m', '--mask_path',   type=str, required=True)
    parser.add_argument('-o', '--output_path', type=str, required=True)
    args = parser.parse_args()
    
    skullstrip_and_clean(args.input_path, args.mask_path, args.output_path)