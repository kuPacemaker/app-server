from django.http import JsonResponse
from polls.models import *
from polls.serializers import *
from rest_framework.authtoken.models import Token
from collections import OrderedDict
from rest_framework.decorators import api_view
import json, uuid

class considerQuestion():
    @api_view(['POST'])
    def verifyQuestion(request):
        token = request.data['token']
        unit_id = request.data['unit_id']
        pair_ids = request.data['pair_ids']
        pair_id_length = len(pair_ids)
        pair_id_list = [0 for i in range(pair_id_length)]
        for i in range(pair_id_length):
            pair_id_list += uuid.UUID(uuid.UUID(pair_ids[i]['pair_id']).hex)
        print(pair_id_list)
        data = OrderedDict()

        user_token = Token.objects.filter(key = token)
        unit = Unit.objects.filter(url_id = unit_id)
        if not (user_token.exists()):
            data["message"] = 'Token is not exist'
        elif not (unit.exists()):
            data["message"] = 'Unit is not exist'
        elif not (UnitQA.objects.filter(unit = unit[0]).exists()):
            data["message"] = 'QASet is not exist'
        else:
            host = Host.objects.get(channel = unit[0].channel)
            user = User.objects.get(id = user_token[0].user_id)
            if not (user == host.user):
                data["message"] = 'User is not host of Channel'

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
        data["isStart"] = False
        data["isEnd"] = False
        i = 0
        qapairs = QAPair.objects.filter(qaset = qaset)
        for i in range(qapairs.count()):
            data["questions"][i] = OrderedDict()
            serializer = QAPairSerializer(qapair[i], many=True)
            data["questions"][i]["id"] = serializer.data[0]['url_id']
            data["questions"][i]["quiz"] = serializer.data[0]['question']
            data["questions"][i]["answer"] = serializer.data[0]['answer']
            data["questions"][i]["user_answer"] = ''
            data["questions"][i]["answer_set"] = serializer.data[0]['answer_set']
            data["questions"][i]["verified"] = True

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)

    @api_view(['POST'])
    def makeReservation(request):
        token = request.data['token']
        unit_id = request.data['unit_id']
        que_number = request.data['que_number']
        release_time = request.data['release_time']
        end_time = request.data['end_time']
        data = OrderedDict()

        user_token = Token.objects.filter(key = token)
        unit = Unit.objects.filter(url_id = unit_id)
        if not (user_token.exists()):
            data["message"] = 'Token is not exist'
        elif not (unit.exists()):
            data["message"] = 'Unit is not exist'
        elif not (UnitQA.objects.filter(unit = unit[0]).exists()):
            data["message"] = 'QASet is not exist'
        else:
            host = Host.objects.get(channel = unit[0].channel)
            user = User.objects.get(id = user_token[0].user_id)
            if not (user == host.user):
                data["message"] = 'User it no host of Channel'

        if bool(data):
            json.dumps(data, ensure_ascii=False, indent="\t")
            return JsonResponse(data, safe=False)

        unit = Unit.objects.get(url_id = unit_id)
        qaset = UnitQA.objects.get(unit = unit).qaset
        new_testplan = TestPlan.objects.create(qaset = qaset)
        new_testplan.que_number = que_number
        new_testplan.release_time = release_time
        new_testplan.end_time = end_time
        new_testplan.save()

        UnitTest.objects.create(unit = unit, test = new_testplan)

        channel = unit.channel
        guests = Guest.objects.filter(channel = channel)
        for guest in guests:
            TestSet.objects.create(user = guest, test = new_testplan)

        data["message"] = 'Reservation saved'

        json.dumps(data, ensure_ascii=False, indent="\t")

        return JsonResponse(data, safe=False)
