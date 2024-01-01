from base64 import b64decode
from io import BytesIO

from joblib import load
from flask import Flask, request
from flask_cors import CORS
from imageio import imread
# import psycopg2
# import os

from arithmeticOCR import recognize_equation_in_image
from solver import solve_eq

app = Flask(__name__)
app.config.from_pyfile('config.py')
CORS(app)

label_encoder = load('label_encoder.pkl') # TODO
label_decoder = {i: label for i, label in enumerate(label_encoder.classes_)}

# conn = psycopg2.connect(
#     host=os.environ.get('PG_HOST'),
#     database=os.environ.get('PG_DATABASE'),
#     user=os.environ.get('PG_USER'),
#     password=os.environ.get('PASSWORD')
# )

@app.route('/solve', methods=["POST"])
def solve():

    image_base64 = request.json["image"].split(",")[-1]
    image_cv2 = imread(BytesIO(b64decode(image_base64)))
    image_cv2 = image_cv2[:, :, :3]  # skip alpha channel

    parsing_status, parsing_result = recognize_equation_in_image(image_cv2, label_decoder)

    if parsing_status is False:
        # cur = conn.cursor()
        # cur.execute("INSERT INTO failed_recognitions (image) VALUES (%s)", (image_base64,))
        # conn.commit()

        return {"processing_status": "ERROR", "error": parsing_result}

    else:
        instructions, status, solution = solve_eq(parsing_result["sympy_eq"])
        return {"processing_status": "FINALIZED",
                "equation": parsing_result["str_eq"], "instructions": instructions,
                "equation_status": status, "solution": solution}


@app.route('/health-check', methods=["GET"])
def health_check():
    return "OK", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)