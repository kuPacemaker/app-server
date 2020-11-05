from django.http import JsonResponse
from polls.models import *
from polls.serializers import *
from rest_framework.authtoken.models import Token
from collections import OrderedDict
from rest_framework.decorators import api_view
from polls.QGAPI.QGAPI import qgapi
from polls.AESCipher import AESCipher
import json, uuid

class considerQuestion():
    @api_view(['POST'])
    def verifyQuestion(request):
        token = request.data['token']
        unit_id = uuid.UUID(uuid.UUID(request.data['unit_id']).hex)
        pair_ids = request.data['pair_ids']
        pair_id_length = len(pair_ids)
        pair_id_list = [0 for i in range(pair_id_length)]
        for i in range(pair_id_length):
            pair_id_list[i] = uuid.UUID(uuid.UUID(pair_ids[i]['pair_id']).hex)
        data = OrderedDict()

        user_token = Token.objects.filter(key = token)
        unit = Unit.objects.filter(url_id = unit_id)
        if not (user_token.exists()):
            data["state"] = "fail"
            data["message"] = "Token is not exist"
        elif not (unit.exists()):
            data["state"] = "fail"
            data["message"] = "Unit is not exist"
        elif not (UnitQA.objects.filter(unit = unit[0]).exists()):
            data["state"] = "fail"
            data["message"] = "QASet is not exist"
        else:
            host = Host.objects.get(channel = unit[0].channel)
            user = User.objects.get(id = user_token[0].user_id)
            if not (user == host.user):
                data["state"] = "fail"
                data["message"] = "User is not this channel\'s host"

        if bool(data):
            json.dumps(data, ensure_ascii=False, indent="\t")
            return JsonResponse(data, safe=False)

        unit = Unit.objects.get(url_id = unit_id)
        qaset = UnitQA.objects.get(unit = unit).qaset
        for i in range(pair_id_length):
            qapair = QAPair.objects.get(url_id = pair_id_list[i])
            qapair.delete()

        i = 1
        qapairs = QAPair.objects.filter(qaset = qaset)
        for qapair in qapairs:
            qapair.index = i
            qapair.save()
            i = i+1

        #data
        data["state"] = "success"
        data["isStart"] = False
        data["isEnd"] = False
        i = 0
        qapairs = QAPair.objects.filter(qaset = qaset)
        serializer = QAPairSerializer(qapairs, many=True)
        data["questions"] = [0 for i in range(qapairs.count())]
        for i in range(qapairs.count()):
            data["questions"][i] = OrderedDict()
            data["questions"][i]["id"] = serializer.data[i]['url_id']
            data["questions"][i]["quiz"] = serializer.data[i]['question']
            data["questions"][i]["answer"] = serializer.data[i]['answer']
            data["questions"][i]["user_answer"] = ''
            data["questions"][i]["answer_set"] = qapairs[i].answer_set
            data["questions"][i]["verified"] = True

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

    @api_view(['POST'])
    def makeReservation(request):
        cipher = AESCipher()
        token = request.data['token']
        unit_id = uuid.UUID(uuid.UUID(request.data['unit_id']).hex)
#release_time = request.data['release_time']
#end_time = request.data['end_time']
        data = OrderedDict()

        user_token = Token.objects.filter(key = token)
        unit = Unit.objects.filter(url_id = unit_id)
        qaset = UnitQA.objects.get(unit = unit[0]).qaset
        if not (user_token.exists()):
            data["state"] = "fail"
            data["message"] = "Token is not exist"
        elif not (unit.exists()):
            data["state"] = "fail"
            data["message"] = "Unit is not exist"
        elif not (UnitQA.objects.filter(unit = unit[0]).exists()):
            data["state"] = "fail"
            data["message"] = "QASet is not exist"
        elif (TestPlan.objects.filter(qaset = qaset).exists()):
            data["state"] = "fail"
            data["message"] = "Reservation is already exist"
        else:
            host = Host.objects.get(channel = unit[0].channel)
            user = User.objects.get(id = user_token[0].user_id)
            if not (user == host.user):
                data["state"] = "fail"
                data["message"] = "User is not Channel\'s host"

        if bool(data):
            json.dumps(data, ensure_ascii=False, indent="\t")
            return JsonResponse(data, safe=False)

        qaset = UnitQA.objects.get(unit = unit[0]).qaset
        qapair = QAPair.objects.filter(qaset = qaset)
        new_testplan = TestPlan.objects.create(qaset = qaset)
        new_testplan.que_number = qapair.count()
        new_testplan.released = True
