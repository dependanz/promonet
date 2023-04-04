# Runs all experiments in the paper
# "Adaptive Neural Speech Prosody Editing"

# Args
# $1 - index of GPU to use

# Download datasets
python -m promonet.data.download

# Setup experiments
python -m promonet.data.augment
python -m promonet.data.preprocess --features spectrogram ppg prosody --gpu $1
python -m promonet.partition

# First pass experiments trainings and evaluations
python -m promonet.train --config config/base.py --gpus $1
python -m promonet.train --config config/conddisc.py --gpus $1
python -m promonet.train --config config/conddisc-condgen.py --gpus $1
python -m promonet.train --config config/conddisc-condgen-augment.py --gpus $1
python -m promonet.train --config config/conddisc-condgen-augment-snake.py --gpus $1

# Baseline trainings and evaluations
# python -m promonet.train --config config/promovoco.py --gpus $1
# python -m promonet.train --config config/spectral.py --gpus $1
# python -m promonet.train --config config/spectral-voco.py --gpus $1
# python -m promonet.train --config config/two-stage.py --gpus $1
# python -m promonet.train --config config/vits.py --gpus $1

# DSP-based baseline evaluations
python -m promonet.evaluate --config config/psola.py
python -m promonet.evaluate --config config/world.py
