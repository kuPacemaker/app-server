from django.shortcuts import render
from polls.models import BKD, Question

class bkdManager():
    def inquireIntoBKD(request, title):
        bkd = BKD.objects.filter(title = title)
        if(bkd):
            #bkd 존재
            bkd = BKD.objects.get(title = title)
            print(bkd.title)
            print(bkd.body)
        else:
            #bkd 미존재
            print("BKD IS NOT EXIST.")

        latest_question_list = Question.objects.order_by('-pub_date')[:5]
        context = {'latest_question_list':latest_question_list}
        return render(request, 'polls/index.html',context)
            
    def makeBKD(request):
        bkd = BKD.objects.create(title = '', body = '')
        #빈 BKD 생성
        print(bkd.id)
        #해당 BKD의 id client로 보냄

        latest_question_list = Question.objects.order_by('-pub_date')[:5]
        context = {'latest_question_list':latest_question_list}
        return render(request, 'polls/index.html',context)

    def saveBKD(request, bkd_id, title, body):
        bkd = BKD.objects.get(id = bkd_id)
        bkd.title = title
        bkd.body = body
        bkd.save()

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

