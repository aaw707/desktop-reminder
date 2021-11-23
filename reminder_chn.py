import PySimpleGUI as sg
from win10toast import ToastNotifier
from psgtray import SystemTray
import datetime as dt
import sys 
import os

#os.chdir(sys._MEIPASS)
# parameters
font = "微软雅黑"
font_size = 12
background_color = "#FFEEED"
button_color = "#FFC2C0"
text_color = "#4A154B"

# window layout
layout = [   
            # Remind me to...
            [sg.Text('提醒事项：', font=(font, font_size), key="_TEXT1_", text_color = text_color, background_color = background_color)],
            # input the task
            [sg.Input('', size = (37, 1), do_not_clear=True, key='_CONTENT_', font = (font, font_size - 2), text_color = text_color)],
            # At XX:XX (time, hour:min  e.g. 9:00)
            [sg.Text('提醒时间', size=(8, 1), font=(font, font_size), key="_TEXT2_", text_color = text_color, background_color = background_color),
                sg.Input(00, key='_TARGET_HR_',  size=(3, 1), font = (font, font_size - 2), text_color = text_color),
                sg.Text('点', size=(3, 1), font=(font, font_size), key="_TEXT3_", text_color = text_color, background_color = background_color),
                sg.Input(00, key='_TARGET_MIN_',  size=(3, 1), font = (font, font_size - 2), text_color = text_color),
                sg.Text('分', size=(3, 1), font=(font, font_size), key="_FORMATER_", text_color = text_color, background_color = background_color)],
            # Or in XX hr XX min
            [sg.Text('或在', size=(4, 1), font=(font, font_size), key="_TEXT4_", text_color = text_color, background_color = background_color),
                sg.Input(00, key='_LENGTH_HR_',  size=(3, 1), font = (font, font_size - 2), text_color = text_color),
                sg.Text('小时', size=(4, 1), font=(font, font_size), key="_TEXT5_", text_color = text_color, background_color = background_color),
                sg.Input(00, key='_LENGTH_MIN_',  size=(3, 1), font = (font, font_size - 2), text_color = text_color),
                sg.Text('分钟后', size=(6, 1), font=(font, font_size), key="_TEXT6_", text_color = text_color, background_color = background_color),
                sg.Button('确认', font=(font, font_size), focus=False, button_color = (text_color, button_color))],
            # upcoming reminders + hide button + exit button
            [sg.Text('已设置提醒：', size = (18, 1), font=(font, font_size), key="_TEXT7_", text_color = text_color, background_color = background_color),
                sg.Button('隐藏', focus=False, font=(font, font_size), button_color = (text_color, button_color)),
                sg.Button('退出', font=(font, font_size), button_color = (text_color, button_color))],
            # print a list of upcoming reminders
            [sg.Text('', font = (font, font_size), key = "_UPCOMING_REMINDERS_", text_color = text_color, background_color = background_color)]]

# initiate the window
window = sg.Window('提醒', enable_close_attempted_event=True, background_color = background_color).Layout(layout)

# minimized system tray
menu = ['', ['显示窗口', '退出']]
tray = SystemTray(menu, single_click_events=False, window=window, tooltip='提醒', icon='icon.ico')

# initiate the toaster
toaster = ToastNotifier()

active_reminders = {}


# Event Loop
while True:
    event, values = window.Read(timeout = 1000)

    # use the System Tray's event as if was from the window
    if event == tray.key:
        event = values[event]       # use the System Tray's event as if was from the window

    # exit the app 
    if event in ('退出', sg.WIN_CLOSED):
        break

    # show window
    if event in ('显示窗口', sg.EVENT_SYSTEM_TRAY_ICON_DOUBLE_CLICKED):
        window.un_hide()
        window.bring_to_front()
    
    # hide the window to task bar
    elif event in ('隐藏', sg.WIN_CLOSE_ATTEMPTED_EVENT):
        window.hide()
        tray.show_icon()    

    # add the reminder and calculate the end time
    if event == "确认":
        # set reminder by target time
        if ((int(values['_TARGET_HR_']) != 0 or int(values['_TARGET_MIN_']) != 0)
            and (int(values['_LENGTH_HR_']) == 0 and int(values['_LENGTH_MIN_']) == 0)):

            target_hr = int(values['_TARGET_HR_'])
            target_min = int(values['_TARGET_MIN_'])
            time_end = dt.time(target_hr, target_min)
                
        # set reminder for a period of time
        elif ((int(values['_TARGET_HR_']) == 0 and int(values['_TARGET_MIN_']) == 0)
            and (int(values['_LENGTH_HR_']) != 0 or int(values['_LENGTH_MIN_']) != 0)):

            length_hr = int(values['_LENGTH_HR_'])
            length_min = int(values['_LENGTH_MIN_'])

            total_min = length_hr * 60 + length_min
            time_start = dt.datetime.now()
            time_delta = dt.timedelta(0, total_min * 60)
            time_end_details = time_start + time_delta
            time_end = dt.time(time_end_details.hour, time_end_details.minute)
        
        else:
            current_time_details = dt.datetime.now()
            time_end = dt.time(current_time_details.hour, current_time_details.minute)

        task = values['_CONTENT_']
        active_reminders[task] = time_end

        # sort the list of reminders to put the closest the first
        active_reminders = {k: v for k, v in sorted(active_reminders.items(), key=lambda item: item[1])}

        # generate the text for the reminders to print out in the window
        upcoming_reminders_text = ""
        for reminder in active_reminders:
            reminder_text = f"{reminder}：{active_reminders[reminder].hour}点{active_reminders[reminder].minute}分 \n"
            upcoming_reminders_text += reminder_text            
        window['_UPCOMING_REMINDERS_'].update(upcoming_reminders_text)
        window['_TARGET_HR_'].update(0)
        window['_TARGET_MIN_'].update(0)
        window['_LENGTH_HR_'].update(0)
        window['_LENGTH_MIN_'].update(0)
        window['_CONTENT_'].update('')
    
    # if there are active reminders
    if active_reminders != {}:
        current_time_details = dt.datetime.now()
        current_time = dt.time(current_time_details.hour, current_time_details.minute)
        # if the first one (closest one) gets to the end time
        if list(active_reminders.values())[0] == current_time:
            # show notification
            print("done")
            toaster.show_toast(values['_CONTENT_'], "时间到啦!", icon_path='icon.ico', duration=10, threaded=True)
            # remove it from the list
            active_reminders.pop(list(active_reminders.keys())[0])

            # update the printed list of reminders
            upcoming_reminders_text = ""
            for reminder in active_reminders:
                reminder_text = f"{reminder} at {active_reminders[reminder].hour}:{active_reminders[reminder].minute} \n"
                upcoming_reminders_text += reminder_text            
            window['_UPCOMING_REMINDERS_'].update(upcoming_reminders_text)


        




tray.close()            # optional but without a close, the icon may "linger" until moused over
window.close()
             


