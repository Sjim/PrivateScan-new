class SuspectedSentenceNode:
    def __init__(self, file_path, line_no, private_word_list, purpose, func_name, private_info=None, script=None,
                 confidence=1,
                 methods_called=[]):
        self.file_path = file_path
        self.line_no = line_no
        self.script = script
        self.private_word_list = private_word_list
        self.purpose = purpose
        self.func_name = func_name
        self.private_info = private_info
        self.confidence = confidence
        self.init_private_info()
        self.methods_called = methods_called

    def init_private_info(self):
        if self.private_info is None:
            self.private_info = [(word[0], purpose) for word in self.private_word_list for purpose in self.purpose]
        self.private_info = list(set(self.private_info))

    def __str__(self):
        res = self.file_path + ' ' + str(self.line_no) + '|'
        for pair in self.private_info:
            res += pair[0] + " " + pair[1] + ","
        return res[:-1]

    def __eq__(self, other):
        return self.file_path == other.file_path and self.line_no == other.line_no
