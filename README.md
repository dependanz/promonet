<h1 align="center">Prosody Modification Network (ProMoNet)</h1>
<div align="center">

[![PyPI](https://img.shields.io/pypi/v/promonet.svg)](https://pypi.python.org/pypi/promonet)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/promonet)](https://pepy.tech/project/promonet)

</div>

Official code for the paper _Adaptive Neural Speech Prosody Editing_
[[paper]](https://www.maxrmorrison.com/pdfs/morrison2023adaptive.pdf)
[[companion website]](https://www.maxrmorrison.com/sites/promonet/)


## Table of contents

- [Installation](#installation)
- [Usage](#usage)
    * [Example](#example)
    * [Adaptation](#adaptation)
    * [Generation](#generation)
- [Training](#training)
    * [Download](#download)
    * [Preprocess](#preprocess)
    * [Partition](#partition)
    * [Train](#train)
    * [Monitor](#monitor)
    * [Evaluate](#evaluate)
- [Citation](#citation)


## Installation

`pip install promonet`


## Usage

### Example

To use `promonet` for speech prosody editing, you must first perform speaker
adaptation on a dataset of recordings of the target speaker. You can then use
the resulting model checkpoint to perform prosody modification in the target
speaker's voice. All of this can be done using either the API or CLI.

#### Application programming interface (API)

```
import promonet


###############################################################################
# Speaker adaptation
###############################################################################


# Speaker's name
name = 'max'

# Directory containing wav files for adaptation
directory = promonet.DATA_DIR / name

# GPU indices to use for training
gpus = [0]

# Perform speaker adaptation
checkpoint = promonet.adapt.speaker(name, directory, gpus=gpus)


###############################################################################
# Prosody editing
###############################################################################


# Load audio for prosody editing
audio = promonet.load.audio('test.wav')

# Get prosody features to edit
pitch, loudness = promonet.preprocess(audio, gpu=gpus[0])

# (Optional) If you have the text transcript, you can edit phoneme
#            durations using a forced alignment representation
pitch, loudness, alignment = promonet.preprocess(
    audio,
    text=promonet.load.text('test.txt'),
    gpu=gpus[0])

# We'll use a ratio of 2.0 for all prosody editing examples
ratio = 2.0

# Perform pitch-shifting
target_pitch = ratio * pitch
shifted = promonet.from_audio(
    audio,
    target_pitch=target_pitch,
    checkpoint=checkpoint,
    gpu=gpus[0])

# Perform time-stretching
alignment.update(
    durations=[ratio * p.duration() for p in target_alignment.phonemes()])
stretched = promonet.from_audio(
    audio,
    target_alignment=alignment,
    checkpoint=checkpoint,
    gpu=gpus[0])

# Perform loudness-scaling
target_loudness = 10 * math.log2(ratio) + loudness
scaled = promonet.from_audio(
    audio,
    target_loudness=target_loudness,
    checkpoint=checkpoint,
    gpu=gpus[0])
```


#### Command-line interface (CLI)

**TODO**


### Adaptation

#### Application programming interface (API)

##### `promonet.from_`

**TODO**


##### `promonet.from_file`

**TODO**


##### `promonet.from_file_to_file`

**TODO**


##### `promonet.from_files_to_files`

**TODO**


#### Command-line interface (CLI)


### Generation

#### Application programming interface (API)

##### `promonet.from_`

**TODO**


##### `promonet.from_file`

**TODO**


##### `promonet.from_file_to_file`

**TODO**


##### `promonet.from_files_to_files`

**TODO**


#### Command-line interface (CLI)

**TODO**

```
python -m promonet
    [-h]
    [--config CONFIG]
    --audio_files AUDIO_FILES [AUDIO_FILES ...]
    --output_files OUTPUT_FILES [OUTPUT_FILES ...]
    [--target_alignment_files TARGET_ALIGNMENT_FILES [TARGET_ALIGNMENT_FILES ...]]
    [--target_loudness_files TARGET_LOUDNESS_FILES [TARGET_LOUDNESS_FILES ...]]
    [--target_periodicity_files TARGET_PERIODICITY_FILES [TARGET_PERIODICITY_FILES ...]]
    [--target_pitch_files TARGET_PITCH_FILES [TARGET_PITCH_FILES ...]]
    [--checkpoint CHECKPOINT]
    [--gpu GPU]

Perform prosody editing

required arguments:
  --audio_files AUDIO_FILES [AUDIO_FILES ...]
                        The audio files to process
  --output_files OUTPUT_FILES [OUTPUT_FILES ...]
                        The files to save the output audio

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG       The configuration file
  --target_alignment_files TARGET_ALIGNMENT_FILES [TARGET_ALIGNMENT_FILES ...]
                        The files with the target phoneme alignment
  --target_loudness_files TARGET_LOUDNESS_FILES [TARGET_LOUDNESS_FILES ...]
                        The files with the per-frame target loudness
  --target_periodicity_files TARGET_PERIODICITY_FILES [TARGET_PERIODICITY_FILES ...]
                        The files with the per-frame target periodicity
  --target_pitch_files TARGET_PITCH_FILES [TARGET_PITCH_FILES ...]
                        The files with the per-frame target pitch
  --checkpoint CHECKPOINT
                        The generator checkpoint
  --gpu GPU             The index of the gpu to use for generation
```



## Training

### Download

Downloads, unzips, and formats datasets. Stores datasets in `data/datasets/`.
Stores formatted datasets in `data/cache/`.

```
python -m promonet.data.download --datasets <datasets>
```


### Preprocess

Prepares features for training. Features are stored in `data/cache/`.

```
python -m promonet.data.preprocess --datasets <datasets> --gpu <gpu>
```


### Partition

Partitions a dataset. You should not need to run this, as the partitions
used in our work are provided for each dataset in
`promonet/assets/partitions/`.

```
python -m promonet.partition --datasets <datasets>
```


### Train

Trains a model. Checkpoints and logs are stored in `runs/`.

```
python -m promonet.train \
    --config <config> \
    --dataset <dataset> \
    --gpus <gpus>
```

If the config file has been previously run, the most recent checkpoint will
automatically be loaded and training will resume from that checkpoint.


### Monitor

You can monitor training via `tensorboard` as follows.

```
tensorboard --logdir runs/train/ --port <port>
```


### Evaluate

Performs objective evaluation and generates examples for subjective evaluation.
Also performs benchmarking of generation speed. Results are stored in `eval/`.

```
python -m promonet.evaluate \
    --config <name> \
    --datasets <datasets> \
    --gpus <gpus>
```


## Citation

### IEEE
M. Morrison and B. Pardo, "Adaptive Neural Speech Prosody Editing," Submitted
to ICML 2023, July 2023.


### BibTex

```
@inproceedings{morrison2023adaptive,
    title={Adaptive Neural Speech Prosody Editing},
    author={Morrison, Max and Pardo, Bryan},
    booktitle={Submitted to ICML 2023},
    month={July},
    year={2023}
}
```
