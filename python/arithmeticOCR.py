import cv2
import numpy as np
from scipy import stats
from sympy.logic.boolalg import BooleanTrue, BooleanFalse
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from sympy import degree, symbols
import requests
import json
import re

transformations = (standard_transformations + (implicit_multiplication_application,))
def str_to_sympy(eq):
    """
    Converts an equation stored in a string to a Sympy Equation.

    :param eq: Equation in string format, e.g., "2x+3=10".
    :return: A tuple containing parsing status (True - success, False - failed) and parsed Sympy Equation.
    """

    try:
        parsed = parse_expr("Eq(" + eq.replace("=", ",") + ")", evaluate=False, transformations=transformations)

        if isinstance(parsed, BooleanTrue) or isinstance(parsed, BooleanFalse):
            # if equation has zero or infinitely many solutions
            return True, parsed

        elif degree(parsed.lhs, symbols("x")) >= 2 or degree(parsed.rhs, symbols("x")) >= 2:
            # if a polynomial of degree >=2 was encountered
            return False, "degree >= 2 is not allowed"

        elif bool(re.search(r'x\d', eq)):
            # if in equation x is followed by digit (for example "20 + x5 = 4" - it indicates wrong recognition)
            return False, "encountered x-symbol followed by digit"

        else:
            # if equation has exactly one solution
            return True, parsed

    except Exception as e:
        return False, str(e)


def fetch_tfserving(images, label_decoder):

    try:
        tf_serving_url = app.config['TFSERVING_URL'] + '/v1/models/ArithmeticOCR:predict'
        instances = [np.array(np.expand_dims(image, 2)).tolist() for image in images]
        response = requests.post(tf_serving_url, json={"instances": instances})

        if response.status_code == 200:
            return response.json()["predictions"]
        else:
            print('Failed to get a valid response from TensorFlow Serving')

    except Exception as e:
        print(str(e))


def prepare_image_for_recognition(image, bin_lt=130):
    # convert to grayscale and perform thresholding
    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, img = cv2.threshold(img, bin_lt, 255, cv2.THRESH_BINARY)

    # convert image to an integer format and invert values
    img = (img / 255).astype(np.uint8)
    img = 1 - img

    # pad image to obtain ~ 1:1 ratio
    height, width = img.shape[0], img.shape[1]
    desired_size = max(height, width) * 1.1
    delta_y, delta_x = int((desired_size - height) // 2), int((desired_size - width) // 2)
    img = cv2.copyMakeBorder(img, delta_y, delta_y, delta_x, delta_x, cv2.BORDER_CONSTANT, value=0)

    # perform dilation
    img = cv2.resize(img, (92, 92))
    img = cv2.dilate(img, np.ones((3, 3), np.uint8), iterations=1)
    img = cv2.resize(img, (45, 45))

    return img


def eliminate_outlier_contours(contours_coords):

    if len(contours_coords) <= 4:
        return contours_coords

    contours = [{"coords": c, "x": np.median(c[:, 0, 0]), "y": np.median(c[:, 0, 1])} for i, c in enumerate(contours_coords)]

    # filter contours by number of points in contour
    contours = [c for c in contours if len(c["coords"]) > 20]

    # by distance to nearest object
    central_points = np.array([[contour["x"], contour["y"]] for contour in contours])
    distances = np.linalg.norm(central_points[:, np.newaxis, :] - central_points, axis=2)
    np.fill_diagonal(distances, np.inf)
    min_distances = np.min(distances, axis=1)
    z_scores = stats.zscore(min_distances)
    contours = [contour for i, contour in enumerate(contours) if abs(z_scores[i]) < 3]

    # by median-y value
    z_scores = stats.zscore([contour["y"] for contour in contours])
    contours = [contour for i, contour in enumerate(contours) if abs(z_scores[i]) < 3]

    # print("Eliminated outliers=", len(contours_coords) - len(contours))
    return [contour["coords"] for contour in contours]


def group_elements(li, grouping_condition):
    """
    Iterates over consecutive elements in the list and puts them in one group as long as the grouping_condition is met.
    """
    out = []
    last = li[0]
    for x in li:
        if grouping_condition(x, last):
            yield out
            out = []
        out.append(x)
        last = x
    yield out
    
    
def stack_contours_vertically(contours, threshold=20):
    """
    Stacks contours vertically if distance between their median x-values does not exceed threshold value.
    """
    
    if len(contours) == 0: 
        return contours

    contours_ = [{"coords": c, "x": np.median(c[:, 0, 0]), "y": np.median(c[:, 0, 1])} for i, c in enumerate(contours)]

    # sort contours by median x-value and group them
    contours_ = sorted(contours_, key=lambda c: c["x"])
    grouping_condition = lambda a, b:  False if (a["x"] - b["x"] < threshold) else True
    grouped_contours = list(group_elements(contours_, grouping_condition))

    # stack grouped contours
    return [np.vstack([contour["coords"] for contour in group]) for group in grouped_contours]


def detect_contours_in_image(image, canny_lt=120):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    img = cv2.Canny(img, canny_lt, 255)

    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)), iterations=1)

    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours = eliminate_outlier_contours(contours)
    contours = stack_contours_vertically(contours)

    return contours


def resize_to_desired_width(image, desired_width=500):
    aspect_ratio = float(image.shape[1]) / image.shape[0]
    height = int(desired_width / aspect_ratio)
    return cv2.resize(image, (desired_width, height))


def identify_objects_in_image(image, label_decoder, canny_lt, bin_lt):

    image_ = resize_to_desired_width(image)
    contours = detect_contours_in_image(image_, canny_lt)
    bounding_boxes = [cv2.boundingRect(contour) for contour in contours if cv2.contourArea(contour) > 20]

    if len(bounding_boxes) == 0:
        return []

    preprocessed_images = [
        prepare_image_for_recognition(image_[y:y + height, x:x + width], bin_lt=bin_lt)
        for x, y, width, height in bounding_boxes
    ]

    predictions = fetch_tfserving(preprocessed_images, label_decoder=label_decoder)
    predicted_labels = [np.argmax(p) for p in predictions]
    labels = [label_decoder[predicted_label] for predicted_label in predicted_labels]

    identified_objects = []
    for idx, (x, y, width, height) in enumerate(bounding_boxes):
        identified_objects.append({"y": y + height // 2, "x": x + width // 2, "label": labels[idx]})

    return sorted(identified_objects, key=lambda elem: elem["x"])


def recognize_equation_in_image(image, label_decoder):

    for canny_lt in [120, 85, 50, 100, 130, 150, 200]:
        for bin_lt in [130, 150, 180, 100, 90]:

            identified_objects = identify_objects_in_image(image, label_decoder, canny_lt, bin_lt)
            equation = "".join([elem["label"] for elem in identified_objects]).replace("X", "x")
            parsing_status, parsing_result = str_to_sympy(equation)

            if parsing_status is True:
                return True, {"str_eq": equation, "sympy_eq": parsing_result}

    return False, "Couldn't recognize this image"

