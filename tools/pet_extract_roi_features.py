#!/usr/bin/env python3

import argparse
import numpy as np
import pandas as pd
import nibabel as nib

# Mapping of 102 ROI names to SynthSeg label IDs.
# This configuration reflects the output of SynthSeg 2.0 utilizing the '--parc' flag.
# It performs cortical parcellation according to the Desikan-Killiany (DK) atlas.

ROI_SUBCORTICAL_LEFT = {
    'left_cerebral_white_matter': 2,
    'left_cerebral_cortex': 3,
    'left_lateral_ventricle': 4,
    'left_inferior_lateral_ventricle': 5,
    'left_cerebellum_white_matter': 7,
    'left_cerebellum_cortex': 8,
    'left_thalamus': 10,
    'left_caudate': 11,
    'left_putamen': 12,
    'left_pallidum': 13,
    '3rd_ventricle': 14,
    '4th_ventricle': 15,
    'brain_stem': 16,
    'left_hippocampus': 17,
    'left_amygdala': 18,
    'csf': 24,
    'left_accumbens_area': 26,
    'left_ventral_dc': 28
}

ROI_SUBCORTICAL_RIGHT = {
    'right_cerebral_white_matter': 41,
    'right_cerebral_cortex': 42,
    'right_lateral_ventricle': 43,
    'right_inferior_lateral_ventricle': 44,
    'right_cerebellum_white_matter': 46,
    'right_cerebellum_cortex': 47,
    'right_thalamus': 49,
    'right_caudate': 50,
    'right_putamen': 51,
    'right_pallidum': 52,
    'right_hippocampus': 53,
    'right_amygdala': 54,
    'right_accumbens_area': 58,
    'right_ventral_dc': 60
}

ROI_CORTEX_LEFT = {
    'ctx-lh-bankssts': 1001,
    'ctx-lh-caudalanteriorcingulate': 1002,
    'ctx-lh-caudalmiddlefrontal': 1003,
    'ctx-lh-cuneus': 1005,
    'ctx-lh-entorhinal': 1006,
    'ctx-lh-fusiform': 1007,
    'ctx-lh-inferiorparietal': 1008,
    'ctx-lh-inferiortemporal': 1009,
    'ctx-lh-isthmuscingulate': 1010,
    'ctx-lh-lateraloccipital': 1011,
    'ctx-lh-lateralorbitofrontal': 1012,
    'ctx-lh-lingual': 1013,
    'ctx-lh-medialorbitofrontal': 1014,
    'ctx-lh-middletemporal': 1015,
    'ctx-lh-parahippocampal': 1016,
    'ctx-lh-paracentral': 1017,
    'ctx-lh-parsopercularis': 1018,
    'ctx-lh-parsorbitalis': 1019,
    'ctx-lh-parstriangularis': 1020,
    'ctx-lh-pericalcarine': 1021,
    'ctx-lh-postcentral': 1022,
    'ctx-lh-posteriorcingulate': 1023,
    'ctx-lh-precentral': 1024,
    'ctx-lh-precuneus': 1025,
    'ctx-lh-rostralanteriorcingulate': 1026,
    'ctx-lh-rostralmiddlefrontal': 1027,
    'ctx-lh-superiorfrontal': 1028,
    'ctx-lh-superiorparietal': 1029,
    'ctx-lh-superiortemporal': 1030,
    'ctx-lh-supramarginal': 1031,
    'ctx-lh-frontalpole': 1032,
    'ctx-lh-temporalpole': 1033,
    'ctx-lh-transversetemporal': 1034,
    'ctx-lh-insula': 1035
}

ROI_CORTEX_RIGHT = {
    'ctx-rh-bankssts': 2001,
    'ctx-rh-caudalanteriorcingulate': 2002,
    'ctx-rh-caudalmiddlefrontal': 2003,
    'ctx-rh-cuneus': 2005,
    'ctx-rh-entorhinal': 2006,
    'ctx-rh-fusiform': 2007,
    'ctx-rh-inferiorparietal': 2008,
    'ctx-rh-inferiortemporal': 2009,
    'ctx-rh-isthmuscingulate': 2010,
    'ctx-rh-lateraloccipital': 2011,
    'ctx-rh-lateralorbitofrontal': 2012,
    'ctx-rh-lingual': 2013,
    'ctx-rh-medialorbitofrontal': 2014,
    'ctx-rh-middletemporal': 2015,
    'ctx-rh-parahippocampal': 2016,
    'ctx-rh-paracentral': 2017,
    'ctx-rh-parsopercularis': 2018,
    'ctx-rh-parsorbitalis': 2019,
    'ctx-rh-parstriangularis': 2020,
    'ctx-rh-pericalcarine': 2021,
    'ctx-rh-postcentral': 2022,
    'ctx-rh-posteriorcingulate': 2023,
    'ctx-rh-precentral': 2024,
    'ctx-rh-precuneus': 2025,
    'ctx-rh-rostralanteriorcingulate': 2026,
    'ctx-rh-rostralmiddlefrontal': 2027,
    'ctx-rh-superiorfrontal': 2028,
    'ctx-rh-superiorparietal': 2029,
    'ctx-rh-superiortemporal': 2030,
    'ctx-rh-supramarginal': 2031,
    'ctx-rh-frontalpole': 2032,
    'ctx-rh-temporalpole': 2033,
    'ctx-rh-transversetemporal': 2034,
    'ctx-rh-insula': 2035
}

ROI_LABEL_MAP = {
    **ROI_SUBCORTICAL_LEFT,
    **ROI_SUBCORTICAL_RIGHT,
    **ROI_CORTEX_LEFT,
    **ROI_CORTEX_RIGHT
}

# This function extracts ROI-wise PET features using a SynthSeg segmentation.
# For each ROI, it computes the number of voxels, mean, standard deviation, and total uptake.
# Saves the results to a CSV file.
# Author: Antonio Scardace

def extract_roi_features(scan_path: str, mask_path: str, out_path: str) -> None:

    pet_vol = nib.load(scan_path).get_fdata()
    mask_vol = nib.load(mask_path).get_fdata().astype(int)
    if pet_vol.shape != mask_vol.shape:
        raise ValueError('PET and mask volumes must have the same shape.')

    df = pd.DataFrame(columns=['roi_label_id', 'roi_name', 'n_voxels', 'mean_uptake', 'std_dev_uptake', 'total_uptake'])
    for roi_name, roi_label_id in ROI_LABEL_MAP.items():
        roi_values = pet_vol[mask_vol == roi_label_id]
        mean_val = float(np.mean(roi_values)) if roi_values.size else 0.0
        std_val = float(np.std(roi_values)) if roi_values.size else 0.0
        total_val = float(np.sum(roi_values)) if roi_values.size else 0.0
        df.loc[len(df)] = [roi_label_id, roi_name, int(roi_values.size), mean_val, std_val, total_val]

    df.to_csv(out_path, index=False, float_format='%.6f')

# CLI to extract ROI-wise PET features from a SynthSeg segmentation.
# Requires input PET scan (NIfTi), mask with reference region (NIfTi), and output path (CSV).
# Author: Antonio Scardace

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_path',  type=str, required=True)
    parser.add_argument('-m', '--mask_path',   type=str, required=True)
    parser.add_argument('-o', '--output_path', type=str, required=True)
    args = parser.parse_args()

    extract_roi_features(args.input_path, args.mask_path, args.output_path)