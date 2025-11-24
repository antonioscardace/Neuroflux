#!/usr/bin/env python3

import argparse
import pandas as pd

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

# This function transforms the SynthSeg volume output to a tidy format with ROI IDs.
# It applies ROI mapping to tidy format.
# Author: Antonio Scardace

def synthseg_csv_to_tidy(csv_path: str) -> None:

    df_vol = pd.read_csv(csv_path)
    df_vol = df_vol.drop(columns=['subject'], errors='ignore')
    df_tidy = df_vol.melt(var_name='roi_name', value_name='volume')

    s_rois = pd.Series(ROI_LABEL_MAP)
    norm_map_keys = s_rois.index.str.lower().str.replace(' ', '_').str.replace('-', '_')
    roi_lookup = pd.Series(data=s_rois.values, index=norm_map_keys).to_dict()
    match_keys = df_tidy['roi_name'].str.lower().str.replace(' ', '_').str.replace('-', '_')
    
    df_tidy['roi_label_id'] = match_keys.map(roi_lookup)
    df_tidy = df_tidy[['roi_label_id', 'roi_name', 'volume']]
    df_tidy['roi_label_id'] = df_tidy['roi_label_id'].astype('Int64')
    df_tidy.to_csv(csv_path, index=False, header=True)
    
# CLI to transform the SynthSeg volumes CSV to the tidy format.
# Requires input volumes file (CSV).
# Author: Antonio Scardace

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--csv_path', type=str, required=True)
    args = parser.parse_args()

    synthseg_csv_to_tidy(args.csv_path)