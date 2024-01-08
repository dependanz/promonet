from encodec import EncodecModel

MODULE = 'ppgs'

# Configuration name
CONFIG = 'encodec'

def _frontend(device='cpu'):
    import torch
    quantizer = EncodecModel.encodec_model_24khz().quantizer
    quantizer.to(device)

    def _quantize(batch: torch.Tensor):
        with torch.no_grad():
            batch = batch.to(torch.int)
            batch = batch.transpose(0, 1)
            return quantizer.decode(batch)

    return _quantize

# This function takes as input a torch.Device and returns a callable frontend
FRONTEND = _frontend

# Network width
HIDDEN_CHANNELS = 256

# Dimensionality of input representation
INPUT_CHANNELS = 128

# Number of hidden layers
NUM_HIDDEN_LAYERS = 5

# Input representation
REPRESENTATION = 'encodec'

# Local checkpoint to use
# If None, Huggingface will be used unless a checkpoint is given in the CLI
LOCAL_CHECKPOINT = f'/repos/ppgs/runs/{CONFIG}/00200000.pt'
