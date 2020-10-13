from polls.models import *
import string, random

class channelJoinCodeGenerator():
    def channelJoinCodeGenerate():
        length = 10 #길이 10 임의지정
        string_pool = string.ascii_letters + '0123456789' #영어 대소문자 + 숫자
        while(True):
            result = ''
            for i in range(length):
                #랜덤 비밀번호 생성
                result += random.choice(string_pool)
            accesspath = Channel.objects.filter(accesspath = result)
            if(accesspath):
                #해당 코드값에 일치하는 채널이 존재
                continue
            else:
                break

        return result # 저장할 채널 참여 코드 반환
