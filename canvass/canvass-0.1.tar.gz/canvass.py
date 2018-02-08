import sys
import re
import uuid

import inquirer


class Canvass(object):
    _current_canvass = None

    def __init__(self, with_traversal=False):
        self.questions = dict()
        self.start = None
        self.with_traversal = with_traversal

    def set_as_current_canvass(self):
        Canvass._current_canvass = self

    def ask(self):
        if self.start is None:
            raise ValueError('Start question is not defined')

        traversal_count = 0
        answers = dict()
        ask_question = self.start
        while True:
            # If this is a Thread, point to first question
            if isinstance(ask_question, Thread):
                ask_question = ask_question[0]

            # If this is a repeat question, then this is a cycle
            if ask_question.question.name in answers:
                _loop_name = ask_question.question.name + '__cycle__'
                if _loop_name not in answers:
                    answers[_loop_name] = list()
                answers[_loop_name].append(answers.pop(ask_question.question.name))

            # Prompt user based on configured question
            try:
                answers = inquirer.prompt([ask_question.question],
                                          answers=answers,
                                          raise_keyboard_interrupt=True)
            except KeyboardInterrupt:
                print('Aborted by user')
                sys.exit()

            # If this is a Checkbox question, convert to tuple
            if isinstance(ask_question.question, inquirer.Checkbox):
                answers[ask_question.question.name] = tuple(answers[ask_question.question.name])

            # If there isn't anywhere to go next, terminate
            if not ask_question.next:
                break

            # Get the name of the next question, possibly based on previous answer
            if isinstance(ask_question, Splitter):
                try:
                    if callable(ask_question.next):
                        q_next_name = ask_question.next(answers[ask_question.name])
                    else:
                        q_next_name = ask_question.next[answers[ask_question.name]]
                except (KeyError, TypeError):
                    raise KeyError('{} is not a valid branch'.format(answers[ask_question.name]))
            elif isinstance(ask_question, Q):
                q_next_name = ask_question.next
            else:
                raise TypeError('Questions must be a Q, Splitter, or Thread object')

            # Add traversal, if needed
            if self.with_traversal:
                answers[ask_question.question.name] = (traversal_count, answers[ask_question.question.name])
                traversal_count += 1

            # If next question is immediate termination, terminate
            if q_next_name == Q.TERMINATE:
                break

            # Check for string based get-item-by-index
            thread_getitem = re.match(r'(.*)\[(\d+)\]$', q_next_name.strip())
            if thread_getitem:
                q_next_name = self.questions[thread_getitem.group(1)][int(thread_getitem.group(2))].name

            # Try to retrieve next question
            try:
                ask_question = self.questions[q_next_name]
            except KeyError:
                raise KeyError('Question {} does not exist'.format(q_next_name))

        # Normalize any cycles that may have happened
        for loop_key in [k for k in answers if '__cycle__' in k]:
            single_key = loop_key.replace('__cycle__', '')
            answers[loop_key].append(answers.pop(single_key))
            answers[single_key] = answers.pop(loop_key)

        return answers

    def __enter__(self):
        Canvass._current_canvass = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class QBase(object):
    def __init__(self, question, next=None, name=None, start=False):
        self.question = question
        self.name = name or question.name
        self.next = next.name if isinstance(next, Q) else next

        Canvass._current_canvass.questions[self.name] = self
        if start:
            Canvass._current_canvass.start = self


class Q(QBase):
    TERMINATE = '__terminate'

    def __init__(self, question, next=None, name=None, start=False):
        super(Q, self).__init__(question, next, name, start)
        if isinstance(self.next, dict):
            raise TypeError('Q cannot have dictionary as next')


class Splitter(QBase):
    def __init__(self, question, next=None, name=None, start=False):
        super(Splitter, self).__init__(question, next, name, start)
        if not (isinstance(self.next, dict) or callable(self.next)):
            raise TypeError('Splitter must have dictionary or callable as next')


class Thread(object):
    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name', str(uuid.uuid4())[:8])
        self.question_sequence = args

        for i, question in enumerate(self.question_sequence[:-1]):
            question.next = self.question_sequence[i + 1].name

        Canvass._current_canvass.questions[self.name] = self
        if kwargs.get('start'):
            Canvass._current_canvass.start = self

    def __getitem__(self, item):
        return self.question_sequence[item]


class YesNoQuestion(inquirer.List):
    def __init__(self, name, message='', ignore=False, validate=True, carousel=False):
        super(YesNoQuestion, self).__init__(
            name, message, choices=('yes', 'no'),
            default=None, ignore=ignore, validate=validate,
            carousel=carousel
        )
