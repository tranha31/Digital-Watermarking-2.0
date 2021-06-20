from __future__ import division
from math import sqrt, cos, pi, floor
import numpy as np
from PIL import Image as im
from mysql.connector import MySQLConnection, Error

K = 5
image = im.open("socute.jpg")
ycbcr = image.convert('YCbCr')

Y = 0
Cb = 1
Cr = 2

YCbCr=list(ycbcr.getdata()) # flat list of tuples
# reshape
imYCbCr = np.reshape(YCbCr, (image.size[1], image.size[0], 3))
# Convert 32-bit elements to 8-bit
imYCbCr = imYCbCr.astype(np.uint8)

# now, display the 3 channels
#im.fromarray(imYCbCr[:,:,Y], "L").show()
#im.fromarray(imYCbCr[:,:,Cb], "L").show()
#im.fromarray(imYCbCr[:,:,Cr], "L").show()

width, height = imYCbCr[:,:,Y].shape
    
#DCT = np.zeros((8,8))
A1 = np.zeros((8,8))
sign = "hellooooooooooooooooooooo"
s = ""

def hexToBinary(sign):
    a = ''.join(format(ord(x), 'b') for x in sign)
    return a

s = hexToBinary(sign)

def connect():
    db_config = {
        'host' : 'localhost',
        'database' : 'attt',
        'user' : 'root',
        'password' : ''
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
        return 1/sqrt(2)
    else:
        return 1
    
def dct(A):
    DCT = np.zeros((8,8))
    for u in range(8):
        for v in range(8):
            sum = 0
            for k in range(8):
                for l in range(8):
                    sum = sum + A[k][l]*cos(pi*u*(2*k+1)/16)*cos(pi*v*(2*l+1)/16)
            sum = sum *C(u)*C(v)/4
            DCT[u][v] = sum
    return DCT
            

def idct(DCT):
    A1 = np.zeros((8,8))
    for k in range(8):
        for l in range(8):
            sum = 0
            for u in range(8):
                for v in range(8):
                    sum = sum + cos(pi*u*(2*k+1)/16)*cos(pi*v*(2*l+1)/16)*DCT[u][v]*C(u)*C(v)/4
            A1[k][l] = int(round(sum))
    return A1
                    
def dctYchanel(Y):
    ldct = []
    for i in range(0, 97, 8):
        for j in range(0, 97, 8):
            MT = np.zeros((8,8))
            for k in range(i, i+8):
                for l in range(j, j+8):
                    MT[k%8][l%8] = Y[k][l]
            D = dct(MT)
            ldct.append(D)
    m = 104
    for n in range(0,41,8):
        MT = np.zeros((8,8))
        for k in range(m, m+8):
            for l in range(n, n+8):
                MT[k%8][l%8] = Y[k][l]
        D = dct(MT)
        ldct.append(D)
                
    return ldct
            
def idctYchanel(Y, L):
    tmp = 0
    for i in range(0, 97, 8):
        for j in range(0, 97, 8):
            MT = idct(L[tmp])
            for k in range(i, i+8):
                for l in range(j, j+8):
                    Y[k][l] = MT[k%8][l%8]
            tmp = tmp + 1
    m = 104
    for n in range(0,41,8):
        MT = idct(L[tmp])
        for k in range(m, m+8):
            for l in range(n, n+8):
                Y[k][l] = MT[k%8][l%8]
        tmp = tmp + 1
            
    
#always get point (5,2) and (4,3)
def watermarking(L, sign):
    tmp = 0
    print(sign)
    for i in range(len(L)):
        D = L[i]
        if sign[tmp] == '0' and D[5][2] < D[4][3]:
            D[5][2], D[4][3] = D[4][3], D[5][2]
        if sign[tmp] == '1' and D[5][2] >= D[4][3]:
            D[5][2], D[4][3] = D[4][3], D[5][2]
        if (D[5][2] > D[4][3]) and (D[5][2] - D[4][3]) < K:
            D[5][2] = D[5][2] + K/2
            D[4][3] = D[4][3] - K/2
        if (D[5][2] <= D[4][3]) and (D[4][3] - D[5][2]) < K:
            D[5][2] = D[5][2] - K/2
            D[4][3] = D[4][3] + K/2
        L[i] = D
      
        tmp = tmp + 1

def pickWatermarking(L):
    sign1 = ""
    for i in range(len(L)):
        D = L[i]
        x1 = D[5][2]
        x2 = D[4][3]
        if(x1 > x2):
            sign1 += "0"
        else:
            sign1 += "1"
    digit = []
    sign2 = ""
    for i in range(len(sign1)//7):
        digit.append(int(sign1[i*7:i*7+7],2))
   
    for i in range(len(digit)):
        if (digit[i]>=48 and digit[i]<=57):
            sign2 += chr(digit[i])
        elif (digit[i]>=65 and digit[i]<=90):
            sign2 += chr(digit[i])
        elif (digit[i]>=97 and digit[i]<=122):
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
        if(x1 > x2):
            sign1 += "0"
        else:
            sign1 += "1"
    digit = []
    sign2 = ""
    for i in range(len(sign1)//7):
        digit.append(int(sign1[i*7:i*7+7],2))
   
    for i in range(len(digit)):
        if (digit[i]>=48 and digit[i]<=57):
            sign2 += chr(digit[i])
        elif (digit[i]>=65 and digit[i]<=90):
            sign2 += chr(digit[i])
        elif (digit[i]>=97 and digit[i]<=122):
            sign2 += chr(digit[i])
        else:
            return "The picture dosen't have sign"
    conn = connect()
    cursor = conn.cursor()
    sql = "select * from sign where s = '" + sign2 + "'"
    cursor.execute(sql)
    row = cursor.fetchone()
    if row is not None:
        return "The picture dosen't have sign"
    else:
        return sign2
         
#if exist sign, notified to user in front-end
def checkWM(D):
    sign1 = ""
    for i in range(len(D)):
        x1 = D[i][5][2]
        x2 = D[i][4][3]
        if (x1>x2):
            sign1 += "0"
        else:
            sign1 += "1"
    digit = []
    sign2 = ""
    for i in range(len(sign1)//7):
        digit.append(int(sign1[i*7:i*7+7],2))
   
    for i in range(len(digit)):
        
        if (digit[i]>=48 and digit[i]<=57):
            sign2 += chr(digit[i])
        elif (digit[i]>=65 and digit[i]<=90):
            sign2 += chr(digit[i])
        elif (digit[i]>=97 and digit[i]<=122):
            sign2 += chr(digit[i])
        else:
            return True
    conn = connect()
    cursor = conn.cursor()
    sql = "select * from sign where s = '" + sign2 + "'"
    cursor.execute(sql)
    row = cursor.fetchone()
    if row is not None:
        return False
    else:
        return True
    
        
L = dctYchanel(imYCbCr[:,:,Y])

if(checkWM(L)):
    watermarking(L, s)

test = pickWatermarking(L)
print(test)

idctYchanel(imYCbCr[:,:,Y], L)

#im.fromarray(imYCbCr[:,:,Y], "L").show()
            
               
            
        
