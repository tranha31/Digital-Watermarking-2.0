from __future__ import division
from math import sqrt, cos, pi, floor
import numpy as np
from PIL import Image as im
from mysql.connector import MySQLConnection, Error
import io
import base64

K = 5
Y = 0
Cb = 1
Cr = 2


def inputImage(base64_string):
    imgdata = base64.b64decode(base64_string)
    image = im.open(io.BytesIO(imgdata))
    ycbcr = image.convert('YCbCr')

    YCbCr = list(ycbcr.getdata())  # flat list of tuples
    # reshape
    imYCbCr = np.reshape(YCbCr, (image.size[1], image.size[0], 3))
    # Convert 32-bit elements to 8-bit
    imYCbCr = imYCbCr.astype(np.uint8)
    return imYCbCr


def hexToBinary(sign):
    a = ''.join(format(ord(x), 'b') for x in sign)
    return a


def connect():
    db_config = {
        'host': '127.0.0.1',
        'database': 'attt',
        'user': 'root',
        'password': '123456'
    }
    conn = None
    try:
        conn = MySQLConnection(**db_config)

        if conn.is_connected():
            return conn

    except Error as error:
        print(error)

    return conn


def C(u):
    if u == 0:
        return 1 / sqrt(2)
    else:
        return 1


def dct(A):
    DCT = np.zeros((8, 8))
    for u in range(8):
        for v in range(8):
            sum = 0
            for k in range(8):
                for l in range(8):
                    sum = sum + A[k][l] * cos(pi * u * (2 * k + 1) / 16) * cos(pi * v * (2 * l + 1) / 16)
            sum = sum * C(u) * C(v) / 4
            DCT[u][v] = sum
    return DCT


def idct(DCT):
    A1 = np.zeros((8, 8))
    for k in range(8):
        for l in range(8):
            sum = 0
            for u in range(8):
                for v in range(8):
                    sum = sum + cos(pi * u * (2 * k + 1) / 16) * cos(pi * v * (2 * l + 1) / 16) * DCT[u][v] * C(u) * C(
                        v) / 4
            A1[k][l] = int(round(sum))
    return A1


def dctYchanel(Y):
    ldct = []
    for i in range(0, 97, 8):
        for j in range(0, 97, 8):
            MT = np.zeros((8, 8))
            for k in range(i, i + 8):
                for l in range(j, j + 8):
                    MT[k % 8][l % 8] = Y[k][l]
            D = dct(MT)
            ldct.append(D)
    m = 104
    for n in range(0, 41, 8):
        MT = np.zeros((8, 8))
        for k in range(m, m + 8):
            for l in range(n, n + 8):
                MT[k % 8][l % 8] = Y[k][l]
        D = dct(MT)
        ldct.append(D)

    return ldct


def idctYchanel(Y, L):
    tmp = 0
    for i in range(0, 97, 8):
        for j in range(0, 97, 8):
            MT = idct(L[tmp])
            for k in range(i, i + 8):
                for l in range(j, j + 8):
                    Y[k][l] = MT[k % 8][l % 8]
            tmp = tmp + 1
    m = 104
    for n in range(0, 41, 8):
        MT = idct(L[tmp])
        for k in range(m, m + 8):
            for l in range(n, n + 8):
                Y[k][l] = MT[k % 8][l % 8]
        tmp = tmp + 1


# always get point (5,2) and (4,3)
def watermarking(L, sign):
    tmp = 0
    # print(sign)
    for i in range(len(L)):
        D = L[i]
        if sign[tmp] == '0' and D[5][2] < D[4][3]:
            D[5][2], D[4][3] = D[4][3], D[5][2]
        if sign[tmp] == '1' and D[5][2] >= D[4][3]:
            D[5][2], D[4][3] = D[4][3], D[5][2]
        if (D[5][2] > D[4][3]) and (D[5][2] - D[4][3]) < K:
            D[5][2] = D[5][2] + K / 2
            D[4][3] = D[4][3] - K / 2
        if (D[5][2] <= D[4][3]) and (D[4][3] - D[5][2]) < K:
            D[5][2] = D[5][2] - K / 2
            D[4][3] = D[4][3] + K / 2
        L[i] = D

        tmp = tmp + 1


