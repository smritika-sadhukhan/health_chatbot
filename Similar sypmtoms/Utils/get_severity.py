import csv


class GetSeverityDict:
    def getSeverityDict(self) -> dict:
        
        '''
        [SUMMARY]: Extract the score wrt symptomsfrom the file 

        Arguement:
      

        Return:
        severityDictionary : dictionary with keys as symptoms and values as scores

        ''' 

        severityDictionary = dict()
        with open("Files/Symptom_severity.csv") as csv_file:

            csv_reader = csv.reader(csv_file, delimiter=",")
            line_count = 0
            try:
                for row in csv_reader:
                    _diction = {row[0]: int(row[1])}
                    severityDictionary.update(_diction)

            except:
                pass
            return severityDictionary

    def calc_condition(self, exp :list, days=5) -> str:
        '''
        [SUMMARY]: Extract the score wrt symptomsfrom the file 

        Arguement:
        exp - list of symptoms

        Return:
        str as suggestions

        ''' 
        severityDictionary = self.getSeverityDict()
        sum = 0
        for item in exp:
            try:
                sum = sum + severityDictionary[item]

            except:
                return "It is recommended to consult with the doctor"
        if (sum * days) / (len(exp) + 1) > 13:
            return "You should take the consultation from doctor. "
        else:
            return "It might not be that bad but you should take precautions."
