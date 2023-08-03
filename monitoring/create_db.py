from sqlalchemy import create_engine

from utils.models import Base
from utils.utils import get_db_url
import logging

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG
)

if __name__ == "__main__":
    DATABASE_URL = get_db_url()
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    logging.info("Database has been created successfully")