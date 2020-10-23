from json import loads
import numpy as np
from controller.data_labels import AGE
from tools.point2idx import points_list

def convert_age_label(value):
    for age in AGE:
        age_span = eval(age)
        if not isinstance(age_span, tuple):
            break
        if value < age_span[1]:
            return age
    return "未标"

def read_anno(file):
    with open(file) as f:
        json = loads(f.read())
    json = json["faces"]
    for j in json:
        landmark = j["landmark"]
        new_landmark = []
        for k in points_list:
            loc = landmark[k]
            x = loc["x"]
            y = loc["y"]
            new_landmark.append(x)
            new_landmark.append(y)
        j["landmark"] = new_landmark
        if "attributes" not in j:
            j["attributes"] = {}
            continue
        attr = j["attributes"]
        gender = attr["gender"]["value"]
        if gender == "Male":
            gender = "男"
        else:
            gender = "女"
        attr["gender"] = gender

        age = attr["age"]["value"]
        age = convert_age_label(int(age))
        attr["age"] = age

        smile = attr["smile"]
        expression = "笑" if int(smile["value"]) > int(smile["threshold"]) else "未标"
        del attr["smile"]
        attr["expression"] = expression

    return json

def view_landmark(file):
    import cv2
    token = "." + file.rsplit(".")[-1]
    anno = file.replace(token, "F.txt")
    landmark = read_anno(anno)["landmark"]
    image = cv2.imread(file)
    landmark = np.array(landmark, dtype=float).reshape(-1, 2).astype(int)
    for x, y in landmark:
        cv2.circle(image, (x, y), 1, (0, 255, 0), 1, cv2.LINE_4)
    image = cv2.resize(image, (600, 600))
    cv2.imshow("file", image)
    cv2.waitKey()

if __name__ == '__main__':
    view_landmark("/Users/darkn/Desktop/test/face_3141.png")