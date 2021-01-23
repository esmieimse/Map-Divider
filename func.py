import cv2
import numpy as np
import datetime


# 左辺を決める
def calcX1(mask, width, height):
  i = flag = 0
  ref_y = int(height/2)

  while True:
    if mask[ref_y, i] > 0: flag = 1
    elif (flag == 1):
      if mask[ref_y, i] == 0: 
        X1 = i
        break
    elif i > int(width/2): 
      X1 = 0
      break
    i = i+1

  return X1

# 上辺を決める
def calcY1(mask, width, height):
  i = flag = 0
  ref_x = int(width/3)

  while True:
    if mask[i, ref_x] > 0: flag = 1
    elif (flag == 1):
      if mask[i, ref_x] == 0: 
        Y1 = i
        break
    elif i > int(height/2): 
      Y1 = 0
      break
    i = i+1

  return Y1

def calcY1_cf(mask1, mask2, width, height):
  i = flag = 0
  ref_x = int(width/3)

  while True:
    if mask2[i, ref_x] > 0: 
      flag = 1
    elif mask1[i, ref_x] > 0 and flag == 1: 
      flag = 2
    elif flag == 2:
      if mask1[i, ref_x] == 0: 
        Y1 = i
        break
    elif i > int(height/2): 
      Y1 = 0
      break
    i = i+1

  return Y1

# 右辺を決める
def calcX2(mask, width, height):
  i = flag = 0
  ref_y = int(height/3)

  while True:
    j = (width-1) - i
    if mask[ref_y, j] > 0: flag = 1
    elif (flag == 1):
      if mask[ref_y, j] == 0: 
        X2 = j
        break
    elif i > int(width/2): 
      X2 = width - 1
      break
    i = i+1

  return X2


# cv2.imreadのパスを日本語可にする
def imread(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
  try:
    n = np.fromfile(filename, dtype)
    img = cv2.imdecode(n, flags)
    return img
  except Exception as e:
    print(e)
    return None

def adjust(img, alpha, beta):
  # 積和演算を行う。
  dst = alpha * img + beta
  # [0, 255] でクリップし、uint8 型にする。
  return np.clip(dst, 0, 255).astype(np.uint8)


# マップ部分のトリミングとサイズ調整
def createBase(filepath, series, alpha=1.0, beta=0.0):
  img = imread(filepath)

  height = img.shape[0]
  width = img.shape[1]

  hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

  #OpenCVのHSVはH:0-180 / S,V:0-255

  if series == "wwds":
    color_lo=np.array([25,100,150])
    color_hi=np.array([35,160,190])
    mask=cv2.inRange(hsv,color_lo,color_hi)

    X1 = calcX1(mask, width, height)
    Y1 = calcY1(mask, width, height)
    X2 = calcX2(mask, width, height)

  elif series == "wwvc":
    color_lo=np.array([27,150,90])
    color_hi=np.array([38,255,140])
    mask=cv2.inRange(hsv,color_lo,color_hi)
    
    X1 = calcX1(mask, width, height)
    Y1 = calcY1(mask, width, height)
    X2 = calcX2(mask, width, height)

  elif series == "cf":
    color_lo_1=np.array([60,60,150])
    color_hi_1=np.array([90,160,250])
    color_lo_2=np.array([80,220,30])
    color_hi_2=np.array([95,255,95])

    mask1=cv2.inRange(hsv,color_lo_1,color_hi_1)
    mask2=cv2.inRange(hsv,color_lo_2,color_hi_2)

    X1 = calcX1(mask1, width, height)
    Y1 = calcY1_cf(mask1, mask2, width, height)
    X2 = calcX2(mask1, width, height)

  Y2 = Y1 + X2 - X1

  img_crop = img[Y1: Y2+1, X1 : X2+1]

  if series in {"wwds", "wwvc"}:
    img_resize = cv2.resize(img_crop, (256,256), interpolation=cv2.INTER_NEAREST)
  elif series in {"cf"}:
    img_resize = cv2.resize(img_crop, (280,280), interpolation=cv2.INTER_NEAREST)

  img_adjust = adjust(img_resize, alpha, beta)

  return img_adjust


# 市松模様
def addFill(img, series):
  depth = 50
  
  if series in {"wwds", "wwvc"}:
    black = np.full((64, 64, 3), np.uint8(depth))
    white = np.full((64, 64, 3), np.uint8(0))

    f1 = np.concatenate([black, white, black, white], 1)
    f2 = np.concatenate([white, black, white, black], 1)
    f  = np.concatenate([f1, f2, f1, f2], 0)

  elif series in {"cf"}:
    black = np.full((56, 56, 3), np.uint8(depth))
    white = np.full((56, 56, 3), np.uint8(0))

    f1 = np.concatenate([black, white, black, white, black], 1)
    f2 = np.concatenate([white, black, white, black, white], 1)
    f  = np.concatenate([f1, f2, f1, f2, f1], 0)

  img_fill = cv2.subtract(img, f) 

  return img_fill


# 格子
def addGrid(img, series):
  img_grid = img
  
  if series in {"wwds", "wwvc"}:
    for c in range(3):
      for x in range(63, 256, 64):
        for y in range(256):
          img_grid[x, y, c] = 255
          img_grid[y, x, c] = 255
  elif series in {"cf"}:
    for c in range(3):
      for x in range(55, 280, 56):
        for y in range(280):
          img_grid[x, y, c] = 255
          img_grid[y, x, c] = 255

  return img_grid


# マス目
def addSquare(img, series):
  img_grid = img

  if series in {"wwds", "wwvc"}:
    for c in range(3):
      for x in range(7, 256, 8):
        for y in range(256):
          if (img_grid[x, y, c] * 1.2) > 255:
            img_grid[x, y, c] = 255
          else:
            img_grid[x, y, c] = img_grid[x, y, c] * 1.2
            
          if (img_grid[y, x, c] * 1.2) > 255:
            img_grid[y, x, c] = 255
          else:
            img_grid[y, x, c] = img_grid[y, x, c] * 1.2

  elif series in {"cf"}:
    for c in range(3):
      for x in range(6, 280, 7):
        for y in range(280):
          if (img_grid[x, y, c] * 1.2) > 255:
            img_grid[x, y, c] = 255
          else:
            img_grid[x, y, c] = img_grid[x, y, c] * 1.2
            
          if (img_grid[y, x, c] * 1.2) > 255:
            img_grid[y, x, c] = 255
          else:
            img_grid[y, x, c] = img_grid[y, x, c] * 1.2
  
  return img_grid


##画像保存
def saveImage(img, savepath):
  now = datetime.datetime.now()
  filename = savepath + '/' + now.strftime('%Y-%m-%d %H%M%S') + '.png'
  cv2.imwrite(filename, img)
