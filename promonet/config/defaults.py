import functools
import os
from pathlib import Path

import GPUtil
import torch


###############################################################################
# Metadata
###############################################################################


# Configuration name
CONFIG = 'promonet'


###############################################################################
# Audio parameters
###############################################################################


# Minimum and maximum frequency
FMIN = 50.  # Hz
FMAX = 550.  # Hz

# Audio hopsize
HOPSIZE = 256  # samples

# Minimum decibel level
MIN_DB = -100.

# Number of melspectrogram channels
NUM_MELS = 80

# Number of spectrogram channels
NUM_FFT = 1024

# Reference decibel level
REF_DB = 20.

# Audio sample rate
SAMPLE_RATE = 22050  # Hz

# Number of spectrogram channels
WINDOW_SIZE = 1024


###############################################################################
# Data parameters
###############################################################################


# Whether to perform speaker adaptation (instead of multi-speaker)
ADAPTATION = True

# All features considered during preprocessing
ALL_FEATURES = [
    'loudness',
    'periodicity',
    'pitch',
    'ppg',
    'spectrogram']

# Whether to use loudness augmentation
AUGMENT_LOUDNESS = False

# Whether to use pitch augmentation
AUGMENT_PITCH = False

# Maximum ratio for pitch augmentation
AUGMENTATION_RATIO_MAX = 2.

# Minimum ratio for pitch augmentation
AUGMENTATION_RATIO_MIN = .5

# Condition discriminators on speech representation
# TODO
CONDITION_DISCRIM = False

# Names of all datasets
DATASETS = ['daps', 'libritts', 'vctk']

# Default periodicity threshold of the voiced/unvoiced decision
VOICING_THRESOLD = .1625

# Whether to use an embedding layer for pitch
PITCH_EMBEDDING = True

# Number of pitch bins
PITCH_BINS = 256

# Embedding size used to represent each pitch bin
PITCH_EMBEDDING_SIZE = 64

# Number of channels in the phonetic posteriorgram features
PPG_CHANNELS = 40

# Type of interpolation method to use to scale PPG features
# Available method are ['linear', 'nearest', 'slerp']
PPG_INTERP_METHOD = 'slerp'

# Type of sparsification used for ppgs
# One of ['constant', 'percentile', 'topk', None]
SPARSE_PPG_METHOD = None

# Threshold for ppg sparsification.
# In [0, 1] for 'contant' and 'percentile'; integer > 0 for 'topk'.
SPARSE_PPG_THRESHOLD = 0.8

# Number of top bins to take in ppg sparsification
SPARSE_PPG_THRESHOLD = 3

# Seed for all random number generators
RANDOM_SEED = 1234

# Only use spectral features
SPECTROGRAM_ONLY = False

# Dataset to use for training
TRAINING_DATASET = 'vctk'

# Whether to use variable-width pitch bins
VARIABLE_PITCH_BINS = False


###############################################################################
# Directories
###############################################################################


# Root location for saving outputs
# TEMPORARY
ROOT_DIR = Path(__file__).parent.parent.parent
# ROOT_DIR = Path('/files10/max/promonet')

# Location to save assets to be bundled with pip release
# TEMPORARY
ASSETS_DIR = Path(__file__).parent.parent / 'assets'
# ASSETS_DIR = Path('/files10/max/promonet/promonet/assets')

# Location of preprocessed features
# TEMPORARY
CACHE_DIR = ROOT_DIR / 'data' / 'cache'
# CACHE_DIR = Path('/files10/max/promonet/data/cache')

# Location of datasets on disk
DATA_DIR = ROOT_DIR / 'data' / 'datasets'

# Location to save evaluation artifacts
EVAL_DIR = ROOT_DIR / 'eval'

# Location to save results
RESULTS_DIR = ROOT_DIR / 'results'

# Location to save training and adaptation artifacts
RUNS_DIR = ROOT_DIR / 'runs'


###############################################################################
# Evaluation parameters
###############################################################################


# Error threshold beyond which a frame of loudness is considered incorrect
ERROR_THRESHOLD_LOUDNESS = 6.  # decibels

# Error threshold beyond which a frame of periodicity is considered incorrect
ERROR_THRESHOLD_PERIODICITY = .1

# Error threshold beyond which a frame of pitch is considered incorrect
ERROR_THRESHOLD_PITCH = 50.  # cents

# Error threshold beyond which a frame of PPG is considered incorrect
ERROR_THRESHOLD_PPG = .1  # JSD

