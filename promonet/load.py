import json

import ppgs
import pypar
import torch
import torchaudio
import torchutil

import promonet


###############################################################################
# Loading utilities
###############################################################################


def audio(file):
    """Load audio from disk"""
    audio, sample_rate = torchaudio.load(file)

    # Maybe resample
    return promonet.resample(audio, sample_rate)


def features(prefix):
    """Load input features from file prefix"""
    return (
        torch.load(f'{prefix}-pitch.pt'),
        torch.load(f'{prefix}-periodicity.pt'),
        torch.load(f'{prefix}-loudness.pt'),
        torch.load(f'{prefix}-ppg.pt'))


def partition(dataset):
    """Load partitions for dataset"""
    with open(promonet.PARTITION_DIR / f'{dataset}.json') as file:
        return json.load(file)


def phonemes(file, interleave=False):
    """Load phonemes and interleave blanks"""
    # Load phonemes
    phonemes = torch.unique_consecutive(torch.load(file))[None]

    if not interleave:
        return phonemes

    # Interleave blanks
    interleaved = torch.full(
        (1, phonemes.shape[1] * 2 + 1),
        ppgs.PHONEME_TO_INDEX_MAPPING[pypar.SILENCE],
        dtype=phonemes.dtype)
    interleaved[:, 1::2] = phonemes

    return interleaved


def pitch_distribution(dataset=promonet.TRAINING_DATASET, partition='train'):
    """Load pitch distribution"""
    if not hasattr(pitch_distribution, 'distribution'):

        # Location on disk
        file = (
            promonet.ASSETS_DIR /
            'stats' /
            f'{dataset}-{partition}-pitch-{promonet.PITCH_BINS}.pt')

        try:

            # Load and cache distribution
            pitch_distribution.distribution = torch.load(file)

        except FileNotFoundError:

            # Get all voiced pitch frames
            allpitch = []
            for stem in torchutil.iterator(
                promonet.load.partition(dataset)[partition],
                'promonet.load.pitch_distribution'
            ):
                for pitch_file in (promonet.CACHE_DIR / dataset).glob(
                    f'{stem}*-pitch.pt'
                ):
                    pitch = torch.load(pitch_file)
                    periodicity = torch.load(
                        pitch_file.parent /
                        pitch_file.name.replace('pitch', 'periodicity'))
                    allpitch.append(
                        pitch[periodicity > promonet.VOICING_THRESOLD])

            # Sort
            pitch, _ = torch.sort(torch.cat(allpitch))

            # Bucket
            indices = torch.linspace(
                0.,
                len(pitch) - 1,
                promonet.PITCH_BINS,
                dtype=torch.float64
            ).to(torch.long)
            pitch_distribution.distribution = pitch[indices]
            pitch_distribution.distribution[0] = promonet.FMIN

            # Save
            torch.save(pitch_distribution.distribution, file)

    return pitch_distribution.distribution


def text(file):
    """Load text file"""
    with open(file, encoding='utf-8') as file:
        return file.read()
