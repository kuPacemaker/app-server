from django.shortcuts import render
from django.http import JsonResponse
from polls.models import *
from polls.serializers import *
from rest_framework.parsers import JSONParser
from .ChoiceProblemGenerator.ChoiceProblemGenerator import choiceProblemGenerator
from collections import OrderedDict
from rest_framework.decorators import api_view
from polls.AESCipher import AESCipher
import requests, json, uuid


class qgapi():
    def stringWithSlash(qa_pair_answer_set):
        count = 0
        index = 0
        flag = 0
        #flag가 0이면 result에 들어갈 단어를 찾아야하고 flag가 1이면 이미 찾은것이므로 다음단어를 찾아야 한다는 뜻
        result = ''
        length = len(qa_pair_answer_set)
        while(count != 4):
            flag = 0
            if(qa_pair_answer_set[index] == '\''):
                #따옴표가 있는 부분의 index를 찾으면
                for i in range(index+1,length):
                    #index 다음부분부터는 단어일테니까 찾는데
                    if(flag == 1):
                        #이미 단어를 찾은 상태라면 건너뛰고
                        continue
                    if(qa_pair_answer_set[i] == '\''):
                        #단어를 찾지 않은 상태이니까 다음 따옴표가 나올때까지 반복하면서 i값을 증가시키는데
                        flag = 1
                        #따옴표가 나온다면 단어를 찾은거니까 이떄 flag값을 바꿔주고
                        result += qa_pair_answer_set[index+1:i]
                        #찾은 단어를 result에 추가하고
                        count += 1
                        #찾은 단어의 갯수를 하나 증가시킨다
                        if(count != 4):
                            #다찾은게 아니라면 /로 연결해주고
                            result += '/'
                            #index의 값을 찾은 따옴표 다음의 위치로 바꿔준다
                            index = i+1
            index += 1
  
        return result

    @api_view(['POST'])
    def generateQuestion(request):
        cipher = AESCipher()
        token = request.data['token']
        unit_id = uuid.UUID(uuid.UUID(request.data['unit_id']).hex)
        user_token = Token.objects.filter(key = token)
        data = OrderedDict()
        if(user_token):
            #token 존재
            unit = Unit.objects.filter(url_id = unit_id)
            if(unit):
                #unit이 존재
                host = Host.objects.filter(channel = unit[0].channel)
                if(user_token[0].user_id == host[0].user.id):
                    #token에 해당하는 user가 unit이 존재하는 channel의 host이면
                    unitqa = UnitQA.objects.filter(unit = unit[0])
                    if(unitqa.exists()):
                        unitqa[0].qaset.delete()
                        News.objects.filter(unit = unit[0]).delete()

                    unit_bkd = UnitBKD.objects.get(unit = unit[0])
                    bkd = BKD.objects.get(id = unit_bkd.bkd.id)
        
                    URL = 'https://117.16.136.170/restful/qg/'
                    datas = {'bkd' : bkd.body}
                    res = requests.request('POST', URL, json=datas, verify=False)
                    content = res.text
                    nouns = []
                    aqset = []
                    question_data = json.loads(content)
                    length = len(question_data['passages'])
                    for i in range(length):
                        nouns += question_data['passages'][i]['nouns']
                        aqset += question_data['passages'][i]['aqset']
    
                    qa_set = choiceProblemGenerator.choiceProblemGenerator(nouns,aqset)
                    
                    unit_for_news = Unit.objects.get(url_id = unit_id)
                    channel_for_news = unit_for_news.channel
                    news_title = "NEW QUESTIONS WERE RECEIVED"
                    news_body = channel_for_news.name+"/"+unit_for_news.name+", "+cipher.decrypt(Host.objects.get(channel = channel_for_news).user.first_name)+", "+channel_for_news.description
                    exist_news = News.objects.filter(ntype = "QUESTION_GENERATION", unit = unit_for_news)
                    if(exist_news):
                        for i in range(exist_news.count()):
                            exist_news[i].delete()
                    
                    news = News.objects.create(ntype = "QUESTION_GENERATION", title = news_title, body = news_body, channel = channel_for_news, unit = unit_for_news)
                    hosts = Host.objects.filter(channel = channel_for_news)
                    for host in hosts:
                        UserNews.objects.create(news = news, user = host.user)

                    unit_qa = UnitQA.objects.create(qaset = qa_set, unit = unit[0])
                    #객관식 문제 생성이 끝난 qa_set에 대해서
                    qa_pair = QAPair.objects.filter(qaset = qa_set)
                    #각 qa_pair를 찾아서
                    length = qa_pair.count()
                    serializer = QAPairSerializer(qa_pair, many=True)

                    #여기서부터 json 형식의 파일을 만들기 위한 작업을 한다.
                    data["state"] = "success"
                    data["message"] = "Questions are generated"
                    data["isStart"] = False
                    data["isEnd"] = False
                    data["questions"] = [0 for i in range(length)]
            
                    for i in range(length):
                        data["questions"][i] = OrderedDict()
                        data["questions"][i]["id"] = serializer.data[i]['url_id']
                        data["questions"][i]["quiz"] = serializer.data[i]['question']
                        data["questions"][i]["answer"] = serializer.data[i]['answer']
                        data["questions"][i]["user_answer"] = ''
                        data["questions"][i]["answer_set"] = serializer.data[i]['answer_set']#qgapi.stringWithSlash(qa_pair[i].answer_set)
                        #이 부분은 str 형식으로 저장되어 있어서 단어를 따로 찾아서 /로 연결해주기 위한 함수를 호출한다
                        data["questions"][i]["verified"] = True
                else:
                    data["state"] = "fail"
                    data["message"] = "User is not this channel\'s host"
            else:
                data["state"] = "fail"
                data["message"] = "Unit is not exist"
        else:
            #token 미존재
            data["state"] = "fail"
            data["message"] = "Token is not exist"

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