# Evaluation ratios for pitch-shifting, time-stretching, and loudness-scaling
EVALUATION_RATIOS = [.717, 1.414]


###############################################################################
# Logging parameters
###############################################################################


# Number of steps between saving checkpoints
CHECKPOINT_INTERVAL = 20000  # steps

# Number of steps between logging to Tensorboard
EVALUATION_INTERVAL = 2500  # steps

# Number of steps to perform for tensorboard logging
DEFAULT_EVALUATION_STEPS = 16

# Number of examples to plot while evaluating during training
PLOT_EXAMPLES = 10


###############################################################################
# Loss parameters
###############################################################################


# Weight applied to the discriminator loss
ADVERSARIAL_LOSS_WEIGHT = 1.

# Weight applied to the feature matching loss
FEATURE_MATCHING_LOSS_WEIGHT = 1.

# Whether to omit the first activation of each discriminator
FEATURE_MATCHING_OMIT_FIRST = False

# Weight applied to the melspectrogram loss
MEL_LOSS_WEIGHT = 45.

# Whether to use multi-mel loss
MULTI_MEL_LOSS = False

# Window sizes to be used in the multi-scale mel loss
MULTI_MEL_LOSS_WINDOWS = [32, 64, 128, 256, 512, 1024, 2048]


###############################################################################
# Model parameters
###############################################################################


# The size of intermediate feature activations
HIDDEN_CHANNELS = 512

# Input features
INPUT_FEATURES = ['loudness', 'periodicity', 'pitch', 'ppg']

# Whether to use FiLM for global conditioning
FILM_CONDITIONING = False

# Hidden dimension channel size
FILTER_CHANNELS = 768

# Convolutional kernel size
KERNEL_SIZE = 3

# (Negative) slope of leaky ReLU activations
LRELU_SLOPE = .1

# The model to use. One of ['psola', 'vocoder', 'world']
MODEL = 'vocoder'

# Whether to use the multi-resolution spectrogram discriminator from UnivNet
MULTI_RESOLUTION_DISCRIMINATOR = False

# Whether to use the multi-scale waveform discriminator from MelGAN
MULTI_SCALE_DISCRIMINATOR = True

# Whether to use the complex multi-band discriminator from RVQGAN
COMPLEX_MULTIBAND_DISCRIMINATOR = False

# Number of attention heads
N_HEADS = 2

# Number of attention layers
N_LAYERS = 5

# Dropout probability
P_DROPOUT = .1

# Kernel sizes of residual block
RESBLOCK_KERNEL_SIZES = [3, 7, 11]

# Dilation rates of residual block
RESBLOCK_DILATION_SIZES = [[1, 3, 5], [1, 3, 5], [1, 3, 5]]

# Whether to use snake activation in the audio generator
# TODO
SNAKE = False

# Speaker embedding size
SPEAKER_CHANNELS = 256

# Initial channel size for upsampling layers
UPSAMPLE_INITIAL_SIZE = 512

# Kernel sizes of upsampling layers
UPSAMPLE_KERNEL_SIZES = [16, 16, 4, 4]

# Upsample rates of residual blocks
UPSAMPLE_RATES = [8, 8, 2, 2]

# Type of vocoder, one of ['hifigan', 'vocos']
VOCODER_TYPE = 'vocos'

# Model architecture to use for vocos vocoder.
# One of ['convnext', 'transformer'].
VOCOS_ARCHITECTURE = 'convnext'


###############################################################################
# Training parameters
###############################################################################


# Maximum number of frames in a batch
MAX_TRAINING_FRAMES = 100000

# Number of buckets to partition training and validation data into based on
# length to avoid excess padding
BUCKETS = 1

# Size in samples of discriminator inputs
CHUNK_SIZE = 16384

# Gradients above this value are clipped to this value
GRADIENT_CLIP_GENERATOR = None

# Number of training steps
STEPS = 200000

# Number of adaptation steps
ADAPTATION_STEPS = 10000

# Number of data loading worker threads
# TEMPORARY
# try:
#     NUM_WORKERS = int(os.cpu_count() / max(1, len(GPUtil.getGPUs())))
# except ValueError:
#     NUM_WORKERS = os.cpu_count()
NUM_WORKERS = 8

# Training optimizer
# TODO
OPTIMIZER = functools.partial(
    torch.optim.AdamW,
    lr=2e-4,
    betas=(.8, .9),
    eps=1e-9)
