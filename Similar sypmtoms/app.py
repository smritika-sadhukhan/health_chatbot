# Importing Libraries
from flask import request, make_response, jsonify, Flask
from google.cloud import dialogflow
import logging
import urllib
import json
import os
import pickle
import collections

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

os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = "C:/Users/Lenovo/Downloads/healthcare-chatbot-ufqk-0142928d0852.json"


@app.route("/get_symptoms", methods=["POST"])
def webhook():

    if "text[]" not in request.form:
        resp = jsonify({"message": "No file part in the request"})
        resp.status_code = 400
        return resp

    text = request.form.get("text[]")

    errors = {}
    success = False

    if len(str(text)) != 0:
        success = True
    else:
        errors[text] = "Text is empty"

    if success:
        resp = jsonify({"message": "Text successfully uploaded.."})
        resp.status_code = 201
        project_id = "healthcare-chatbot-ufqk"
        session_id = "session_id"
        language_code = "en"
        result = get_response_suggestion(project_id, session_id, [text], language_code)
        print(result)
        return jsonify(
            {"Suggestion": result["Suggestion"], "Response": result["Response"]}
        )
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return resp


def get_response_suggestion(project_id, session_id, texts, language_code):

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=texts[0], language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )


    res = processRequest(response)
    return res



def processRequest(response):

    # Get all the Query Parameter
    query_response = response
    text = response.query_result.query_text
    parameters = a = dict(collections.OrderedDict(response.query_result.parameters))

    print(text, parameters)

    # User may choose none when there is no relevent symptom and analysis disease
    if text == "None":
        suggestion = []
        response_list = []
        similar_symptopms, possible_disease = symptoms_obj.similar_symptoms(
            set(list_symp)
        )
        consult_result = get_severity_dict_obj.calc_condition(list_symp)
        print("possible_disease", possible_disease, list_symp)
        # Descriptions are not shown  when we have more than 1 disease found
        if len(possible_disease) > 1:

            response_list.append(
                "After analysis, on the basis  of the symptoms like "
                + ", ".join(list(set(list_symp[:-1])))
                + " and "
                + list_symp[-1]
                + " matches with the "
                + ", ".join(possible_disease[:-1])
                + " and "
                + possible_disease[-1]
            )
            response_list.append(
                'Based on your symptoms we suggest that "'
                + consult_result
                + ' "Since your symptoms match more than one disease it is better to consult a docter to know more about a specific disease.'
            )

            response_list.append("So do you want to consult with the docter.")

            suggestion.append("Yes I want doctor consultation")
            suggestion.append("No I dont want doctor consultation")
            dict1 = {}
            dict1["Response"] = response_list
            dict1["Suggestion"] = suggestion
            return dict1

        else:
            # Descriptions are shown only when we are suggesting 1 disease
            description = description_obj.getDescription(possible_disease[0].lower())
            response_list.extend(
                [
                    [
                        "After analysis, on the basis  of the symptoms like "
                        + ", ".join(list(set(list_symp[:-1])))
                        + " and "
                        + list_symp[-1]
                        + " matches with the "
                        + possible_disease[-1]
                    ],
                    [
                        description.split(".")[:1][0]
                        + "Based on your symptoms we suggest that "
                        + consult_result
                    ],
                    ["So do you want to consult with the docter."],
                ]
            )
            suggestion.append("Yes I want doctor consultation")
            suggestion.append("No I dont want doctor consultation")
            dict1 = {}
            dict1["Response"] = response_list
            dict1["Suggestion"] = suggestion
            return dict1

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
            response_list = []
            response_list.append(
                "Please provide your symptoms so that we can evaluate the disease and give precautionary tips."
            )
            dict1 = {}
            dict1["Response"] = response_list
            dict1["Suggestion"] = []
            return dict1
        else:
            response_list = []
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
                    response_list = []
                    response_list.extend(
                        [
                            [
                                "We have few precautionary tips for you based on your symptoms and possible disease."
                            ],
                            [
                                ", ".join(list(set(prec))[:-1])
                                + " and "
                                + list(set(prec))[-1]
                            ],
                            ["Please take care. It was nice talking to you"],
                        ]
                    )

                    dict1 = {}
                    dict1["Response"] = response_list
                    dict1["Suggestion"] = []
                    return dict1
                else:
                    response_list = []
                    # If no precaution is found from the database
                    response_list.append("Please take care. It was nice talking to you")

                    dict1 = {}
                    dict1["Response"] = response_list
                    dict1["Suggestion"] = []
                    return dict1
    elif "zip-code" in list(parameters.keys()):
        response_list = [
            "Which docter would like to have appointment for consultation."
        ]
        suggestion = ["Dr Avik Roy", "Mr Rahul Agarwal"]
        dict1 = {}
        dict1["Response"] = response_list
        dict1["Suggestion"] = suggestion
        return dict1
    elif "symptoms_list" in parameters:
        # Considering some symptoms are passed
        for symp in parameters["symptoms_list"]:
            list_symp.append(symp)
        list_sym = [parameters["symptoms_list"]]
        similar_symptopms, possible_disease = symptoms_obj.similar_symptoms(
            set(parameters["symptoms_list"])
        )
        similar_symptopms = set(similar_symptopms)
        dict1 = {}
        dict1["Suggestion"] = list(similar_symptopms)
        dict1["Response"] = ["Do you have any more symptoms ?",'If yes please choose from the below list or else choose None']
        return dict1

    else:
        suggestion = []
        response_list = []
        if len(str((response.query_result.fulfillment_text))) > 0:
            response_list.append(format(response.query_result.fulfillment_text))
        for i in response.query_result.fulfillment_messages:
            try:
                response_list.append(
                    i.simple_responses.simple_responses[0].text_to_speech
                )
            except:

                for j in i.suggestions.suggestions:
                    suggestion.append(j.title)
        dict1 = {}
        dict1["Response"] = response_list
        dict1["Suggestion"] = suggestion
        return dict1


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print("Starting app on port %d" % (port))
    app.run(debug=True, port=port, host="0.0.0.0")
