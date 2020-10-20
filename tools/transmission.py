import requests
import os
import hashlib
import json
import re
from glob import glob
import zipfile

UPLOAD_URL = "http://songbook.ushow.media:91/face_annotation/face-annotation/upload-one"
REQUEST_URL = "http://songbook.ushow.media:91/face_annotation/face-annotation/request-one"

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
            print("请求失败:", result["err"])
            return {"status": False, "image": None, "anno": None, "annotate_tot_num": None,
                    "annotate_user_num": None, "annotate_user_face_num": None,
                    "annotate_user_face_tot_num": None, "tot_num": None}
        if not os.path.exists(DOWNLOAD_DIRECTORY):
            os.makedirs(DOWNLOAD_DIRECTORY)

        image = os.path.join(DOWNLOAD_DIRECTORY, result["img_name"])
        anno = os.path.join(DOWNLOAD_DIRECTORY, "{}.json".format(result["img_name"].split(".")[0]))

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
            "anno": anno,
            "annotate_tot_num": result["annotate_tot_num"],
            "annotate_user_num": result["annotate_user_num"],
            "annotate_user_face_num": result["annotate_user_face_num"],
            "annotate_user_face_tot_num": result["annotate_user_face_tot_num"],
            "tot_num": result["tot_num"]
        }
        return result

    def download(self, url, dst):
        try:
            if os.path.exists(dst):
                return True
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
        # image_md5 = hashlib.md5(open(img_url, 'rb').read()).hexdigest()
        self.post_data["img_url"] = os.path.basename(img_url)
        self.post_data["face_num"] = face_num
        file = {'face_point': open(anno_url, "rb")}
        result = post_one(UPLOAD_URL, self.post_data, files=file)
        return result

class DataManager:
    def __init__(self, name=None):
        if name is None:
            from controller.login import CACHE_DIR
            with open(os.path.join(CACHE_DIR, "user_info.txt")) as f:
                lines = f.readlines()
                name = lines[0].strip()
                password = lines[1].strip()
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
        return self.image, self.anno, result["annotate_user_face_num"], result["annotate_user_face_tot_num"]

    def upload_data(self):
        if self.image is not None and self.anno is not None:
            filename = os.path.basename(self.image).split(".")[0]
            anno_list = glob(os.path.join(ANNOTATION_DIRECTORY, "{}*.pts".format(filename)))
            f = zipfile.ZipFile('upload_tmp_anno_data.zip', 'w', zipfile.ZIP_DEFLATED)
            for anno in anno_list:
                f.write(anno)
            f.close()
            result = self.uploader.run(self.image, "upload_tmp_anno_data.zip", len(anno_list))
            os.remove('upload_tmp_anno_data.zip')
            if result["err"] == "ok":
                return True
            else:
                print(result["err"])
                return False
        else:
            return False


def post_one(url, post_data, files=None):
    try:
        req = requests.post(url, post_data, files=files)
    except:
        print("post失败，可能是没网")
        return {"err": "ConnectionError"}
    txt = req.text
    try:
        txt = json.loads(txt)
    except:
        print("请求发生错误:", txt)
        return {"err": txt}
    return txt


def test_request():
    post_data = {
        "user_name": "yangjianli"
    }
    return post_one(REQUEST_URL, post_data)


def test_upload():
    img_url = "3c696038d77f2c13902351d008c2a60e.jpg"
    post_data = {
        "user_name": "lixuesong",
        "img_url": img_url,
        "face_num": 100
    }
    files = {'face_point': open("/Users/darkn/code/work/MarkLabels/tools/transmission.py", "rb")}
    r = post_one(UPLOAD_URL, post_data, files=files)
    print(r)

if __name__ == "__main__":
    print(test_upload())