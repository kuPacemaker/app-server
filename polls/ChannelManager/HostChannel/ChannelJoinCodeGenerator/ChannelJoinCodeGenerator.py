import string, random

class channelJoinCodeGenerator():
    def channelJoinCodeGenerate():
        length = 10 #길이 10 임의지정
        string_poll = string.ascii_letters + '0123456789' #영어 대소문자 + 숫자
        result = ''
        for i in range(length):
            #랜덤 비밀번호 생성
            result += random.choice(string_pool)

        return result # 저장할 채널 참여 코드 반환
