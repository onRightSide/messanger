import logging


logger = logging.getLogger("server_logger.log")

form = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s")

fh = logging.FileHandler("log/server.log", encoding='utf-8')
fh.setLevel(logging.DEBUG)
fh.setFormatter(form)

logger.addHandler(fh)
logger.setLevel(logging.DEBUG)

