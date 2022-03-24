class SuspectedSentenceNode:
    def __init__(self, file_path, line_no, private_word_list, purpose, private_info=None, script=None, confidence=1):
        self.file_path = file_path
        self.line_no = line_no
        self.script = script
        self.private_word_list = private_word_list
        self.purpose = purpose
        self.private_info = private_info
        self.confidence = confidence
        self.init_private_info()

    def init_private_info(self):
        if self.private_info is None:
            self.private_info = [(word[0], purpose) for word in self.private_word_list for purpose in self.purpose]
            self.private_info = list(set(self.private_info))

    def __str__(self):
        if self.private_info is None:
            return self.file_path + ' ' + str(self.line_no) + '\n' + str(self.private_word_list) + ' ' + self.purpose
        else:
            return self.file_path + ' ' + str(self.line_no) + '\n' + str(self.private_info)

    def __eq__(self, other):
        return self.file_path == other.file_path and self.line_no == other.line_no
