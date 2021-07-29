# Reference: https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask

from pickle import load
import re
import flask
from flask import request, jsonify

def load_model(saved_model_path):
    """
    Function to load the saved classification model, built my scikit learn.

    Arguments:
        saved_model_path: (str) location of saved model file
    Returns:
        model: sklearn model instance
    """

    return load(open(saved_model_path, 'rb'))

def load_preprocessing_modules(saved_preprocessing_file_path):
    """
    Function to load the saved preprocessing modules

    Arguments:
        saved_preprocessing_file_path: (str) location of saved preprocessing file
    Returns:
        preprocessing_module: sklearn preprocessing instance
    """

    return load(open(saved_preprocessing_file_path, 'rb'))

app = flask.Flask(__name__)

knn_model = load_model("./knn_model.pkl")
scaler = load_preprocessing_modules("./scaler.pkl")


@app.errorhandler(404)
def unimplemented_endpoint_error(e):
    """
    Handles case when user tries to request the unimplemented endpoint

    Returns:
        result: (json) returns error message as REST API response
        status_code: (int) url not implemented status code
    """

    result = {
        'message': 'Unimplented Endpoint: please make a POST request to URL/api/v1/predict, and pass parameters as JSON body'
    }

    return jsonify(result), 404


@app.errorhandler(400)
def feature_not_found(feature_name):
    """
    A function to handle exception when user has forgot to include a required feature.

    Arguments:
        feature_name: (str) name of a missing feature.
    Returns:
        result: returns error message as REST API response
        status_code: (int) user input error status code
    """

    result = {
        'message': 'Value for feature ' + feature_name + ' is missing'
    }

    return jsonify(result), 400

@app.errorhandler(400)
def typecasting_error(feature_name):
    """
    A function to handle exception when user has passed value of wrong type for a feature.

    Arguments:
        feature_name: (str) name of the feature, which had incorrect value.
    Returns:
        result: returns error message as REST API response
        status_code: (int) user input error status code  
    """

    result = {
        'message': 'Please provide Float value for ' + feature_name
    }

    return jsonify(result), 400

@app.errorhandler(500)
def runtime_exception():
    """
    Handles runtime exception occurs while serving model through REST API.

    Arguments:
        None.
    Returns:
        result: (json) returns error message as REST API response
        status_code: (int) server error status code
    """

    result = {
        'message': 'Server Error (Unhandled Exception Occured): Please make sure that you have passed correct number of arguments in POST request in json format'
    }

    return jsonify(result), 500


@app.route("/api/v1/predict", methods = ["POST"])
def inference_on_single_instance():
    """ 
    Provide POST REST endpoint for serving classifier inference on single instance.

    Arguments:
        None. (all parameters are passed through json body)  
    Returns:
        final_result: (json) give prediction results (if request is successfull) as REST API response, otherwise gives error message
    """

    required_features_values = []

    try:
        for i in range(1, 29):
            feature_name = 'V'+str(i)
            if feature_name in request.json:
                try:
                    val = float(request.json[feature_name])
                except ValueError:
                    return typecasting_error(feature_name) 

                required_features_values.append(val)
            else:
                return feature_not_found(feature_name)

        if 'Amount' in request.json:
            amount_val = float(request.json['Amount'])
            amount_val = scaler.transform([[amount_val]])[0][0]
            required_features_values.append(amount_val)
        else:
            return feature_not_found('Amount')

        predictions = knn_model.predict([required_features_values])
        final_result = {
            "prediction": int(predictions[0])
        }

    except Exception:
        return runtime_exception()

    return jsonify(final_result)


if(__name__ == "__main__"):
    app.run(port = 5000, debug = True)
     