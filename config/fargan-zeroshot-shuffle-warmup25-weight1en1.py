MODULE = 'promonet'

# Configuration name
CONFIG = 'fargan-zeroshot-shuffle-warmup25-weight1en1'

# The model to use.
# One of ['fargan', 'hifigan', 'vocos', 'world'].
MODEL = 'fargan'

# Step to start using adversarial loss
ADVERSARIAL_LOSS_START_STEP = 300000

# Weight applied to the discriminator loss
ADVERSARIAL_LOSS_WEIGHT = .1

# Training batch size
BATCH_SIZE = 256

# Training sequence length
CHUNK_SIZE = 4096  # samples

# Step to start training discriminator
DISCRIMINATOR_START_STEP = 275000

# Whether to use mel spectrogram loss
MEL_LOSS = False

# Whether to use multi-resolution spectral convergence loss
SPECTRAL_CONVERGENCE_LOSS = True

# Whether to use WavLM x-vectors for zero-shot speaker conditioning
ZERO_SHOT = True

# Whether to shuffle speaker embeddings during training
ZERO_SHOT_SHUFFLE = True
