import os
import psutil
import argparse
import subprocess
import pandas as pd

from tqdm import tqdm

# Fully CPU-based preprocessing pipeline for paired sMRI and PET data.
# Given a T1w sMRI scan and the PET acquisition from the same visit, it produces a set of outputs.
# The final outputs comprise around 100 ROIs based on the Desikan–Killiany atlas.
# Author: Antonio Scardace

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--keep',        action='store_true') 
    parser.add_argument('--no_stdout',   action='store_true')
    parser.add_argument('--no_stderr',   action='store_true')
    parser.add_argument('--skip_pvc',    action='store_true')
    parser.add_argument('--skip_suvr',   action='store_true')
    parser.add_argument('--dataset_csv', type=str, required=True)
    parser.add_argument('--template',    type=str, required=True)
    parser.add_argument('--n_threads',   type=int, default=psutil.cpu_count(logical=False))
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    mri_script = os.path.join(base_dir, 'preproc_mri.sh')
    pet_script = os.path.join(base_dir, 'preproc_pet.sh')
    stdout_val = None if args.verbose else subprocess.DEVNULL
    threads = str(args.n_threads)

    if not os.path.exists(args.dataset_csv):
        raise ValueError('Dataset file not found')

    if not os.path.exists(args.template):
        raise ValueError('Template file not found')

    # Resolves absolute paths for the Bash execution scripts relative to this file.
    # Ensures pipeline scripts are located correctly regardless of the working directory.
    # Then runs the preprocessing scripts.

    df = pd.read_csv(args.dataset_csv)
    grouped = df.groupby(['subject_id', 'visit_number'])

    for (subject, visit), group_df in tqdm(grouped, 'Visits Analysis', len(grouped)):

        print('Preprocessing', subject, 'in visit', visit)
        mri_scan = group_df[group_df['modality'] == 'MRI'].iloc[0]
        pet_scan = group_df[group_df['modality'] == 'PET'].iloc[0]
        os.makedirs(mri_scan['preproc_dir'], exist_ok=True)
        os.makedirs(pet_scan['preproc_dir'], exist_ok=True)

        print('Preprocessing sMRI')
        subprocess.run(check=True, stdout=stdout_val, args=[
            mri_script, threads, mri_scan['raw_path'], args.template, mri_scan['preproc_dir']
        ])
        
        print('Preprocessing PET')
        subprocess.run(check=True, stdout=stdout_val, args=[
            pet_script, pet_scan['raw_path'], mri_scan['preproc_dir'], args.template, pet_scan['preproc_dir']
        ])