from django.core.mail import EmailMessage
import string, random

class emailSender():
    def sendEmail(uid):
        title = 'Reset for PACEMAKER\'s password.' #메일 제목
        content = 'Hello! We are PACEMAKER11\nThis mail is to reset your password!!\n\n\n\nYour new password : '#메일 기본 내용
        length = 10 #길이 10 임의지정
        string_pool = string.ascii_letters + '0123456789' #영어 대소문자 + 숫자
        result = ''
        for i in range(length):
            #랜덤 비밀번호 생성
            result += random.choice(string_pool)
        
        content += result
        send_email = EmailMessage(title, content, to = [uid]) #메일 전송 내용
        send_email.send() 
        
        return result #저장할 비밀번호 반환 - DB에 저장할 목적
