from sqlalchemy import create_engine
from utils.models import PredictionTable
from utils.db_utils import open_sqa_session
from utils.utils import get_db_url

def save_predictions(prediction) -> None:
    """Save predictions to database.

    Args:
        predictions (pd.DataFrame): Pandas dataframe with predictions column.
    """
    DATABASE_URI = get_db_url()
    engine = create_engine(DATABASE_URI)
    session = open_sqa_session(engine)
    session.add_all([
        PredictionTable(**prediction)
    ])
    session.commit()