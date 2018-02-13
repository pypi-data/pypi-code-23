from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .dbobjects import Base, Question, User, Meal, Score
import pkg_resources

db_path = pkg_resources.resource_filename('nuqui', 'data/nuqui.db')
engine = create_engine('sqlite:///'+db_path)
Base.metadata.bind = engine
SESSION = sessionmaker(bind=engine)
Base.metadata.create_all()
session = SESSION()
session.close()

from .nuqui import remove_user, create_user, add_meal, evaluate, get_predefined_question_dict_with_random_answers, get_score
