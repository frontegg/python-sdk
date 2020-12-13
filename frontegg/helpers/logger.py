import logging
import os
logger = logging.getLogger('Frontegg')
format = logging.Formatter('[Frontegg:%(levelname)s]: %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(format)
logger.addHandler(sh)

debug = os.environ.get('FRONTEGG_DEBUG')

if debug:
    logger.setLevel(logging.DEBUG)
