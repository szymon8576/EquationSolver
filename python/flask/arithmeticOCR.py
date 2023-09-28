from tensorflow import argmax
import cv2
import numpy as np
from scipy import stats
from sympy.logic.boolalg import BooleanTrue, BooleanFalse
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from sympy import degree, symbols
import requests
import json

transformations = (standard_transformations + (implicit_multiplication_application,))


def str_to_sympy(eq):

    try:
        parsed = parse_expr("Eq(" + eq.replace("=", ",") + ")",
                            evaluate=False,
                            transformations=transformations)

        if isinstance(parsed, BooleanTrue) or isinstance(parsed, BooleanFalse):
            return True, parsed
        elif degree(parsed.lhs, symbols("x")) >= 2 or degree(parsed.rhs, symbols("x")) >= 2:
            return False, "degree >= 2 is not allowed"
        else:
            return True, parsed

    except Exception as e:
        return False, str(e)


def predict_label(image, label_decoder):

    # prediction = model(np.array([image])) # model.predict(np.array([image]), verbose=0)
    # Specify the URL of your TensorFlow Serving server
    tf_serving_url = 'https://eq-solver-tf-serving.onrender.com/v1/models/arithmeticOCR_model:predict'
    # Replace with the actual URL for your TensorFlow Serving API

    try:
        # Send a POST request to TensorFlow Serving
        response = requests.post(tf_serving_url, json={"instances": np.array([np.expand_dims(image, 2)]).tolist()  })

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the response JSON
            prediction = response.json()["predictions"][0]
            # print(prediction)
            predicted_label = np.argmax(prediction)
            # print(predicted_label)
            encoded_label = label_decoder[predicted_label]
            # print(encoded_label)
            return encoded_label

            # Return the prediction as a JSON response
        else:
            print('Failed to get a valid response from TensorFlow Serving')

    except Exception as e:
        print(str(e))





def center_and_make_square(image):
    # convert to grayscale and perform thresholding
    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, img = cv2.threshold(img, 130, 255, cv2.THRESH_BINARY)

    # convert image to integer format and invert values
    img = (img / 255).astype(np.uint8)
    img = 1 - img

    height, width = img.shape[0], img.shape[1]

    # pad image to obtain ~ 1:1 ratio
    desired_size = max(height, width) * 1.1
    delta_y, delta_x = int((desired_size - height) // 2), int((desired_size - width) // 2)
    img = cv2.copyMakeBorder(img, delta_y, delta_y, delta_x, delta_x, cv2.BORDER_CONSTANT, value=(0))

    # perform dilation before passing img to AI model
    img = cv2.resize(img, (92, 92))
    img = cv2.dilate(img, np.ones((3, 3), np.uint8), iterations=1)
    img = cv2.resize(img, (45, 45))

    return img


def group_contours(li, groupping_condition):
    out = []
    last = li[0]
    for x in li:
        if groupping_condition(x, last):
            yield out
            out = []
        out.append(x)
        last = x
    yield out


def eliminate_outlier_contours(contours):
    if len(contours) <= 4:
        return contours

    contours_ = [{
        "coords": c, "x": np.median(c[:, 0, 0]), "y": np.median(c[:, 0, 1])
    } for i, c in enumerate(contours)]

    # print([len(c["coords"]) for c in contours_])
    # print([cv2.contourArea(c["coords"]) for c in contours_])

    # by number of points in contour
    contours_ = [c for c in contours_ if len(c["coords"]) > 20]


    # by distance to nearest object
    points = np.array([[contour["x"], contour["y"]] for contour in contours_])
    distances = np.linalg.norm(points[:, np.newaxis, :] - points, axis=2)
    np.fill_diagonal(distances, np.inf)
    min_distances = np.min(distances, axis=1)
    z_scores = stats.zscore(min_distances)
    # print([round(z,2) for z, x in zip(z_scores, [contour["x"] for contour in contours_])])
    contours_ = [contour for i, contour in enumerate(contours_) if abs(z_scores[i]) < 2]

    z_scores = stats.zscore([contour["y"] for contour in contours_])
    # print([round(z,2) for z, x in zip(z_scores, [contour["y"] for contour in contours_])])
    contours_ = [contour for i, contour in enumerate(contours_) if abs(z_scores[i]) < 2.2]  # dists_from_median[i] < 2.2 * median_y]

    # print("Eliminated outliers=", len(contours) - len(contours_))
    return [contour["coords"] for contour in contours_]


def stack_contours_vertically(contours):
    if len(contours) == 0:
        return contours

    contours_ = [{
        "coords": c, "x": np.median(c[:, 0, 0]), "y": np.median(c[:, 0, 1])
    } for i, c in enumerate(contours)]

    # sort contours by mean x-value and group them
    contours_ = sorted(contours_, key=lambda c: c["x"])

    # print("contours distances:")
    # print([c["x"] for c in contours_])
    # print([c["y"] for c in contours_])

    groupping_condition = lambda a, b:  False if (a["x"] - b["x"] < 20) else True
    groupped_contours = list(group_contours(contours_, groupping_condition))

    # stack grouped contours
    return [np.vstack([contour["coords"] for contour in group]) for group in groupped_contours]


def find_contours(image, canny_lower_threshold):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    img = cv2.Canny(img, canny_lower_threshold, 255)
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)), iterations=1)

    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    contours = eliminate_outlier_contours(contours)
    contours = stack_contours_vertically(contours)

    img2 = image.copy()
    for cnt in contours:
        hull = cv2.convexHull(cnt)
        cv2.drawContours(img2, [hull], -1, (0, 0, 255), 1)

    cv2.imwrite("debug.png", img2)

    return contours


def find_bounding_boxes(contours):
    return [cv2.boundingRect(contour) for contour in contours if cv2.contourArea(contour) > 50]


def resize_to_desired_width(image, desired_width=500):
    aspect_ratio = float(image.shape[1]) / image.shape[0]
    desired_height = int(desired_width / aspect_ratio)
    return cv2.resize(image, (desired_width, desired_height))


def identify_objects(bounding_boxes, image, label_decoder):
    identified_objects = []
    for x, y, width, height in bounding_boxes:
        centered = center_and_make_square(image[y:y + height, x:x + width])

        label = predict_label(centered, label_decoder=label_decoder)
        identified_objects.append(
            {"y": y + height // 2,
             "x": x + width // 2,
             "label": label}
        )

    return sorted(identified_objects, key=lambda elem: elem["x"])


def identify_objects_in_image(image, label_decoder, canny_lower_threshold):

    image_resized = resize_to_desired_width(image)
    contours = find_contours(image_resized, canny_lower_threshold)
    bounding_boxes = find_bounding_boxes(contours)
    identified_objects = identify_objects(bounding_boxes, image_resized, label_decoder)
    return identified_objects


def convert_image_to_equation(image, label_decoder):

    for canny_lt in [120, 85, 50, 100, 130, 150, 200]:

        identified_objects = identify_objects_in_image(image, label_decoder, canny_lt)
        equation = "".join([elem["label"] for elem in identified_objects]).replace("X", "x")
        # print(equation)
        parsing_status, parsing_result = str_to_sympy(equation)

        if parsing_status is True:
            return True, {"str_eq": equation, "sympy_eq": parsing_result}

    return False, "Couldn't recoginze this equation"

