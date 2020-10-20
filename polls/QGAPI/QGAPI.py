from django.shortcuts import render
from django.http import JsonResponse
from polls.models import *
from polls.serializers import *
from rest_framework.parsers import JSONParser
from .ChoiceProblemGenerator.ChoiceProblemGenerator import choiceProblemGenerator
from collections import OrderedDict
import requests, json


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

    def generateQuestion(request,document):#, token, channel, unit, document):
        user_token = True #= Token.objecs.filter(token = token)
        if(user_token):
            #token 존재
            bkd = BKD.objects.get(id = document)
        
            URL = 'http://117.16.136.170/restful/qg'
            data = {'bkd' : bkd.body}
            res = requests.post(URL, data=data)
            content = res.text
            nouns = []
            aqset = []
            question_data = json.loads(content)
            length = len(question_data['passages'])
            for i in range(length):
                nouns += question_data['passages'][i]['nouns']
                aqset += question_data['passages'][i]['aqset']
    
            qa_set = choiceProblemGenerator.choiceProblemGenerator(nouns,aqset)
            #객관식 문제 생성이 끝난 qa_set에 대해서
            qa_pair = QAPair.objects.filter(qaset = qa_set)
            #각 qa_pair를 찾아서
            length = qa_pair.count()
            serializer = QAPairSerializer(qa_pair, many=True)

            #여기서부터 json 형식의 파일을 만들기 위한 작업을 한다.
            data = OrderedDict()
            data["isStart"] = None
            data["isEnd"] = None
            data["questions"] = [0 for i in range(length)]
            
            for i in range(length):
                data["questions"][i] = OrderedDict()
                data["questions"][i]["id"] = serializer.data[i]['url_id']
                data["questions"][i]["quiz"] = serializer.data[i]['question']
                data["questions"][i]["answer"] = serializer.data[i]['answer']
                data["questions"][i]["user_answer"] = ''
                data["questions"][i]["answer_set"] = qgapi.stringWithSlash(qa_pair[i].answer_set)
                #이 부분은 str 형식으로 저장되어 있어서 단어를 따로 찾아서 /로 연결해주기 위한 함수를 호출한다
                data["questions"][i]["verified"] = True

            json.dumps(data, ensure_ascii=False, indent="\t")

            return JsonResponse(data, safe=False)
        else:
            #token 미존재
            print("TOKEN IS NOT EXIST")

