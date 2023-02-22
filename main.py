# Import libraries

import PySimpleGUI as sg
from sort_sensor_quality import sort_sensor_quality, draw_figure
import seaborn as sns

sns.set(rc={'figure.figsize': (7, 7)})

# Setting theme and layouts
#_____________________________________
sg.theme('DarkGrey13')

layout0 = [[sg.Text('Выберите номер плотины')],
           [sg.Combo(['1-2', '3', '4', '5', 'Здание ГЭС - давление', 'Здание ГЭС - перемещение','Все плотины'],
                     size=(30, 5), key='-C-', enable_events=True)],
           [sg.Text('Введите путь к архиву')],
           [sg.InputText()],
           [sg.Submit()]]

layout1 = [[sg.Text('Плотина номер')],
           [],
           [sg.Text('Введите количество дней для расчета')],
           [sg.InputText()],
           [sg.Submit()]]

layout2 = [[sg.Text('Плотина номер')],
           [],
           [sg.Text('Подозрительные датчики')]
           ]

layout3 = []
#__________________________________________

# Window0
#__________________________________________
window0 = sg.Window('NNGES sensors', layout0)

while True:             # Event Loop
    event0, values0 = window0.read()
    print(event0, values0)
    if event0 == sg.WIN_CLOSED or event0 == 'Exit' or event0 == 'Submit':
        break
    if event0 == '-C-KEY DOWN':
        window0['-C-'].Widget.event_generate('<Down>')
window0.close()
#___________________________________________

# After closing Window0
#___________________________________________
dam_num = values0['-C-']
path = values0[0]
layout1[0].append(sg.Text(dam_num))
layout2[0].append(sg.Text(dam_num))
#___________________________________________

# Window1
#___________________________________________
window1 = sg.Window('NNGES sensors', layout1)

while True:             # Event Loop
    event1, values1 = window1.read()
    print(event1, values1)
    if event1 == sg.WIN_CLOSED or event1 == 'Exit' or event1 == 'Submit':
        break
window1.close()
#___________________________________________

# After closing Window1
#___________________________________________
num_days = int(values1[0])
num_points = num_days * 24 * 12

res, fig1, fig2 = sort_sensor_quality(num_points, dam_num, path)

for i in range(len(res.index)):
    layout2.append([sg.Text(res.index[i])])
layout2.append([sg.Canvas(key='-CANVAS1-'), sg.Canvas(key='-CANVAS2-')])
#___________________________________________

# Window2
#___________________________________________
window2 = sg.Window('NNGES sensors', layout2, finalize=True)
fig_canvas_agg = draw_figure(window2['-CANVAS1-'].TKCanvas, fig1)
fig_canvas_agg = draw_figure(window2['-CANVAS2-'].TKCanvas, fig2)

while True:             # Event Loop
    event2, values2 = window2.read()
    print(event2, values2)
    if event2 == sg.WIN_CLOSED or event2 == 'Exit' or event2 == 'Submit':
        break
window2.close()
#___________________________________________

