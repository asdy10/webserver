import socket
from twocaptcha import TwoCaptcha
import time
import threading
import pygame as pg
from io import BytesIO
import sqlite3
import base64
from PIL import Image
import cv2 as cv
import numpy as np
import glob


def diff_pictures(picture, picture2):
    try:
        count = 0
        image = cv.imread(picture)
        image2 = cv.imread(picture2)
        for i in range(300):
            for j in range(300):
                if (image[i, j][0] != image2[i, j][0]) or (image[i, j][1] != image2[i, j][1]) or (
                        image[i, j][2] != image2[i, j][2]):
                    count += 1
                # print(i,j,image[i, j],image2[i, j])
        print("                         different =", count)
    except Exception as e:
        print(e, "cant find picture")


def is_hash_exist(imghash, cursor):
    global count_copy

    imghash = imghash.encode("utf-8")
    # print(imghash[:80])
    try:
        cursor.execute(" SELECT id FROM geetest WHERE hash=?", (imghash,))
        result = cursor.fetchall()
        if (result != []):

            count_copy += 1
            print("                         count copy =", count_copy)
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


def is_simple_hash_exist(simple_hash, cursor):
    global count_copy

    simple_hash = simple_hash.encode("utf-8")
    # print(simple_hash[:80])
    try:
        cursor.execute(" SELECT id FROM geetest WHERE simple_hash=?", (simple_hash,))
        result = cursor.fetchall()
        if (result != []):

            count_copy += 1
            print("                                                  count copy =", count_copy)
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


def check_user_key(data):
    try:
        global key_arr
        if (data == "qwerasdfzxcv10"):
            return 0
        else:
            for i in range(1, 20):
                if (key_arr[i] == data.split("key=")[1].split("&")[0]):
                    return i
            else:
                return -1
    except:
        return -1


def normalize_img(img):
    normalizedImg = np.zeros((443, 345))
    normalizedImg = cv.normalize(img, normalizedImg, 0, 255, cv.NORM_MINMAX)
    return normalizedImg


def get_normalize_hash(imghash):
    global arr
    # print(imghash[:80])
    imghash = imghash.encode("utf-8")
    dataImg64 = base64.b64decode(imghash)
    img = "image.png"
    f = open(img, 'wb')
    f.write(dataImg64)
    f.close()
    WHITE = (255, 255, 255)
    sc = pg.image.load(img)
    for x in range(len(arr)):
        pg.draw.circle(sc, WHITE, arr[x], 1)
    pg.image.save(sc, img)
    pg.quit()
    with open(img, "rb") as image:
        b64string = base64.b64encode(image.read())
    # print(b64string.decode("utf-8")[:80])
    return b64string.decode("utf-8")


def save_image(imghash, cursor):
    start_time = time.time()
    cursor.execute("SELECT COUNT(*) FROM geetest")
    result = cursor.fetchall()
    table_size = int(result[0][0])
    # global arr
    imghash = imghash.encode("utf-8")
    dataImg64 = base64.b64decode(imghash)
    default_name = "C:\\Users\\WinServer\\AppData\\Local\\Programs\\Python\\Python39\\Scripts\\server\\photo\\"
    img = default_name + str(time.time()) + ".png"
    f = open(img, 'wb')  # write binary
    f.write(dataImg64)
    f.close()  # may be omitted
    simple_hash = imghash[10000:11000] + imghash[20000:21000] + imghash[30000:31000]
    # with open(img, "rb") as image:
    #	b64string = base64.b64encode(image.read())

    cursor.execute("INSERT INTO geetest (id, hash, name, simple_hash) VALUES(?, ?, ?,?)",
                   (table_size, imghash, img, simple_hash))


# print("save")
def get_answer(imghash):
    imghash = imghash.encode("utf-8")
    decode_text = imghash
    # print(len(imghash),imghash[:80])

    W = 345
    H = 443
    WHITE = (255, 255, 255)
    RED = (225, 0, 50)
    GREEN = (0, 225, 0)
    BLUE = (0, 0, 225)

    sc = pg.display.set_mode((W, H))
    sc.fill((100, 150, 200))
    output = BytesIO(base64.b64decode(decode_text))
    dog_surf = pg.image.load(output)
    dog_rect = dog_surf.get_rect(
        bottomright=(W, H))
    sc.blit(dog_surf, dog_rect)
    pg.display.update()