def pickWatermarking(L):
    sign1 = ""
    for i in range(len(L)):
        D = L[i]
        x1 = D[5][2]
        x2 = D[4][3]
        if (x1 > x2):
            sign1 += "0"
        else:
            sign1 += "1"
    digit = []
    sign2 = ""
    for i in range(len(sign1) // 7):
        digit.append(int(sign1[i * 7:i * 7 + 7], 2))

    for i in range(len(digit)):
        if (digit[i] >= 48 and digit[i] <= 57):
            sign2 += chr(digit[i])
        elif (digit[i] >= 65 and digit[i] <= 90):
            sign2 += chr(digit[i])
        elif (digit[i] >= 97 and digit[i] <= 122):
            sign2 += chr(digit[i])
        else:
            return "The picture dosen't have sign"

    return sign2


def checkExistWatermarking(L):
    sign1 = ""
    for i in range(len(L)):
        D = L[i]
        x1 = D[5][2]
        x2 = D[4][3]
        if (x1 > x2):
            sign1 += "0"
        else:
            sign1 += "1"
    digit = []
    sign2 = ""
    for i in range(len(sign1) // 7):
        digit.append(int(sign1[i * 7:i * 7 + 7], 2))

    for i in range(len(digit)):
        if (digit[i] >= 48 and digit[i] <= 57):
            sign2 += chr(digit[i])
        elif (digit[i] >= 65 and digit[i] <= 90):
            sign2 += chr(digit[i])
        elif (digit[i] >= 97 and digit[i] <= 122):
            sign2 += chr(digit[i])
        else:
            return "The picture dosen't have sign"
    conn = connect()
    cursor = conn.cursor()
    sql = "select * from users where sign = '" + sign2 + "'"
    cursor.execute(sql)
    row = cursor.fetchone()
    if row is None:
        return "The picture dosen't have sign"
    else:
        return sign2


# if exist sign, notified to user in front-end
def checkWM(D):
    sign1 = ""
    for i in range(len(D)):
        x1 = D[i][5][2]
        x2 = D[i][4][3]
        if (x1 > x2):
            sign1 += "0"
        else:
            sign1 += "1"
    digit = []
    sign2 = ""
    for i in range(len(sign1) // 7):
        digit.append(int(sign1[i * 7:i * 7 + 7], 2))

    for i in range(len(digit)):

        if (digit[i] >= 48 and digit[i] <= 57):
            sign2 += chr(digit[i])
        elif (digit[i] >= 65 and digit[i] <= 90):
            sign2 += chr(digit[i])
        elif (digit[i] >= 97 and digit[i] <= 122):
            sign2 += chr(digit[i])
        else:
            return True
    conn = connect()
    cursor = conn.cursor()
    sql = "select * from users where sign = '" + sign2 + "'"
    cursor.execute(sql)
    row = cursor.fetchone()
    if row is not None:
        return False
    else:
        return True


# x is imYCbCr[:,:,Y], y is imYCbCr[:,:,Cb], z is imYCbCr[:,:,Cr]
def outImage(x, y, z):
    out_img_y = im.fromarray(x, "L")
    out_img_cb = im.fromarray(y, "L")
    out_img_cr = im.fromarray(z, "L")
    out_img = im.merge('YCbCr', [out_img_y, out_img_cb, out_img_cr]).convert('RGB')

    buffer = io.BytesIO()
    out_img.save(buffer, format="PNG")
    buffer.seek(0)
    myimage = buffer.getvalue()
    t = base64.b64encode(myimage)
    t = str(t)
    t = t[2:]
    t = t[:-1]
    r = "data:image/png;base64," + t
    return r
    # return "data:image/png;base64," + base64.b64encode(myimage)


# Embedding watermarking
def embedWatermarking(base64_string, sign):
    imYCbCr = inputImage(base64_string)
    s = hexToBinary(sign)
    L = dctYchanel(imYCbCr[:, :, Y])
    if (checkWM(L)):
        watermarking(L, s)
        idctYchanel(imYCbCr[:, :, Y], L)
        # im.fromarray(imYCbCr[:,:,Y], "L").show()
        result = outImage(imYCbCr[:, :, Y], imYCbCr[:, :, Cb], imYCbCr[:, :, Cr])
        return result
    else:
        return "Image was had sign"


# Check image has watermarking. Result is a text
def checkImageWM(base64_string):
    imYCbCr = inputImage(base64_string)
    L = dctYchanel(imYCbCr[:, :, Y])
    result = checkExistWatermarking(L)
    return result



