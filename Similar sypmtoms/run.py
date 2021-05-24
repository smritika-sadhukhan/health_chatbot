# Importing Libraries
from flask import Flask
from Utils.symptoms_finder import Symptoms
from Utils.description import Description
from Utils.get_severity import GetSeverityDict
from Utils.precaution import GetprecautionDict
from flask import request, make_response, jsonify

app = Flask(__name__)

#Creating
symptoms_obj = Symptoms()
description_obj = Description()
get_severity_dict_obj = GetSeverityDict()
get_precaution_dict_obj = GetprecautionDict()

with open("Files/symptoms.pkl", "rb") as f:
    mynewlist = pickle.load(f)

chk_dis = ",".join(mynewlist).split(",")


@app.route("/get_precaution", methods=["POST"])
def precaution_getter():

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
        text = text.lower()
        data = text.split(",")
        data1 = []
        for i in data:
            i = i.split()
            i = " ".join(i)
            data1.append(i)
        logging.info(f"the input data is , {data1}")
        list_precaution = get_precaution_dict_obj.getprecautionDict(data1[0])
        return jsonify({"Suggestion": list_precaution})
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return resp


@app.route("/get_consult", methods=["POST"])
def advice_getter():

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
        text = text.lower()
        data = text.split(",")
        data1 = []
        for i in data:
            i = i.split()
            i = "_".join(i)
            data1.append(i)
        logging.info(f"the input data is , {data1}")
        consult_result = get_severity_dict_obj.calc_condition(data1)
        return jsonify({"Advise": consult_result})
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return resp


@app.route("/get_description", methods=["POST"])
def description_getter():

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
        text = text.lower()
        data = text.split(",")
        data1 = []
        for i in data:
            i = i.split()
            i = " ".join(i)
            data1.append(i)
        logging.info(f"the input data is , {data1}")
        description = description_obj.getDescription(data1[0])
        return jsonify({"Description": description})
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return resp


@app.route("/get_symptoms", methods=["POST"])
def symptoms_getter():

    if request.method == "POST":
        req = request.get_json(silent=True, force=True)
        res = processRequest(req)

        res = json.dumps(res, indent=4)
        r = make_response(res)
        r.headers["Content-Type"] == "application/json0"
        return r

    def processRequest(req):
        query_response = req["queryResult"]
        print(query_response)
        text = query_response.get("queryText", None)
        parameters = query_response.get("parameters", None)

        res = get_data()

        return res


@app.route("/get_disease", methods=["POST"])
def disease_getter():

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
        data = text.split(",")
        data1 = []
        for i in data:
            i = i.split()
            i = "_".join(i)
            data1.append(i)
        logging.info(f"the input data is , {data1}")
        similar_symptopms, possible_disease = symptoms_obj.similar_symptoms(data1)
        return jsonify({"Possible disease": possible_disease})
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return resp


if __name__ == "__main__":
    app.run()
