from flask import Flask

from app.mover import mover
from pkg.config import Config
from pkg.sftp import SFTPConfig
from util.service_logging import log

app = Flask(__name__)


def load_config(app: Flask) -> None:
    sftp_config = SFTPConfig.from_env()
    config = Config.from_env()
    if sftp_config.survey_source_path == "":
        log.error("survey_source_path is blank")
        raise Exception("survey_source_path is blank")
    config.log()
    sftp_config.log()
    app.nisra_config = config
    app.sftp_config = sftp_config


app.register_blueprint(mover)


log.info("Application started")
