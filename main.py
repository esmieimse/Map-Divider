import func
import PySimpleGUI as sg
import glob
import os
import configparser
import cv2
import sys
import win32api

def resource_path(relative_path):
  if hasattr(sys, '_MEIPASS'):
    basepath = win32api.GetLongPathName(sys._MEIPASS)
    return os.path.join(basepath, relative_path)
  return os.path.join(os.path.abspath("."), relative_path)


config = configparser.ConfigParser()
config.read('MapDivider.config', encoding='utf-8')


sg.theme('SystemDefault')

seriesTitle1 = sg.Combo(('ACWW (DS)', 'ACWW (WiiU)', 'ACCF'), default_value='シリーズを選択', size=(15, 1), key='-SERIES1-')
seriesTitle2 = sg.Combo(('ACWW (DS)', 'ACWW (WiiU)', 'ACCF'), default_value='シリーズを選択', size=(15, 1), key='-SERIES2-')
errorMessage1s = sg.Text(size=(15, 1), text_color='red', key='-ERROR1s-')
errorMessage1f = sg.Text(size=(15, 1), text_color='red', key='-ERROR1f-')
errorMessage2s = sg.Text(size=(15, 1), text_color='red', key='-ERROR2s-')
errorMessage2f = sg.Text(size=(15, 1), text_color='red', key='-ERROR2f-')

checkFill1 = sg.Checkbox('色分け', size=(9,1), default=config['OVERLAY']['Fill'], key='-FILL1-')
checkFill2 = sg.Checkbox('色分け', size=(9,1), default=config['OVERLAY']['Fill'], key='-FILL2-')
checkGrid1 = sg.Checkbox('グリッド', size=(9,1), default=config['OVERLAY']['Grid'], key='-GRID1-')
checkGrid2 = sg.Checkbox('グリッド', size=(9,1), default=config['OVERLAY']['Grid'], key='-GRID2-')
checkSquare1 = sg.Checkbox('マス目(2×2)', size=(9,1), default=config['OVERLAY']['Square'], key='-SQUARE1-')
checkSquare2 = sg.Checkbox('マス目(2×2)', size=(9,1), default=config['OVERLAY']['Square'], key='-SQUARE2-')

checkCol1 = [[checkSquare1], [checkGrid1], [checkFill1], 
             [sg.Submit('実行', size=(10,1), key='-SUBMIT1-')], [sg.Submit('保存', size=(10,1), disabled = True, key='-SAVE1-')]]
checkCol2 = [[checkSquare2], [checkGrid2], [checkFill2], 
             [sg.Submit('実行', size=(10,1), key='-SUBMIT2-')], [sg.Submit('保存', size=(10,1), disabled = True, key='-SAVE2-')]]

Image1 = sg.Image(size=(256,256), pad=((30,10),10), background_color='#d5d8d8', key='-IMAGE1-')
Image2 = sg.Image(size=(256,256), pad=((30,10),10), background_color='#d5d8d8', key='-IMAGE2-')

Slider1a = sg.Slider(range=(1, 1.5), size=(28, 12), default_value=config['DISPLAY']['Alpha'], resolution=0.05, pad=(0,0), 
                     orientation='h', disable_number_display=True, enable_events=True, disabled = True, key='-SLIDER1a-')
Slider1b = sg.Slider(range=(-30, 30), size=(28, 12), default_value=config['DISPLAY']['Beta'], resolution=6, pad=(0,0), 
                     orientation='h', disable_number_display=True, enable_events=True, disabled = True, key='-SLIDER1b-')
Slider2a = sg.Slider(range=(1, 1.5), size=(28, 12), default_value=config['DISPLAY']['Alpha'], resolution=0.05, pad=(0,0), 
                     orientation='h', disable_number_display=True, enable_events=True, disabled = True, key='-SLIDER2a-')
Slider2b = sg.Slider(range=(-30, 30), size=(28, 12), default_value=config['DISPLAY']['Beta'], resolution=6, pad=(0,0), 
                     orientation='h', disable_number_display=True, enable_events=True, disabled = True, key='-SLIDER2b-')

Slider1 = [[sg.Text('明るさ', size=(6,1), pad=((4,3),2)), Slider1b], [sg.Text('ｺﾝﾄﾗｽﾄ', size=(6,1), pad=((4,3),2)), Slider1a]]
Reset1 = sg.Button('リセット', pad=((6,11),0), button_color=('black','#dddddd'), enable_events=True, key='-RESET1-')
Settings1 = sg.Frame('表示設定',[[sg.Col(Slider1), Reset1]] ,title_color='#334444', pad=(5,10))

Slider2 = [[sg.Text('明るさ', size=(6,1), pad=((4,3),2)), Slider2b], [sg.Text('ｺﾝﾄﾗｽﾄ', size=(6,1), pad=((4,3),2)), Slider2a]]
Reset2 = sg.Button('リセット', pad=((6,11),0), button_color=('black','#dddddd'), enable_events=True, key='-RESET2-')
Settings2 = sg.Frame('表示設定',[[sg.Col(Slider2), Reset2]] ,title_color='#334444', pad=(5,10))


