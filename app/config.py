import logging
import os


class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


    @classmethod
    def setup_logging(cls):
        logging.basicConfig(level=cls.LOG_LEVEL,
                            format=cls.LOG_FORMAT,
                            force=True
                            )

        logger = logging.getLogger(__name__)
        logger.info("logging initialized at %s level", cls.LOG_LEVEL)
