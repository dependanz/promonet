MODULE = 'promonet'

# Configuration name
CONFIG = 'augment-multiband-varpitch-256-conddisc'

# Whether to use pitch augmentation
AUGMENT_PITCH = True

# Whether to use the complex multi-band discriminator from RVQGAN
COMPLEX_MULTIBAND_DISCRIMINATOR = True

# Condition discriminators on speech representation
CONDITION_DISCRIM = True

# Maximum number of frames in a batch
MAX_TRAINING_FRAMES = 60000

# Whether to use variable-width pitch bins
VARIABLE_PITCH_BINS = True