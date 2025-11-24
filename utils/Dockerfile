FROM python:3.12-slim

LABEL maintainer="Antonio Scardace <antonio.scardace@phd.unict.it>"

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PATH="/app:${PATH}"

RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
        pandas==2.2.3 \
        numpy==1.26.4 \
        nibabel==5.3.2 \
        scipy==1.16.3

COPY . /app/

RUN chmod +x /app/*.py && \
    ln -s /app/skullstrip_and_clean.py /usr/local/bin/skullstrip_and_clean && \
    ln -s /app/pet_extract_roi_features.py /usr/local/bin/pet_extract_roi_features && \
    ln -s /app/pet_normalize_suvr.py /usr/local/bin/pet_normalize_suvr && \
    ln -s /app/synthseg_one_hot.py /usr/local/bin/synthseg_one_hot && \
    ln -s /app/synthseg_tidy.py /usr/local/bin/synthseg_tidy

CMD ["bash"]