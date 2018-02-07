"""Enfors Machine Learning Bot by Christer Enfors.
"""

from enforsml.text import nlp, utils


class ParseError(BaseException):

    def __init__(self, file_obj, msg):
        BaseException.__init__(self, "Error in file %s, line %d: %s" %
                               (file_obj.file_name, file_obj.line_num, msg))


class BotFile:
    """An EnforsML bot file.
    """

    def __init__(self):
        self.file_name = None
        self.line_num = 0
        self.intents = []

    def load(self, file_name):
        """Load a bot file from the file name file_name.
        """

        self.file_name = file_name
        self.line_num = 0
        intent = None
        mode = None

        with open(file_name, "r") as f:
            for line in f.readlines():

                self.line_num += 1

                line = self.clean_up_line(line)

                # Comments
                if line.startswith("#"):
                    continue

                # Empty lines
                elif len(line) == 0:
                    self.end_of_intent(intent)
                    intent = None

                elif line.startswith("Intent"):
                    intent = self.start_of_intent(line)

                elif line == "User:":
                    mode = "User"

                elif line == "Bot:":
                    mode = "Bot"

                elif line.startswith("- "):
                    self.text_line(line[2:], mode, intent)
                    
                else: 
                    # print(line)
                    pass

        if intent:
            self.end_of_intent(intent)

        return self.intents

    def clean_up_line(self, line):
        """Clean up lines read from a file.
        """
        
        line = line.replace("\r", "")
        return line.strip()

    def start_of_intent(self, line):
        """Called when we find the start of an Intent.
        """

        words = line.split(" ")
        
        try:
            intent_name = words[1]
        except IndexError:
            raise ParseError(self, "Intent needs a name")

        # I don't understand why, but train_sentences=[] MUST be
        # present in the following line.
        intent = nlp.Intent(intent_name, train_sentences=[])
        return intent
            
            
    def end_of_intent(self, intent):
        """Called when we are done loading an intent.
        """

        if intent:
            self.intents.append(intent)

#            print("Questions:")
#            print(intent.train_sentences)
#            print("Answer:")
#            print(intent.response_data)
#            print()
            

    def text_line(self, line, mode, intent):
        """Take care of a line beginning with "- ".
        """

        if not intent:
            raise ParseError(self, "This text line is not part of an Intent")

        if mode is None:
            raise ParseError(self, "I don't know if this is a User or Bot line")
        
        if mode == "User":
            intent.add_train_txt(line)

        elif mode == "Bot":
            intent.response_data = line
