<img src="docs/images/readme.png" alt="neuroflux"/>

<div align="center">
    <a href="https://img.shields.io/badge/Python-3.9-blue?style=for-the-badge" alt="Python"><img src="https://img.shields.io/badge/Python-3.9-blue?style=for-the-badge" alt="Python"></a>
    <a href="https://img.shields.io/badge/License-GPL--3.0-lightgrey?style=for-the-badge"><img src="https://img.shields.io/badge/License-GPL--3.0-orange?style=for-the-badge" alt="License"></a>
    <a href="https://github.com/antonioscardace/Neuroflux/actions/workflows/cd-docker-publish.yml"><img src="https://img.shields.io/github/actions/workflow/status/antonioscardace/Neuroflux/cd-docker-publish.yml?style=for-the-badge" alt="DockerHub Push"></a>
</div>
<br/>

neuroflux is a CPU-based preprocessing pipeline for paired structural MRI (**sMRI**) and **tau-PET** data, built on open-source neuroimaging tools. Given a T1w sMRI and a corresponding PET scan from the same visit, neuroflux performs automated preprocessing to generate standardized, analysis-ready derivatives in BIDS format. The resulting outputs include preprocessed MRI and PET (PVC-corrected and SUVR-normalized) scans, a brain mask, a multi-ROI segmentation based on the **Desikan–Killiany atlas**, and ROI-level volumetric and uptake features.

<p align="center"><img src="docs/images/output.png" width="50%" alt="neuroflux"/></p>

## Installation

The use of a dedicated virtual environment, like [Anaconda](https://www.anaconda.com/), is recommended to avoid dependency conflicts.<br/>
To run the entire pipeline, [Docker](https://docs.docker.com/get-docker/) is required.<br/>
Clone the repository and install the package in editable mode:

```console
git clone https://github.com/antonioscardace/neuroflux.git
cd neuroflux/
pip install -e .
```

## Usage

The input CSV file must contain at least four columns: `subject_id, image_uid, path, type`, where the latter specifies whether the image is an MRI or PET scan. Additional metadata can be included as optional columns, such as diagnosis, sex, age, acquisition_date, and PET-specific details such as the radiotracer and other acquisition parameters. MRI and PET scans should belong to the same subject and visit (within 6 months). To run the preprocessing, run the following command:

```console
python3 scripts/neuroflux.py \
  --mri_path PATH \
  --pet_path PATH \
  --template_path PATH \
  --mri_output_dir PATH \
  --path_output_dir PATH \
  --verbose \
  --keep_all
```

## Citations

```
[1] Avants et al. (2009): Advanced normalization tools (ANTs). The Insight Journal, 2(365), 1–35.
[2] Marcoux et al. (2018): An automated pipeline for the analysis of PET data on the cortical surface. Frontiers in Neuroinformatics.
[3] Isensee et al. (2019): Automated brain extraction of multi‑sequence MRI using artificial neural networks. Human Brain Mapping.
[4] López‑González et al. (2020): Intensity normalization methods in brain FDG‑PET quantification. NeuroImage, 222, 117229.
[5] Tustison et al. (2021): The ANTsX ecosystem for quantitative biological and medical imaging: ANTsR, ANTsPy, and deep learning. Nature Communications.
[6] Billot et al. (2023): SynthSeg: Segmentation of brain MRI scans of any contrast and resolution without retraining. Medical Image Analysis, 83, 102789.
```