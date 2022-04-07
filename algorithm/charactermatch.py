import copy
import difflib
# import Levenshtein


# duplicated
def character_match_abbr(word_std, abbr, word):
    if word.find(word_std) != -1:
        return True
    while word.find(abbr[0]) != -1 and word.find(abbr[0]) + 3 <= len(word):
        word = word[word.find(abbr[0]):]
        copy_abbr = copy.deepcopy(abbr)
        flag = True
        for i in range(3):
            index = copy_abbr.find(word[0])
            if index == -1:
                flag = False
                break
            else:
                copy_abbr = copy_abbr[index:]
                word = word[1:]
        if flag:
            return True
        else:
            continue
    return False


def character_match(word_std, word):
    """
    模糊匹配
    Args:
        word_std:
        word:

    Returns:
    script_path
    """
    word, word_std = word.lower().replace("_", ""), word_std.lower()
    if word.find(word_std) != -1 or difflib.SequenceMatcher((lambda x: x in ["_", "/"]), word, word_std).ratio() > 0.9:
        return True
    else:
        return False


def word_match(word_std_list, word):
    """

    Args:
        word_std_list: 可能的缩写类型
        word: 查询的单词

    Returns:
        True/False

    """
    if "ip" in word_std_list:
        word_std_list.remove("ip")
        if word == "ip" or word == 'IP' or word == 'Ip':
            return True
    for word_std in word_std_list:
        if character_match(word_std, word):
            return True
        else:
            continue
    return False


def test_match(a, b):
    print(b.find(a) != -1)
    print(difflib.SequenceMatcher((lambda x: x in ["_", "/"]), a, b).ratio())

    print()


if __name__ == '__main__':
    # print(word_match(["password", "pwd", "psw", "pswd"], "psd"))
    # print(word_match(["password", "pwd", "psw", "pswd"], "userpwd"))
    # print(word_match(["password", "pwd", "psw", "pswd"], "user_psw_1"))
    # print(word_match(["password", "pwd", "psw", "pswd"], "pwa"))
    # print(word_match(["password", "pwd", "psw", "pswd"], "passw"))
    # print(word_match(["password", "pwd", "psw", "pswd"], "passpsw"))
    # print(word_match(["password", "pwd", "psw", "pswd"], "user_password_a"))
    # print(word_match(["password", "pwd", "psw", "pswd"], "psw_a"))
    word_match(["pswd", "psw", "pwd", "password", "pass_word", "gitpass"], "gen_password")
    word_match(["key"], "gitkey")
    print(word_match(["Pseudonym", "alias"], "pseudonyms"))
    # word_match(["ipaddr", "IPAddress", "ip"], "output_dir")
    # word_match(["ipaddr", "IPAddress", "ip"], "os.path.pardir")

# 包含+长度限制
