import logging, configparser

logger = logging.getLogger("IndiBotLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
fh = logging.FileHandler('IndiBot.log', 'w+')
fh.setFormatter(formatter)
fh.setLevel(logging.INFO)
logger.addHandler(fh)

log = logging.getLogger("IndiBotLog")

# Read properties from app.ini
configParser = configparser.ConfigParser()
configParser.read("app.ini")
props = dict(configParser.items("DEFAULT"))
