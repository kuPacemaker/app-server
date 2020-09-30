import string, random


def channelJoinCodeGeneration():
    length = 10
    string_pool = string.ascii_letters + '0123456789'
    result = ''
    for i in range(length):
        result += random.choice(string_pool)

    return result
