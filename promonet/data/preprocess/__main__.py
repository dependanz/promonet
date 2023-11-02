import yapecs

import promonet


###############################################################################
# Preprocess datasets
###############################################################################


def parse_args():
    parser = yapecs.ArgumentParser(description='Preprocess datasets')
    parser.add_argument(
        '--datasets',
        nargs='+',
        choices=promonet.DATASETS,
        help='The datasets to preprocess')
    parser.add_argument(
        '--features',
        default=promonet.ALL_FEATURES,
        choices=promonet.ALL_FEATURES,
        nargs='+',
        help='The features to preprocess')
    parser.add_argument(
        '--gpu',
        type=int,
        help='The index of the gpu to use')
    return parser.parse_args()


promonet.data.preprocess.datasets(**vars(parse_args()))
