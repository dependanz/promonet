MODULE = 'promonet'

# Configuration name
CONFIG = 'mel-ppg'

# The model to use. One of [
#     'end-to-end',
#     'hifigan',
#     'psola',
#     'two-stage',
#     'vits',
#     'vocoder',
#     'world'
# ]
MODEL = 'end-to-end'

# Pitch conditioning
PITCH_FEATURES = True
PITCH_EVAL_METHOD = 'cents'

# Phonemic posteriorgram conditioning
PPG_FEATURES = True
PPG_MODEL = 'mel-ppg'
PPG_CHANNELS = 40

ADAPTATION=False