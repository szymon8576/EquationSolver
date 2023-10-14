from base64 import b64decode
from io import BytesIO

from joblib import load
from flask import Flask, request
from flask_cors import CORS
from imageio import imread

from arithmeticOCR import convert_image_to_equation
from solver import solve_eq


app = Flask(__name__)
CORS(app)


label_encoder = load('label_encoder.pkl')
label_decoder = {i: label for i, label in enumerate(label_encoder.classes_)}


@app.route('/solve', methods=["POST"])
def solve():

    image_base64 = request.json["image"].split(",")[-1]
    image_cv2 = imread(BytesIO(b64decode(image_base64)))
    image_cv2 = image_cv2[:, :, :3]  # skip alpha channel

    parsing_status, parsing_result = convert_image_to_equation(image_cv2, label_decoder)

    if parsing_status is False:
        return {"processing_status": "ERROR", "error": parsing_result }
    else:
        instructions, status, solution = solve_eq(parsing_result["sympy_eq"])
        return {"processing_status": "FINALIZED",
                "equation": parsing_result["str_eq"], "instructions": instructions,
                "equation_status": status, "solution": solution}


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)