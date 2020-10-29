from polls.models import *
import random

class choiceProblemGenerator():
    def choiceProblemGenerator(nouns, aqset):
        count = len(nouns)
        length = len(aqset)
        print(length)
        count_for_arr = 0

        question = [0 for i in range(length)]
        answer = [0 for i in range(length)]
        answerset = ["" for i in range(length)]
        
        prev_rand_num = [-1 for i in range(3)]

        for i in range(length):
            prev_rand_num = [-1 for i in range(3)]
            count_for_arr = 0
            random_answer_position = random.randint(0,3)
            question[i] = aqset[i][1]
            answer[i] = aqset[i][0]
            for j in range(4):
                if(j != random_answer_position):
                    random_noun_choice = random.randint(0,count-1)
                    while(random_noun_choice == i or random_noun_choice == prev_rand_num[0] or random_noun_choice == prev_rand_num[1] or random_noun_choice == prev_rand_num[2]):
                        random_noun_choice = random.randint(0,count-1)
                    prev_rand_num[count_for_arr] = random_noun_choice
                    answerset[i] += nouns[random_noun_choice]
                    count_for_arr += 1
                else:
                    answerset[i] += answer[i]

                if(j != 3):
                    #각 quiz의 보기들을 |^|로 구별하여 하나의 문자열로 만들어준다.
                    answerset[i] += "|^|"
        
        qa_set = QASet.objects.create(valid = False)
        for i in range(length):
            QAPair.objects.create(qaset = qa_set, index = i+1, question = question[i], answer = answer[i], answer_set = answerset[i])

        return qa_set
