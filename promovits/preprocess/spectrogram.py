import functools
import multiprocessing as mp

import torch
import librosa

import promovits


###############################################################################
# Spectrogram computation
###############################################################################


def from_audio(audio, mels=False):
    """Compute spectrogram from audio"""
    # Cache hann window
    if not hasattr(from_audio, 'window'):
        from_audio.window = torch.hann_window(
            promovits.WINDOW_SIZE,
            dtype=audio.dtype,
            device=audio.device)

    # Pad audio
    size = (promovits.NUM_FFT - promovits.HOPSIZE) // 2
    audio = torch.nn.functional.pad(
        audio,
        (size, size),
        mode='reflect')

    # Compute stft
    stft = torch.stft(
        audio,
        promovits.NUM_FFT,
        hop_length=promovits.HOPSIZE,
        window=from_audio.window,
        center=False,
        normalized=False,
        onesided=True)

    # Compute magnitude
    spectrogram = torch.sqrt(stft.pow(2).sum(-1) + 1e-6)

    # Maybe convert to mels
    spectrogram = linear_to_mel(spectrogram) if mels else spectrogram

    return spectrogram[0]


def from_file(audio_file, mels=False):
    """Compute spectrogram from audio file"""
    audio = promovits.load.audio(audio_file)
    return from_audio(audio, mels)


def from_file_to_file(audio_file, output_file, mels=False):
    """Compute spectrogram from audio file and save to disk"""
    output = from_file(audio_file, mels)
    torch.save(output, output_file)


def from_files_to_files(audio_files, output_files, mels=False):
    """Compute spectrogram from audio files and save to disk"""
    preprocess_fn = functools.partial(from_file_to_file, mels=mels)
    with mp.Pool() as pool:
        pool.starmap(preprocess_fn, zip(audio_files, output_files))


###############################################################################
# Utilities
###############################################################################


def linear_to_mel(spectrogram):
    # Create mel basis
    if not hasattr(linear_to_mel, 'mel_basis'):
        basis = librosa.filters.mel(
            promovits.SAMPLE_RATE,
            promovits.NUM_FFT,
            promovits.NUM_MELS)
        basis = torch.from_numpy(basis)
        basis = basis.to(spectrogram.dtype).to(spectrogram.device)
        linear_to_mel.basis = basis

    # Convert to mels
    melspectrogram = torch.matmul(linear_to_mel.basis, spectrogram)

    # Apply dynamic range compression
    return torch.log(torch.clamp(melspectrogram, min=1e-5))
