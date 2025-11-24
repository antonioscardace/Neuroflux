#!/usr/bin/env python3

import argparse
import numpy as np
import nibabel as nib

# This function converts a 3D SynthSeg segmentation into a 4D one-hot mask.
# Each label in the 3D volume becomes a separate channel in the 4D output.
# Background (label 0) is ignored. The output is saved as a float32 NIfTI file.
# Author: Antonio Scardace

def synthseg_4d_mask_creation(scan_path: str, out_path: str) -> None:

    scan = nib.load(scan_path)
    scan_data = scan.get_fdata().astype(np.int32)
    unique_labels = np.unique(scan_data)
    unique_labels = unique_labels[unique_labels != 0]

    shape_3d = scan_data.shape
    shape_4d = shape_3d + (len(unique_labels),)
    scan_data_4d = np.zeros(shape_4d, dtype=np.float32)
    for i, label in enumerate(unique_labels):
        scan_data_4d[..., i] = (scan_data == label).astype(np.float32)

    one_hot_mask = nib.Nifti1Image(scan_data_4d, scan.affine, scan.header)
    one_hot_mask.set_data_dtype(np.float32)
    nib.save(one_hot_mask, out_path)

# CLI to create 4D masks from a 3D SynthSeg segmentation.
# Requires input 3D segmentation (NIfTi) and output path (NIfTi).
# Author: Antonio Scardace

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_path',  type=str, required=True)
    parser.add_argument('-o', '--output_path', type=str, required=True)
    args = parser.parse_args()
    
    synthseg_4d_mask_creation(args.input_path, args.output_path)