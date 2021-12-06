import torch
import torchaudio
import tqdm

import promovits


###############################################################################
# Constants
###############################################################################


# PPG model checkpoint file
CHECKPOINT_FILE = promovits.ASSETS_DIR / 'checkpoints' / 'ppg.pt'

# PPG model configuration
CONFIG_FILE = promovits.ASSETS_DIR / 'configs' / 'ppg.yaml'

# Sample rate of the PPG model
SAMPLE_RATE = 16000


###############################################################################
# Phonetic posteriorgram
###############################################################################


def from_audio(
    audio,
    sample_rate=promovits.SAMPLE_RATE,
    config=CONFIG_FILE,
    checkpoint_file=CHECKPOINT_FILE,
    gpu=None):
    """Compute PPGs from audio"""
    device = torch.device('cpu' if gpu is None else f'cuda:{gpu}')

    # Cache model
    if not hasattr(from_audio, 'model'):
        from_audio.model = promovits.preprocess.ppg.conformer_ppg_model.build_ppg_model.load_ppg_model(
        config,
        checkpoint_file,
        device)

    # Maybe resample
    if sample_rate != SAMPLE_RATE:
        resample_fn = torchaudio.transforms.Resample(
            sample_rate,
            SAMPLE_RATE)
        audio = resample_fn(audio)

    # Setup features
    audio = audio.to(device)
    length = torch.tensor([audio.shape[-1]], dtype=torch.long, device=device)

    # Infer ppgs
    with torch.no_grad():
        return from_audio.model(audio, length).T.cpu()


def from_file(audio_file, gpu=None):
    """Compute PPGs from audio file"""
    return from_audio(promovits.load.audio(audio_file), gpu=gpu)


def from_file_to_file(audio_file, output_file, gpu=None):
    """Compute PPGs from audio file and save to disk"""
    ppg = from_file(audio_file, gpu)
    torch.save(ppg, output_file)


def from_files_to_files(audio_files, output_files, gpu=None):
    """Compute PPGs from audio files and save to disk"""
    iterator = tqdm.tqdm(
        zip(audio_files, output_files),
        desc='Extracting PPGs',
        total=len(audio_files),
        dynamic_ncols=True)
    for audio_file, output_file in iterator:
        from_file_to_file(audio_file, output_file, gpu)
