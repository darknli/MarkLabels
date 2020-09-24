from json import loads
import numpy as np

def read_anno(file):
    with open(file) as f:
        json = loads(f.read())
    json = json["faces"]
    for j in json:
        landmark = j["landmark"]
        new_landmark = []
        for k, loc in landmark.items():
            x = loc["x"]
            y = loc["y"]
            new_landmark.append(x)
            new_landmark.append(y)
        j["landmark"] = new_landmark
    return json[0]

def view_landmark(file):
    import cv2
    token = "." + file.rsplit(".")[-1]
    anno = file.replace(token, "F.txt")
    landmark = read_anno(anno)["landmark"]
    image = cv2.imread(file)
    landmark = np.array(landmark, dtype=float).reshape(-1, 2).astype(int)
    print(len(landmark))
    for x, y in landmark:
        cv2.circle(image, (x, y), 1, (0, 255, 0), 1, cv2.LINE_4)
    image = cv2.resize(image, (600, 600))
    cv2.imshow("file", image)
    cv2.waitKey()

if __name__ == '__main__':
    view_landmark("/Users/darkn/Desktop/test/face_3141.png")