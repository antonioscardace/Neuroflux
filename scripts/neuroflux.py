import os
import psutil
import argparse
import subprocess

# Script to preprocess sMRI and PET scans.
# Author: Antonio Scardace

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose',        action='store_true')
    parser.add_argument('--mri_path',       type=str, required=True)
    parser.add_argument('--pet_path',       type=str, required=True)
    parser.add_argument('--template_path',  type=str, required=True)
    parser.add_argument('--mri_output_dir', type=str, required=True)
    parser.add_argument('--pet_output_dir', type=str, required=True)
    parser.add_argument('--n_threads',      type=int, default=psutil.cpu_count(logical=False))
    args = parser.parse_args()

    # Checks if input paths exist.
    # Validates thread count.

    if not os.path.exists(args.mri_path):
        raise ValueError('sMRI file not found.')
    
    if not os.path.exists(args.pet_path):
        raise ValueError('PET file not found.')

    if not os.path.exists(args.template_path):
        raise ValueError('Template file not found.')
    
    os.makedirs(args.mri_output_dir, exist_ok=True)
    os.makedirs(args.pet_output_dir, exist_ok=True)

    # Resolves absolute paths for the Bash execution scripts relative to this file.
    # Ensures pipeline scripts are located correctly regardless of the working directory.
    # Then runs the preprocessing scripts.

    base_dir = os.path.dirname(os.path.abspath(__file__))
    mri_script = os.path.join(base_dir, 'preproc_mri.sh')
    pet_script = os.path.join(base_dir, 'preproc_pet.sh')
    stdout_val = None if args.verbose else subprocess.DEVNULL
    threads = str(args.n_threads)

    print('Preprocessing sMRI')
    subprocess.run(check=True, stdout=stdout_val, args=[
        mri_script, threads, args.mri_path, args.template_path, args.mri_output_dir
    ])
    
    print('Preprocessing PET')
    subprocess.run(check=True, stdout=stdout_val, args=[
        pet_script, args.pet_path, args.mri_output_dir, args.template_path, args.pet_output_dir
    ])