layoutTab1 = [
  [seriesTitle1, errorMessage1s],
  [sg.Text('フォルダを選択：', pad=((5,0),(5,0))), errorMessage1f],
  [sg.InputText(size=(45,1), default_text=config['GENERAL']['FolderPath'], key='-FOLDERPATH-'), sg.FolderBrowse()], 
  [sg.Text('_' * 58, text_color='#aaaaaa')],
  [sg.Frame('', [[Image1,sg.Col(checkCol1, element_justification='center')]], background_color='#d5d8d8', element_justification = "center", pad=((5,5),(5,0)))],
  [Settings1]
]

layoutTab2 = [
  [seriesTitle2, errorMessage2s],
  [sg.Text('画像ファイルを選択：', pad=((5,0),(5,0))), errorMessage2f],
  [sg.InputText(size=(45,1), key='-FILEPATH-'), sg.FileBrowse(file_types=(('Image Files', ['*.png', '*.jpg', '*.jpeg', '*.bmp']),))], 
  [sg.Text('_' * 58, text_color='#aaaaaa')],
  [sg.Frame('', [[Image2,sg.Col(checkCol2, element_justification='center')]], background_color='#d5d8d8', element_justification = "center", pad=((5,5),(5,0)))],
  [Settings2]
]

layout = [
  [sg.TabGroup([[sg.Tab('指定フォルダから生成', layoutTab1), sg.Tab('画像から生成', layoutTab2)]])]
]


window = sg.Window('マップ区画表示ツール', layout, icon=resource_path('app.ico'), titlebar_icon='app.ico')


flag1 = False
flag2 = False