def get_resolve_by_hash(imghash):
    try:
        with sqlite3.connect("database2.db") as db:
            start_time = time.time()

            cursor = db.cursor()
            if (is_hash_exist(imghash, cursor) == True):
                cursor.execute("SELECT resolve FROM geetest WHERE hash=?", (imghash.encode("utf-8"),))
                result = cursor.fetchall()
                if (result != [] and result != [(None,)]):
                    return str(result[0][0])
                else:
                    return "-1"
            else:
                save_image(imghash, cursor)
                # print("save")
                return "-1"
    except Exception as e:
        print(e, "get_resolve_by_hash")
        return "-1"


def get_resolve_by_simple_hash(simple_hash):
    global hash_array
    global resolve_array
    x = 0
    global count_copy
    try:
        x = hash_array.index(simple_hash.encode("utf-8"))
        answer = str(resolve_array[x])
        count_copy += 1
        print("copy", count_copy)
        return answer
    except Exception as e:
        return "-1"


def add_image_to_db(imghash):
    i = -1
    with sqlite3.connect("database2.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM geetest")
        result = cursor.fetchall()
        table_size = int(result[0][0])
    for img in glob.glob(
            "C:\\Users\\Click01\\AppData\\Local\\Programs\\Python\\Python39-32\\Scripts\\for_test\\photo\\*.png"):
        i += 1
        print(i)
        with open(img, "rb") as image:
            b64string = base64.b64encode(image.read())
        with sqlite3.connect("data.db") as db:
            cursor = db.cursor()
            if (is_hash_exist(b64string, cursor) == False):
                cursor.execute("INSERT INTO geetest (id, hash, name) VALUES(?, ?, ?)",
                               (i - count + table_size, b64string, img))


def get_resolve_by_id(id, cursor):
    cursor.execute("SELECT resolve FROM geetest WHERE id=?", (id,))
    result = cursor.fetchall()
    try:

        if (result != [] and result != [(None,)]):
            return str(result)
        else:
            return -1
    except Exception as e:
        print(e, "get_resolve_by_id")
        return -1


def set_resolve(id, resolve, cursor):
    try:
        cursor.execute("UPDATE geetest SET resolve=? WHERE id=? ", (resolve, id))
    except Exception as e:
        print(e, "set_resolve")


def add_solves_to_db():
    while True:
        try:
            with sqlite3.connect("database2.db") as db:
                cursor = db.cursor()
                cursor.execute("SELECT COUNT(*) FROM geetest")
                result = cursor.fetchall()
                table_size = int(result[0][0])

            for i in range(table_size):
                try:
                    start_time = time.time()
                    img = ""
                    with sqlite3.connect("database2.db") as db:
                        cursor = db.cursor()
                        if (get_resolve_by_id(i, cursor) == -1):
                            img = cursor.execute("SELECT name FROM geetest WHERE id=?", (i,)).fetchall()[0][0]
                    if img != "":
                        with Image.open(img) as ima:
                            image_jpg = img.split(".png")[0] + ".jpg"
                            ima.save(image_jpg)
                        try:
                            solver = TwoCaptcha('3f40f8718ec3a9f8215c54a23eb29f1c')
                            answer = solver.coordinates(image_jpg)
                            answer = answer["code"].split("coordinates:")[1]
                            if len(answer) > 15:
                                with sqlite3.connect("database2.db") as db:
                                    cursor = db.cursor()
                                    set_resolve(i, answer, cursor)
                                    print("get answer for", i, time.time() - start_time)
                        except Exception as e:
                            print(e)
                except:
                    pass
        except Exception as e:
            print(e)


