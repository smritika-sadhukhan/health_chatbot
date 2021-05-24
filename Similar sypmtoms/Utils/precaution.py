import csv


class GetPrecautionDict:
    def getprecautionDict(self, disease: str) -> list:
        
        '''
        [SUMMARY]: Extracting precaution from the csv file and return a list

        Arguement:
        disease

        Return:
        precautionDictionary[disease]

        ''' 
        precautionDictionary = dict()

        with open("Files/symptom_precaution.csv") as csv_file:

            csv_reader = csv.reader(csv_file, delimiter=",")
            line_count = 0
            for row in csv_reader:
                _prec = {row[0].lower(): [row[1], row[2], row[3], row[4]]}
                precautionDictionary.update(_prec)
            return precautionDictionary[disease]