while True:
  event, values = window.read()

  if event is None:
    if flag1 == True:
      alpha = str(alpha)
      beta  = str(beta)
      config.set('DISPLAY', 'alpha', alpha)
      config.set('DISPLAY', 'beta', beta)
    elif flag2 == True:
      alpha = str(alpha)
      beta  = str(beta)
      config.set('DISPLAY', 'alpha', alpha)
      config.set('DISPLAY', 'beta', beta)

    with open('MapDivider.config', 'w') as configfile:
      config.write(configfile)
      
    break


  ##実行ボタン押したときの処理(Tab1)
  if event == '-SUBMIT1-':
    if values['-SERIES1-'] == 'シリーズを選択':
      window['-ERROR1s-'].update('選択してください')

    elif values['-FOLDERPATH-'] == '':
      window['-ERROR1s-'].update('')
      window['-ERROR1f-'].update('選択してください')
      
    else:
      window['-ERROR1s-'].update('')
      window['-ERROR1f-'].update('')
      if values['-SERIES1-'] == 'ACWW (DS)':
        series = 'wwds'
      elif values['-SERIES1-'] == 'ACWW (WiiU)':
        series = 'wwvc'
      elif values['-SERIES1-'] == 'ACCF':
        series = 'cf'
  
      config.set('GENERAL', 'FolderPath', values['-FOLDERPATH-'])
      files = glob.glob(values['-FOLDERPATH-'] + '/*')
      files = sorted(files, key=lambda f: os.stat(f).st_ctime, reverse=True)


      alpha = values['-SLIDER1a-']
      beta  = values['-SLIDER1b-']
      img = func.createBase(files[0], series, alpha, beta)

      if values['-SQUARE1-'] == True:
        img = func.addSquare(img, series)
        config.set('OVERLAY', 'Square', '1')
      else:
        config.set('OVERLAY', 'Square', '0')

      if values['-FILL1-'] == True:
        img = func.addFill(img, series)
        config.set('OVERLAY', 'Fill', '1')
      else:
        config.set('OVERLAY', 'Fill', '0')

      if values['-GRID1-'] == True:
        img = func.addGrid(img, series)
        config.set('OVERLAY', 'Grid', '1')
      else:
        config.set('OVERLAY', 'Grid', '0')


      img_encode = cv2.imencode('.png', img)[1].tobytes()
      window['-IMAGE1-'].update(data=img_encode)
      window['-SLIDER1a-'].update(disabled = False)
      window['-SLIDER1b-'].update(disabled = False)
      window['-SAVE1-'].update(disabled = False)


  ##実行ボタン押したときの処理(Tab2)
  if event == '-SUBMIT2-':
    if values['-SERIES2-'] == 'シリーズを選択':
      window['-ERROR2s-'].update('選択してください')

    elif values['-FILEPATH-'] == '':
      window['-ERROR2s-'].update('')
      window['-ERROR2f-'].update('選択してください')
      
    else:
      window['-ERROR2s-'].update('')
      window['-ERROR2f-'].update('')
      if values['-SERIES2-'] == 'ACWW (DS)':
        series = 'wwds'
      elif values['-SERIES2-'] == 'ACWW (WiiU)':
        series = 'wwvc'
      elif values['-SERIES2-'] == 'ACCF':
        series = 'cf'

      alpha = values['-SLIDER2a-']
      beta  = values['-SLIDER2b-']
      img = func.createBase(values['-FILEPATH-'], series, alpha, beta)

      if values['-SQUARE2-'] == True:
        img = func.addSquare(img, series)
        config.set('OVERLAY', 'Square', '1')
      else:
        config.set('OVERLAY', 'Square', '0')

      if values['-FILL2-'] == True:
        img = func.addFill(img, series)
        config.set('OVERLAY', 'Fill', '1')
      else:
        config.set('OVERLAY', 'Fill', '0')

      if values['-GRID2-'] == True:
        img = func.addGrid(img, series)
        config.set('OVERLAY', 'Grid', '1')
      else:
        config.set('OVERLAY', 'Grid', '0')
      
      img_encode = cv2.imencode('.png', img)[1].tobytes() 
      window['-IMAGE2-'].update(data=img_encode)
      window['-SLIDER2a-'].update(disabled = False)
      window['-SLIDER2b-'].update(disabled = False) 
      window['-SAVE2-'].update(disabled = False)

  
  ##スライダー動かしたときの処理(Tab1)
  if event in ['-SLIDER1a-', '-SLIDER1b-']:
    flag1 = True
    alpha = values['-SLIDER1a-']
    beta  = values['-SLIDER1b-']
    img = func.createBase(files[0], series, alpha, beta)

    if values['-SQUARE1-'] == True:
      img = func.addSquare(img, series)
    if values['-FILL1-'] == True:
      img = func.addFill(img, series)
    if values['-GRID1-'] == True:
      img = func.addGrid(img, series)
    
    img_encode = cv2.imencode('.png', img)[1].tobytes()
    window['-IMAGE1-'].update(data=img_encode)


  ##スライダー動かしたときの処理(Tab2)
  if event in ['-SLIDER2a-', '-SLIDER2b-']:
    flag2 = True
    alpha = values['-SLIDER2a-']
    beta  = values['-SLIDER2b-']
    img = func.createBase(values['-FILEPATH-'], series, alpha, beta)

    if values['-SQUARE2-'] == True:
      img = func.addSquare(img, series)
    if values['-FILL2-'] == True:
      img = func.addFill(img, series)
    if values['-GRID2-'] == True:
      img = func.addGrid(img, series)
    
    img_encode = cv2.imencode('.png', img)[1].tobytes()
    window['-IMAGE2-'].update(data=img_encode)


  ##スライダーリセット処理(Tab1)
  if event == '-RESET1-':
    window.FindElement('-SLIDER1a-').Update(1.0)
    window.FindElement('-SLIDER1b-').Update(0.0)

    img = func.createBase(files[0], series)

    if values['-SQUARE1-'] == True:
      img = func.addSquare(img, series)
    if values['-FILL1-'] == True:
      img = func.addFill(img, series)
    if values['-GRID1-'] == True:
      img = func.addGrid(img, series)
    
    img_encode = cv2.imencode('.png', img)[1].tobytes()
    window['-IMAGE1-'].update(data=img_encode)


  ##スライダーリセット処理(Tab2)
  if event == '-RESET2-':
    window.FindElement('-SLIDER2a-').Update(1.0)
    window.FindElement('-SLIDER2b-').Update(0.0)
    
    img = func.createBase(values['-FILEPATH-'], series)

    if values['-SQUARE2-'] == True:
      img = func.addSquare(img, series)
    if values['-FILL2-'] == True:
      img = func.addFill(img, series)
    if values['-GRID2-'] == True:
      img = func.addGrid(img, series)
    
    img_encode = cv2.imencode('.png', img)[1].tobytes()
    window['-IMAGE2-'].update(data=img_encode)
  

  ##保存ボタン押したときの処理(Tab1)
  if event == '-SAVE1-':
    savepath = config['GENERAL']['SavePath']

    if savepath == '':
      value = sg.popup_get_folder('保存するフォルダを指定してください')
      config.set('GENERAL', 'SavePath', value)

      with open('MapDivider.config', 'w') as configfile:
        config.write(configfile)
      
      func.saveImage(img, value)

    else: 
      func.saveImage(img, savepath)

    
  ##保存ボタン押したときの処理(Tab2)
  if event == '-SAVE2-':
    savepath = config['GENERAL']['SavePath']

    if savepath == '':
      value = sg.popup_get_folder('保存するフォルダを指定してください')
      config.set('GENERAL', 'SavePath', value)

      with open('MapDivider.config', 'w') as configfile:
        config.write(configfile)
      
      func.saveImage(img, value)

    else: 
      func.saveImage(img, savepath)

window.close()
print(values)