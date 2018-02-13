# a quiz app that tooks the question from http://www.jservice.io/ and put it into the db with https://github.com/nuqui-chatbot/nuqui-question-database
from .dbobjects import User, Score, Question, Meal
from . import SESSION
from random import randint, shuffle
import datetime


def create_user(user_id, user_name):
    session = SESSION()
    user_score = Score(points=0, latest_points=0)
    user = User(id=user_id, name=user_name, score=user_score)
    session.add(user_score)
    session.add(user)
    session.commit()
    session.close()


def remove_user(user_id):
    session = SESSION()
    user = session.query(User).filter_by(id=user_id).one()
    session.delete(user)
    session.commit()
    session.close()


def get_predefined_question_dict_with_random_answers(user_id):
    # get the questions the user already answered and delete them from the list of possible questions
    session = SESSION()
    user = session.query(User).filter_by(id=user_id).one()
    questions_id = user.questions
    all_qustions = session.query(Question).all()
    possible_questions = []
    # select question form list of possible questions where one of users last 10 meals has relation to
    last_ten_meals = user.meals[-10:]
    if last_ten_meals is not None:
        # _get_ingredient_list(last_ten_meals)
        ingred_last_meals = _get_ingredient_list(last_ten_meals)

        for ing in ingred_last_meals:
            possible_questions.extend(session.query(Question).filter(Question.answer.like("%" + ing + "%")).all())
            possible_questions.extend(session.query(Question).filter(Question.question.like("%" + ing + "%")).all())
    else:
        possible_questions = [question for question in all_qustions if question not in questions_id]

    # select random question from list of possible questions
    question = possible_questions[randint(0, len(possible_questions) - 1)]
    # get three random answers and the right answer and shuffle them
    possible_answers = _get_three_random_answers(question, all_qustions)
    possible_answers.append(question.answer)
    shuffle(possible_answers)
    # create question dict and add the possible answers, then return the dict
    question_dict = question.to_dictionary()
    question_dict['answer'] = possible_answers
    user.open_question = question
    user.questions.append(question)
    user.open_question_answer = _get_letter_of_answer(question.answer, possible_answers) 
    session.commit()
    session.close()
    return question_dict


def _get_ingredient_list(meals):
    """
    :type meals: list of meal objects
    """
    amount_ingredient_list = []
    for meal in meals:
        amount_ingredient_list.extend(meal.food.split(","))

    return amount_ingredient_list


def _get_letter_of_answer(answer, answers_list):
    index = answers_list.index(answer)
    if index == 0:
        return "!A"
    elif index == 1:
        return "!B"
    elif index == 2:
        return "!C"
    else:
        return "!D"


def _get_three_random_answers(ori_question, all_qustions):
    random_answers_answer = [question.answer for question in all_qustions if question != ori_question]
    return [random_answers_answer[randint(0, len(random_answers_answer) - 1)] for x in range(0, 3)]


def evaluate(answer, user_id):
    session = SESSION()
    user = session.query(User).filter_by(id=user_id).one()
    success = user.open_question_answer == answer
    points = user.open_question.value
    right_answer = user.open_question.answer
    if success:
        user.score.latest_points = points
        user.score.points += points
    total_points = user.score.points
    session.commit()
    session.close()

    return {
        "success": success,
        "right_answer": right_answer,
        "achieved_points": points,
        "total_points": total_points
    }


# Return the dict of the open question the user has or none if he does not have any (only used for testing)
def user_get_open_question(user_id):
    session = SESSION()
    user = session.query(User).filter_by(id=user_id).one()
    session.close()
    if user.open_question is None:
        return None
    else:
        return user.open_question.to_dictionary


# food_String: a string with ingrediants. e.g. "wasser,zwiblen,salz"
def add_meal(user_id, food_string, calories):
    session = SESSION()
    meal = Meal(timestamp=datetime.datetime.now(), calories=calories,
                food=food_string)
    session.add(meal)
    user = session.query(User).filter_by(id=user_id).one()
    user.meals.append(meal)
    session.commit()
    session.close()


def get_score(user_id):
    session = SESSION()
    user = session.query(User).filter_by(id=user_id).one()
    score = user.score
    answer_dict = { 
            "latest_points": score.latest_points,
            "total_points": score.points
            }
    session.close()
    return answer_dict


