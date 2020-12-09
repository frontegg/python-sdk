import logging
logger = logging.getLogger('Frontegg')
format = logging.Formatter('[Frontegg:%(levelname)s]: %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(format)
logger.addHandler(sh)