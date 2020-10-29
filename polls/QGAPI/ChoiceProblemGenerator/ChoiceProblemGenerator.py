from polls.models import *
import random

class choiceProblemGenerator():
    def choiceProblemGenerator(nouns, aqset):
        count = len(nouns)
        length = len(aqset)

        question = [0 for i in range(length)]
        answer = [0 for i in range(length)]
        answerset = ["" for i in range(length)]

        for i in range(length):
            random_answer_position = random.randint(0,3)
            question[i] = aqset[i][1]
            answer[i] = aqset[i][0]
            for j in range(4):
                if(j != random_answer_position):
                    random_noun_choice = random.randint(0,count-1)
                    while(random_noun_choice == i):
                        random_noun_choice = random.randint(0,count-1)
                    answerset[i] += nouns[random_noun_choice] 
                else:
                    answerset[i] += answer[i]

                if(j == 3):
                    #각 quiz의 보기들을 /로 구별하여 하나의 문자열로 만들어준다.
                    answerset[i] += '/'
        
        qa_set = QASet.objects.create(valid = False)
        for i in range(length):
            QAPair.objects.create(qaset = qa_set, index = i+1, question = question[i], answer = answer[i], answer_set = answerset[i])

        return qa_set
