import yaml, logging, logging.handlers, os, sys
from playhouse.pool import PooledMySQLDatabase
from playhouse.sqlite_ext import SqliteExtDatabase
from datetime import datetime, UTC, timezone

UNIXTIME = int(datetime.now(UTC).timestamp())
unixtime_to_date = lambda uts, fmt: datetime.fromtimestamp(uts, timezone.utc).strftime(fmt)

uagents = {
    "chrome_linux": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
}

def get_config(location):
    with open(location, 'r') as f:
        config = yaml.full_load(f)
        return config


def create_dir(location):
    dirname = os.path.dirname(location)
    if not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)
    return dirname


def get_logger(log_config):
    logger = logging.getLogger("pyapp")
    log_file = "{}/{}".format(log_config['root'], log_config['name'])
    lf = create_dir(log_file)
    fmtr = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    hdlr = logging.handlers.WatchedFileHandler(log_file)
    hdlr.setFormatter(fmtr)
    logger.addHandler(hdlr)
    logger.setLevel(log_config.get('level', 'INFO'))
    return logger

def get_logger_file(logger):
    try:
        lh = logger.handlers[0]
        lf = lh.baseFilename
        return lf
    except Exception as e:
        return ""


def connect_mysqldb(db_config):
    db_params = {}
    try:
        for key in ['host', 'port', 'user', 'passwd', 'max_connections', 'stale_timeout', 'timeout', 'use_unicode', 'charset']:
            db_params[key] = db_config[key]
        db = PooledMySQLDatabase(db_config['name'], **db_params)
    except Exception as e:
        raise e
    return db


def connect_sqlitedb(db_config):
    pragmas = {}
    try:
        for key in ['journal_mode', 'cache_size', 'foreign_keys', 'ignore_check_constraints', 'synchronous']:
            pragmas[key] = db_config[key]
        db_name = db_config['name'].format(UNIXTIME=UNIXTIME)
        db_path = "{}/{}".format(db_config['path'], db_name)
        db = SqliteExtDatabase(db_path, pragmas=pragmas, timeout=db_config['timeout'])
    except Exception as e:
        raise e
    return db

# simple argparse
def parse_args(argv):
    # sys.argv is a list of args, we manually parse each element here
    kwargs = dict(arg.split('=') for arg in argv)
    for k, v in kwargs.items():
        print(f"{k}: {v}")
    return kwargs
