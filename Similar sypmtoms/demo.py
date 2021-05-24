# Importing Libraries
from flask import request, make_response, jsonify, Flask
import logging
import urllib
import json
import os
import pickle

# Importing Modules
from Utils.symptoms_finder import Symptoms
from Utils.description import Description
from Utils.get_severity import GetSeverityDict
from Utils.precaution import GetPrecautionDict

app = Flask(__name__)

# Creating objects
symptoms_obj = Symptoms()
description_obj = Description()
get_severity_dict_obj = GetSeverityDict()
get_precaution_dict_obj = GetPrecautionDict()

# Creating a list where symptoms will be stored for future references
list_symp = []


@app.route("/get_symptoms", methods=["POST"])
def webhook():

    if request.method == "POST":
        req = request.get_json(silent=True, force=True)
        res = processRequest(req)

        res = json.dumps(res, indent=4)
        r = make_response(res)
        r.headers["Content-Type"] = "application/json"
        return r


def processRequest(req):

    # Get all the Query Parameter
    query_response = req["queryResult"]
    text = query_response.get("queryText", None)
    parameters = query_response.get("parameters", None)

    print(parameters)

    # User may choose none when there is no relevent symptom and analysis disease
    if text == "None":
        similar_symptopms, possible_disease = symptoms_obj.similar_symptoms(
            set(list_symp)
        )
        consult_result = get_severity_dict_obj.calc_condition(list_symp)
        print("possible_disease", possible_disease, list_symp)
        # Descriptions are not shown  when we have more than 1 disease found
        if len(possible_disease) > 1:
            query_response = {
                "fulfillmentMessages": [
                    {
                        "platform": "ACTIONS_ON_GOOGLE",
                        "simpleResponses": {
                            "simpleResponses": [
                                {
                                    "textToSpeech": "After analysis, on the basis  of the symptoms like "
                                    + ", ".join(list(set(list_symp[:-1])))
                                    + " and "
                                    + list_symp[-1]
                                    + " matches with the "
                                    + ", ".join(possible_disease[:-1])
                                    + " and "
                                    + possible_disease[-1]
                                }
                            ]
                        },
                    },
                    {
                        "platform": "ACTIONS_ON_GOOGLE",
                        "simpleResponses": {
                            "simpleResponses": [
                                {
                                    "textToSpeech": 'Based on your symptoms we suggest that " '
                                    + consult_result
                                    + ' "Since your symptoms match more than one disease it is better to consult a docter to know more about a specific disease.'
                                }
                            ]
                        },
                    },
                    {
                        "platform": "ACTIONS_ON_GOOGLE",
                        "simpleResponses": {
                            "simpleResponses": [
                                {
                                    "textToSpeech": "So do you want to consult with the docter."
                                }
                            ]
                        },
                    },
                    {
                        "platform": "ACTIONS_ON_GOOGLE",
                        "suggestions": {
                            "suggestions": [
                                {"title": "'Yes I want doctor consultation"},
                                {"title": "No I dont want doctor consultation"},
                            ]
                        },
                    },
                ]
            }
        else:
            # Descriptions are shown only when we are suggesting 1 disease
            description = description_obj.getDescription(possible_disease[0].lower())
            query_response = {
                "fulfillmentMessages": [
                    {
                        "platform": "ACTIONS_ON_GOOGLE",
                        "simpleResponses": {
                            "simpleResponses": [
                                {
                                    "textToSpeech": "After analysis, on the basis  of the symptoms like "
                                    + ", ".join(list(set(list_symp[:-1])))
                                    + " and "
                                    + list_symp[-1]
                                    + " matches with the "
                                    + possible_disease[-1]
                                    + '  '
                                    + description.split(".")[:1][0]
                                    + '  Based on your symptoms we suggest that " '
                                    + consult_result
                                    + " So do you want to consult with the docter. "
                                }
                            ]
                        },
                    },
                    # {
                    #     "platform": "ACTIONS_ON_GOOGLE",
                    #     "simpleResponses": {
                    #         "simpleResponses": [{"textToSpeech": description.split('.')[:1][0]+ 'Based on your symptoms we suggest that " '
                    #                 + consult_result+'So do you want to consult with the docter.'}]
                    #     },
                    # },
                    # {
                    #     "platform": "ACTIONS_ON_GOOGLE",
                    #     "simpleResponses": {
                    #         "simpleResponses": [
                    #             {
                    #                 "textToSpeech":
                    #             }
                    #         ]
                    #     },
                    # },
                    # {
                    #     "platform": "ACTIONS_ON_GOOGLE",
                    #     "simpleResponses": {
                    #         "simpleResponses": [
                    #             {
                    #                 "textToSpeech": "So do you want to consult with the docter."
                    #             }
                    #         ]
                    #     },
                    # },
                    {
                        "platform": "ACTIONS_ON_GOOGLE",
                        "suggestions": {
                            "suggestions": [
                                {"title": "Yes I want doctor consultation"},
                                {"title": "No I dont want doctor consultation"},
                            ]
                        },
                    },
                ]
            }

        return {"fulfillmentMessages": query_response["fulfillmentMessages"]}

    elif (
        text == "No I dont want doctor consultation"
        or text == "Yes Confirm"
        or text == "Don't Confirm"
    ):
        print(text)
        #  Ending the conversation by giving some precautionary tips who either does not want
        #  consultation or have successfully booked the appointment.

        c = 0

        try:
            # Checking wheather we have any symptoms list_symp
            similar_symptopms, possible_disease = symptoms_obj.similar_symptoms(
                set(list_symp)
            )

        except:
            # Incrementing c for future reference when no symptom found
            c = c + 1

        if c == 1:
            # To return when no symptoms are found
            query_response = {
                "fulfillmentMessages": [
                    {
                        "platform": "ACTIONS_ON_GOOGLE",
                        "simpleResponses": {
                            "simpleResponses": [
                                {
                                    "textToSpeech": "Please provide your symptoms so that we can evaluate the disease and give precautionary tips."
                                }
                            ]
                        },
                    }
                ]
            }
            return {"fulfillmentMessages": query_response["fulfillmentMessages"]}
        else:
            # We have symptoms to get the precautionary tips
            prec = []
            for i in possible_disease:
                try:

                    list_precaution = get_precaution_dict_obj.getprecautionDict(
                        i.lower()
                    )
                    prec.extend(list_precaution)

                except:
                    print("Cannot find precaution for the disease", i)
                    pass
                # If more than 1 precaution is found from the database
                if len(prec) > 0:
                    query_response = {
                        "fulfillmentMessages": [
                            {
                                "platform": "ACTIONS_ON_GOOGLE",
                                "simpleResponses": {
                                    "simpleResponses": [
                                        {
                                            "textToSpeech": "We have few precautionary tips for you based on your symptoms and possible disease."
                                            + ", ".join(list(set(prec))[:-1])
                                            + " and "
                                            + list(set(prec))[-1]
                                        }
                                    ]
                                },
                            },
                            # {
                            #     "platform": "ACTIONS_ON_GOOGLE",
                            #     "simpleResponses": {
                            #         "simpleResponses": [
                            #             {
                            #                 "textToSpeech": ",".join(list(set(prec))[:-1])
                            #                 + " and "
                            #                 + list(set(prec))[-1]
                            #             }
                            #         ]
                            #     },
                            # },
                            {
                                "platform": "ACTIONS_ON_GOOGLE",
                                "simpleResponses": {
                                    "simpleResponses": [
                                        {
                                            "textToSpeech": "Please take care. It was nice talking to you"
                                        }
                                    ]
                                },
                            },
                        ]
                    }

                    return {
                        "fulfillmentMessages": query_response["fulfillmentMessages"]
                    }
                else:
                    
                    # If no precaution is found from the database
                    query_response = {
                        "fulfillmentMessages": [
                            {
                                "platform": "ACTIONS_ON_GOOGLE",
                                "simpleResponses": {
                                    "simpleResponses": [
                                        {
                                            "textToSpeech": "Please take care. It was nice talking to you"
                                        }
                                    ]
                                },
                            },
                        ]
                    }

                    return {
                        "fulfillmentMessages": query_response["fulfillmentMessages"]
                    }

    elif "zip-code" in list(parameters.keys()):
        # Presenting list of docters available
        query_response = {
            "fulfillmentMessages": [
                {
                    "platform": "ACTIONS_ON_GOOGLE",
                    "simpleResponses": {
                        "simpleResponses": [
                            {
                                "textToSpeech": "Which docter would like to have appointment for consultation."
                            }
                        ]
                    },
                },
                {
                    "platform": "ACTIONS_ON_GOOGLE",
                    "suggestions": {
                        "suggestions": [
                            {"title": "Dr Avik Roy"},
                            {"title": "Mr Rahul Agarwal"},
                        ]
                    },
                },
            ]
        }
        return {"fulfillmentMessages": query_response["fulfillmentMessages"]}
    elif "symptoms_list" in parameters:
        # Considering some symptoms are passed
        for symp in parameters["symptoms_list"]:
            list_symp.append(symp)
        list_sym = [parameters["symptoms_list"]]
        similar_symptopms, possible_disease = symptoms_obj.similar_symptoms(
            set(parameters["symptoms_list"])
        )
        similar_symptopms = set(similar_symptopms)
        list1 = []
        for i in query_response["fulfillmentMessages"]:
            try:

                for m in similar_symptopms:
                    list1.append({"title": m})
                    i["suggestions"]["suggestions"] = list1[2:]

                i["suggestions"]["suggestions"].append({"title": "fever"})

            except:
                pass

        return {
            "fulfillmentText": "Please select a relevant symptom from the below list",
            "fulfillmentMessages": query_response["fulfillmentMessages"],
        }


















if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print("Starting app on port %d" % (port))
    app.run(debug=True, port=port, host="0.0.0.0")
