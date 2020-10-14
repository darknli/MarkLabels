import requests
import os
import hashlib
import json

UPLOAD_URL = "http://yangjianli.box.ushow.media:91/face_annotation/face-annotation/upload-one"
REQUEST_URL = "http://yangjianli.box.ushow.media:91/face_annotation/face-annotation/request-one"

DOWNLOAD_DIRECTORY = "dataset"
ANNOTATION_DIRECTORY = "annotation"

class Downloader:
    def __init__(self, name):
        self.post_data = {
            "user_name": name
        }

    def run(self):
        result = post_one(REQUEST_URL, self.post_data)
        if result["err"] != "ok":
            return {"status": False, "image": None, "anno": None}
        if not os.path.exists(DOWNLOAD_DIRECTORY):
            os.makedirs(DOWNLOAD_DIRECTORY)

        md5 = hashlib.md5(result["img_url"].encode()).hexdigest()
        image = os.path.join(DOWNLOAD_DIRECTORY, "{}.jpg".format(md5))
        anno = os.path.join(DOWNLOAD_DIRECTORY, "{}.json".format(md5))

        for i in range(5):
            if i != 0:
                print("第%d次尝试下载...", i)
            print("正在下载%s\n到%s" % (result["img_url"], image))
            status = self.download(result["img_url"], image)
            if not status:
                continue
            print("正在下载%s" % result["face_annotation_url"])
            status = self.download(result["face_annotation_url"], anno)
            if status:
                break
        result = {
            "status": status,
            "image": image,
            "anno": anno
        }
        return result

    def download(self, url, dst):
        try:
            r = requests.get(url)
            with open(dst, 'wb') as f:
                f.write(r.content)
        except BaseException:
            print("下载过程出了问题")
            return False
        return True

class Uploader:
    def __init__(self, name):
        self.post_data = {
            "user_name": name,
            "face_num": 1
        }

    def run(self, img_url, anno_url, face_num):
        image_md5 = hashlib.md5(open(img_url, 'rb').read()).hexdigest()
        self.post_data["img_url"] = "%s.png" % image_md5
        self.post_data["face_num"] = face_num
        file = {'face_point': open(anno_url, "rb")}
        result = post_one(UPLOAD_URL, self.post_data, files=file)
        return result

class DataManager:
    def __init__(self, name):
        self.downloader = Downloader(name)
        self.uploader = Uploader(name)
        self.image = None
        self.anno = None

    def download_data(self):
        result = self.downloader.run()
        if result["status"]:
            self.image = result["image"]
            self.anno = result["anno"]
        else:
            raise ValueError("下载失败！检查输入参数是否正确")

    def upload_data(self):
        result = self.uploader.run(self.image, self.anno, 1)


def post_one(url, post_data, files=None):
    req = requests.post(url, post_data, files=files)
    return json.loads(req.text)


def test_request():
    post_data = {
        "user_name": "yangjianli"
    }
    return post_one(REQUEST_URL, post_data)


def test_upload():
    img_url = "3c696038d77f2c13902351d008c2a60e.jpg"
    post_data = {
        "user_name": "yangjianli",
        "img_url": img_url,
        "face_num": 1
    }
    files = {'face_point': open("/Users/darkn/code/work/MarkLabels/tools/transmission.py", "rb")}
    post_one(UPLOAD_URL, post_data, files=files)


if __name__ == "__main__":
    # d = Downloader("yangjianli")
    # print(d.run())
    u = Uploader("yangjianli")
    s = u.run("dataset/480ec494452237bbb6052a2484404026.jpg",
          "dataset/480ec494452237bbb6052a2484404026.json", 1)
    print(s)