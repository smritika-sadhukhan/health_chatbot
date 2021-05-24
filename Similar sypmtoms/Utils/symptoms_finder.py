import pickle
import re


class Symptoms:
    def check_pattern(self, dis_list, inp):
        '''
        [SUMMARY]: Checking the closest symptoms given by user with the existing list

        Arguement:
        dis_list - list of symptoms
        inp - symptom to check  with


        Return:
        pred_list - closest symptom after comparing

        '''

        pred_list = []
        ptr = 0
        patt = "^" + inp + "$"
        regexp = re.compile(inp)
        for item in dis_list:

            # print(f"comparing {inp} to {item}")
            if regexp.search(item):
                pred_list.append(item)
                # return 1,item
        if len(pred_list) > 0:
            return 1, pred_list
        else:
            return ptr, item

    def similar_symptoms(self, list_sym):

        '''
        [SUMMARY]: Using list of symptoms given and according finding out relevent symptoms and possible disease

        Arguement:
        list_sym - All the symptoms given by user
        
        Return:
        list_final - relevent symptoms based on existing disease
        dis_final - disease based on existing symptoms

        '''

        with open("Files/filename.pickle", "rb") as handle:
            data = pickle.load(handle)

        data["Common_cold"] = data["Common"] + ["cold"] + ["common"] + ["Common_cold"]
        
        del data["Common"]
        with open("Files/symptoms.pkl", "rb") as f:
            mynewlist = pickle.load(f)

        chk_dis = ",".join(mynewlist).split(",")

        list_pattern = []
        for i in list_sym:
            if i!='fever':
                conf, cnf_dis = self.check_pattern(chk_dis, i)
                list_pattern.append(cnf_dis[0])

        list_sym = list_pattern
        list1 = []
        dict1 = data
        list_dis = []
        cc=0
        for i in dict1:
            c = 0
            for j in list_sym:
                if j in dict1[i]:
                    c = c + 1
                
                if c == len(list_sym):
                    list_dis.append(i)
                    list1.extend(dict1[i])
                    cc=cc+1
        if cc==0:
            list_dis.append(i)
            list1.extend(dict1[i])
        set_list1 = set(list1)
        if len(list_dis) != 1:
            dict2 = {}
            for i in set_list1:
                dict2[i] = list1.count(i)

            list5 = sorted(dict2.items(), key=lambda kv: (kv[1], kv[0]))
            list6 = []
            for i in list5[:10]:
                list6.append(i[0])
            final = list6 + ["None"]
        else:
            final = ["fever", "None"]
          
        list_final = []
        for i in final:
            i = i.split("_")
            i = " ".join(i)
            list_final.append(i)
        dis_final = []
        for i in list_dis:
            i = i.split("_")
            i = " ".join(i)
            dis_final.append(i)
        return (list_final, dis_final)