#배포시간과 마감시간 설정부분
#new_testplan.release_time = release_time
#new_testplan.end_time = end_time
        new_testplan.save()

        test = UnitTest.objects.create(unit = unit[0], test = new_testplan)

        channel = unit[0].channel
        guests = Guest.objects.filter(channel = channel)
        for guest in guests:
            testset = TestSet.objects.create(user = guest.user, test = new_testplan)
            testset.received = True
            if(Host.objects.filter(user = testset.user, channel = channel).exists()):
                testset.submitted = True
            testset.save()
            for i in range(qapair.count()):
                TestPair.objects.create(tset = testset, pair = qapair[i])


        unit_for_news = Unit.objects.get(url_id = unit_id)
        channel_for_news = unit_for_news.channel
        bkd_for_news = UnitBKD.objects.get(unit = unit_for_news).bkd
        news_title = "NEW QUIZ IS OPENED"
        news_body = channel_for_news.name+"/"+unit_for_news.name+", "+cipher.decrypt(Host.objects.get(channel = channel_for_news).user.first_name)+", "+channel_for_news.description
        news = News.objects.create(ntype = "PAPER_RECEIVE", title = news_title, body = news_body, channel = channel_for_news, unit = unit_for_news)
        guests = Guest.objects.filter(channel = channel_for_news)
        for guest in guests:
            UserNews.objects.create(news = news, user = guest.user)

        data["state"] = "success"
        data["message"] = "Reservation saved"
        
        user = User.objects.get(id = user_token[0].user_id)
        unit = Unit.objects.filter(url_id = unit_id)
        channel = Channel.objects.filter(id = unit[0].channel.id)

        serializer = ChannelInfoSerializer(channel, many=True)
        data["channel"] = OrderedDict()
        data["channel"]["id"] = serializer.data[0]['url_id']
        data["channel"]["title"] = serializer.data[0]['name']
        data["channel"]["detail"] = serializer.data[0]['description']
        data["channel"]["code"] = serializer.data[0]['accesspath']

        serializer = UnitSerializer(unit, many=True)
        data["unit"] = OrderedDict()
        data["unit"]["id"] = serializer.data[0]['url_id']
        data["unit"]["index"] = serializer.data[0]['index']
        data["unit"]["title"] = serializer.data[0]['name']
        data["unit"]["isOpened"] = True

        unit_bkd = UnitBKD.objects.filter(unit = unit[0])
        data["unit"]["document"] = OrderedDict()
        if (unit_bkd):
            bkd = BKD.objects.filter(id = unit_bkd[0].bkd.id)
            serializer = BKDSerializer(bkd, many=True)
            data["unit"]["document"]["id"] = serializer.data[0]['url_id']
            data["unit"]["document"]["visible"] = unit_bkd[0].opened
            data["unit"]["document"]["title"] = bkd[0].title
            data["unit"]["document"]["body"] = bkd[0].body
        else:
            data["unit"]["document"]["id"] = None
            data["unit"]["document"]["visible"] = False
            data["unit"]["document"]["title"] = ""
            data["unit"]["document"]["body"] = ""

        data["paper"] = OrderedDict()
        if (UnitQA.objects.filter(unit = unit[0]).exists()):
            qaset = UnitQA.objects.get(unit = unit[0]).qaset

            test = UnitTest.objects.filter(unit = unit[0])
            if (test.exists()):
                isStart = test[0].test.released
                testset = TestSet.objects.filter(user = user, test = test[0].test)
                if(testset.exists()):
                    isEnd = testset[0].submitted
                else:
                    isEnd = False
            else:
                isStart = False
                isEnd = False

            data["paper"]["isStart"] = isStart
            data["paper"]["isEnd"] = isEnd
            
            qapairs = QAPair.objects.filter(qaset = qaset)
            qapair_length = qapairs.count()
            serializer = QAPairSerializer(qapairs, many=True)
            if(qapair_length != 0):
                data["paper"]["questions"] = [0 for i in range(qapair_length)]
                for i in range(qapair_length):
                    data["paper"]["questions"][i] = OrderedDict()
                    data["paper"]["questions"][i]["id"] = serializer.data[i]['url_id']
                    data["paper"]["questions"][i]["quiz"] = qapairs[i].question
                    data["paper"]["questions"][i]["answer"] = qapairs[i].answer
                    if(test.exists()):
                        testplan = TestPlan.objects.get(qaset = qaset)
                        testset = TestSet.objects.get(user = user, test = testplan)
                        data["paper"]["questions"][i]["user_answer"] = TestPair.objects.get(tset = tes
                    else:
                        data["paper"]["questions"][i]["user_answer"] = ""
                    data["paper"]["questions"][i]["answer_set"] = qapairs[i].answer_set
                    data["paper"]["questions"][i]["verified"] = True
            else:
                 data["paper"]["questions"] = []

        else:
            data["paper"]["isStart"] = False
            data["paper"]["isEnd"] = False
            data["paper"]["questions"] = []

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)
