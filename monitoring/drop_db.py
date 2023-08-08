# pylint: disable=invalid-name,duplicate-code
import logging

from sqlalchemy import create_engine
from utils.utils import get_db_url
from utils.models import Base

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)


def main():
    """
    Drop the database if the database exists
    """
    DATABASE_URL = get_db_url()
    engine = create_engine(DATABASE_URL)
    Base.metadata.drop_all(engine)
    logging.info("Database has been dropped successfully")


if __name__ == "__main__":
    main()
