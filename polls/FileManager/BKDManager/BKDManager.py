from django.shortcuts import render
from django.http import JsonResponse
from polls.models import BKD, Question
from polls.serializers import BKDSerializer, BKDIDSerializer

class bkdManager():
    def requestBKD(request, title):
        bkd = BKD.objects.filter(title = title)
        if(bkd):
            #bkd 존재
            bkd = BKD.objects.get(title = title)
            print(bkd.title)
            print(bkd.body)
        else:
            #bkd 미존재
            print("BKD IS NOT EXIST.")

        bkd = BKD.objects.filter(title = title)
        serializer = BKDSerializer(bkd, many=True)

        return JsonResponse(serializer.data[0], safe=False)

    def createBKD(request):
        bkd = BKD.objects.create(title = '', body = '')
        #빈 BKD 생성
        bkd_id = bkd.id
        bkd = BKD.objects.filter(id = bkd_id)
        serializer = BKDIDSerializer(bkd, many=True)
        #해당 ID Client로 보냄
        
        return JsonResponse(serializer.data[0], safe=True)

    def editBKD(request, bkd_id, title, body):
        print(body)
        bkd = BKD.objects.get(id = bkd_id)
        bkd.title = title
        bkd.body = body
        bkd.save()

        print(bkd.body)

        latest_question_list = Question.objects.order_by('-pub_date')[:5]
        context = {'latest_question_list':latest_question_list}
        return render(request, 'polls/index.html',context)


    def deleteBKD(request, title):
        bkd = BKD.objects.filter(title = title)
        if(bkd):
            #BKD 존재 및 삭제
            bkd.delete()
            print("BKD IS DELETED")
        else:
            #BKD 미존재
            print("BKD IS NOT EXIST")

        latest_question_list = Question.objects.order_by('-pub_date')[:5]
        context = {'latest_question_list':latest_question_list}
        return render(request, 'polls/index.html',context)