class diff_image():  # класс по сравнению картинок.
    """Потоковый обработчик"""

    def __init__(self, arr):
        """Инициализация потока"""
        threading.Thread.__init__(self)
        self.queue = arr
        self.full_array = arr

    def run(self):
        """Запуск потока"""
        while self.queue != []:
            img = self.queue.pop()
            result = self.find_all_copy(img)

    def CalcImageHash(FileName):
        image = cv.imread(FileName)  # Прочитаем картинку
        # resized = cv.resize(image, (128,128), interpolation = cv.INTER_AREA) #Уменьшим картинку
        gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)  # Переведем в черно-белый формат
        avg = gray_image.mean()  # Среднее значение пикселя
        ret, threshold_image = cv.threshold(gray_image, avg, 255, 0)  # Бинаризация по порогу

        # Рассчитаем хэш
        _hash = ""
        for x in range(443):
            for y in range(345):
                val = threshold_image[x, y]
                if val == 255:
                    _hash = _hash + "1"
                else:
                    _hash = _hash + "0"

        return _hash

    def CompareHash(hash1, hash2):
        l = len(hash1)
        i = 0
        count = 0
        while i < l:
            if hash1[i] != hash2[i]:
                count = count + 1
            i = i + 1
        return count

    def find_all_copy(self, img):
        imghash = CalcImageHash(img)
        for i in self.full_array:
            x = 1000
            res = ""
            if (i != img):
                imghash2 = CalcImageHash(i)
                y = CompareHash(imghash, imghash2)
                if y < x:
                    x = y
                    res = i
        if (x < 100):
            return res
        else:
            return " "


def CalcImageHash(FileName):
    image = cv.imread(FileName)  # Прочитаем картинку
	# resized = cv.resize(image, (128,128), interpolation = cv.INTER_AREA) #Уменьшим картинку
    gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)  # Переведем в черно-белый формат
    avg = gray_image.mean()  # Среднее значение пикселя
    ret, threshold_image = cv.threshold(gray_image, avg, 255, 0)  # Бинаризация по порогу

    # Рассчитаем хэш
    _hash = ""
    for x in range(443):
        for y in range(345):
            val = threshold_image[x, y]
            if val == 255:
                _hash = _hash + "1"
            else:
                _hash = _hash + "0"

    return _hash


def CompareHash(hash1, hash2):
    l = len(hash1)
    i = 0
    count = 0
    while i < l:
        if hash1[i] != hash2[i]:
            count = count + 1
        i = i + 1
    return count


def set_simple_hash(id, cursor):
    result = cursor.execute("SELECT simple_hash FROM geetest WHERE id=?", (id,)).fetchall()
    if (result == [] or result == [(None,)]):
        img_name = cursor.execute("SELECT name FROM geetest WHERE id=?", (id,)).fetchall()[0][0]
        x = CalcImageHash(img_name)
        cursor.execute("UPDATE geetest SET simple_hash=? WHERE id=? ", (x, id))
    # print("set simple_hash to", id)


def find_same_simple_hash(id, cursor):
    default_simple_hash = cursor.execute("SELECT simple_hash FROM geetest WHERE id=?", (id,)).fetchall()[0][0]
    res_different = 10000
    res_pos = 0
    start_time = time.time()
    for i in range(1, id):
        simple_hash = cursor.execute("SELECT simple_hash FROM geetest WHERE id=?", (i,)).fetchall()[0][0]
        different = CompareHash(default_simple_hash, simple_hash)
        if different < res_different and i != id:
            res_different = different
            res_pos = i
    # print("different simple hash",res_different,res_pos, time.time()-start_time)

    if res_different < 1000:
        print(res_different)
        return res_pos
    else:
        return -1


def set_resolve_by_simple_hash():
    with sqlite3.connect("database2.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM geetest")
        result = cursor.fetchall()
        table_size = int(result[0][0])
    for i in range(1, table_size):
        set_simple_hash(i, cursor)
        with sqlite3.connect("database2.db") as db:
            cursor = db.cursor()
            result = cursor.execute("SELECT resolve FROM geetest WHERE id=?", (i,)).fetchall()

            if (result == [] or result == [(None,)]):
                position_same_simple_hash = find_same_simple_hash(i, cursor)
                if position_same_simple_hash != -1:
                    print("find same simple_hash", i, position_same_simple_hash)
                    resolve = \
                    cursor.execute("SELECT resolve FROM geetest WHERE id=?", (position_same_simple_hash,)).fetchall()[
                        0][0]
                    cursor.execute("UPDATE geetest SET resolve=? WHERE id=? ", (resolve, i))
                else:
                    no_word = "no"
                    cursor.execute("UPDATE geetest SET resolve=? WHERE id=? ", (no_word, i))


