import csv


class Description:
    def getDescription(self, disease: str) -> str:
        
        '''
        [SUMMARY]: 
        Extracting descriptions of disease 

        Arguement:
        disease - str
       
        Return:
        description_list[disease] - description of a list

        ''' 
        description_list = dict()
        with open("Files/symptom_Description.csv") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            line_count = 0
            for row in csv_reader:
                _description = {row[0].lower(): row[1]}
                description_list.update(_description)
            print(type(description_list))
            return description_list[disease]