def update_array():
    global full_array
    global resolve_array
    global hash_array
    while True:
        try:
            with sqlite3.connect("database2.db") as db:
                cursor = db.cursor()
                hash_array.clear()
                resolve_array.clear()
                start_time = time.time()
                full_array = cursor.execute("SELECT simple_hash, resolve FROM geetest").fetchall()
                print(time.time() - start_time)
                for i in range(len(full_array)):
                    hash_array.append(full_array[i][0])
                    resolve_array.append(full_array[i][1])
                print("download db", time.time() - start_time)
            time.sleep(120)
        except:
            time.sleep(120)


class ClassName(object):
    """docstring for ClassName"""

    def __init__(self, arg):
        super(ClassName, self).__init__()
        self.arg = arg


def main():
    my_thread1 = threading.Thread(target=add_solves_to_db, args=(), daemon=True)
    my_thread1.start()

    update_array1 = threading.Thread(target=update_array, args=(), daemon=True)
    update_array1.start()

    count = 0
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("185.185.58.139", 443))
        server.listen(10)
        print("Working...")
        count_save = 0
        while (True):
            try:
                HDRS = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n"
                client_socket, address = server.accept()
                data = client_socket.recv(400000).decode("utf-8")
                print(data)
                answer = "error"
                body = "null"
                user_key = "0"

                try:
                    user_key = data.split("key=")[1].split("&")[0]
                    type_mes = data.split("type=")[1].split("&")[0]
                    body = data.split("body=")[1].split("&")[0]
                # size = data.split("size=")[1].split("&")[0]
                except:
                    user_key = "0"
                if (user_key != "qwerasdfzxcv10"):
                    answer = "KEY_IS_NOT_EXISTS"
                else:
                    if type_mes == "simplehash":
                        if (len(body) == 3000):
                            answer = get_resolve_by_simple_hash(body)
                            if (answer != "None" and answer != "-1"):
                                count += 1
                                print("gooooooooooooooooooood", count)
                        else:
                            answer = "bad image"
                    elif type_mes == "send":
                        size = data.split("size=")[1].split("&")[0]
                        if len(body) == int(size):
                            # print(len(body))
                            if int(size) > 100000:
                                count_save += 1
                                print("save", count_save)
                                with sqlite3.connect("database2.db") as db:
                                    cursor = db.cursor()

                                    save_image(body, cursor)
                            else:
                                answer = "None"
                        else:
                            answer = "bad image"
                    else:
                        answer = "bad image"
                # position = check_user_key(data)
                # if(int(position)!=-1):
                #	answer=get_result_from_array(position)
                # else:
                #	answer = "KEY_IS_NOT_EXISTS"
                # print("body = "+body[:80])

                content = answer.encode("utf-8")
                client_socket.send(HDRS.encode("utf-8") + content)
                client_socket.shutdown(socket.SHUT_WR)
            except Exception as e:
                print(e)
                client_socket.shutdown(socket.SHUT_WR)
    except KeyboardInterrupt:
        server.close()
        print("shutdown...")


# for i in range(1256):
#	with sqlite3.connect("database2.db") as db:
#		cursor = db.cursor()
#		name = cursor.execute("SELECT name FROM geetest WHERE id=?",(i,)).fetchall()[0][0]
#		default_name = "C:\\Users\\WinServer\\AppData\\Local\\Programs\\Python\\Python39\\Scripts\\server\\photo\\" 
#		#print(name)
#		try:
#			name=name.split("photo\\")[1]
#			name=default_name+name
#			#print(name)
#		except:
#			pass
#		cursor.execute("UPDATE geetest SET name=? WHERE id=? ",(name, i))
count_copy = 0
arr = []
full_array = []
resolve_array = []
hash_array = []
with sqlite3.connect("database2.db") as db:
    cursor = db.cursor()

    start_time = time.time()
    full_array = cursor.execute("SELECT simple_hash, resolve FROM geetest").fetchall()
    print(time.time() - start_time)
    for i in range(len(full_array)):
        hash_array.append(full_array[i][0])
        resolve_array.append(full_array[i][1])
    print("download db", time.time() - start_time)
for i in range(53, 385):
    arr.append([47, i])
    arr.append([130, i])
    arr.append([213, i])
    arr.append([296, i])
for i in range(6):
    arr.append([i, 55])
    arr.append([i, 384])
for i in range(217, 338):
    arr.append([i, 434])
main()
