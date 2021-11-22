import PySimpleGUI as sg
from win10toast import ToastNotifier
from psgtray import SystemTray
import datetime as dt
import sys 
import os

#os.chdir(sys._MEIPASS)
# parameters
font = "Courier"
font_size = 12
background_color = "#FFEEED"
button_color = "#FFC2C0"
text_color = "#4A154B"

# window layout
layout = [   
            # Remind me to...
            [sg.Text('Remind me to...', font=(font, font_size), key="_TEXT1_", text_color = text_color, background_color = background_color)],
            # input the task
            [sg.Input('', size = (37, 1), do_not_clear=True, key='_CONTENT_', font = (font, font_size - 2), text_color = text_color)],
            # At XX:XX (time, hour:min  e.g. 9:00)
            [sg.Text('At', size=(6, 1), font=(font, font_size), key="_TEXT2_", text_color = text_color, background_color = background_color),
                sg.Input(00, key='_TARGET_HR_',  size=(3, 1), font = (font, font_size - 2), text_color = text_color),
                sg.Text(':', size=(3, 1), font=(font, font_size), key="_TEXT3_", text_color = text_color, background_color = background_color),
                sg.Input(00, key='_TARGET_MIN_',  size=(3, 1), font = (font, font_size - 2), text_color = text_color),
                sg.Text(' ', size=(3, 1), font=(font, font_size), key="_FORMATER_", text_color = text_color, background_color = background_color),
                sg.Button('Thanks', font=(font, font_size), focus=False, button_color = (text_color, button_color))],
            # Or in XX hr XX min
            [sg.Text('Or in', size=(6, 1), font=(font, font_size), key="_TEXT4_", text_color = text_color, background_color = background_color),
                sg.Input(00, key='_LENGTH_HR_',  size=(3, 1), font = (font, font_size - 2), text_color = text_color),
                sg.Text('hr', size=(3, 1), font=(font, font_size), key="_TEXT5_", text_color = text_color, background_color = background_color),
                sg.Input(00, key='_LENGTH_MIN_',  size=(3, 1), font = (font, font_size - 2), text_color = text_color),
                sg.Text('min', size=(3, 1), font=(font, font_size), key="_TEXT6_", text_color = text_color, background_color = background_color),
                sg.Button('Please', font=(font, font_size), focus=False, button_color = (text_color, button_color))],
            # upcoming reminders + hide button + exit button
            [sg.Text('Upcoming reminders', size = (18, 1), font=(font, font_size), key="_TEXT7_", text_color = text_color, background_color = background_color),
                sg.Button('Hide', focus=False, font=(font, font_size), button_color = (text_color, button_color)),
                sg.Button('Exit', font=(font, font_size), button_color = (text_color, button_color))],
            # print a list of upcoming reminders
            [sg.Text('', font = (font, font_size), key = "_UPCOMING_REMINDERS_", text_color = text_color, background_color = background_color)]]

# initiate the window
window = sg.Window('Reminder', enable_close_attempted_event=True, background_color = background_color).Layout(layout)

# minimized system tray
menu = ['', ['Show Window', 'Exit']]
tray = SystemTray(menu, single_click_events=False, window=window, tooltip='Reminder', icon='icon.ico')

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
    if event in ('Exit', sg.WIN_CLOSED):
        break

    # show window
    if event in ('Show Window', sg.EVENT_SYSTEM_TRAY_ICON_DOUBLE_CLICKED):
        window.un_hide()
        window.bring_to_front()
    
    # hide the window to task bar
    elif event in ('Hide', sg.WIN_CLOSE_ATTEMPTED_EVENT):
        window.hide()
        tray.show_icon()    

    # add the reminder and calculate the end time
    if event in ("Thanks", "Please"):
        # set reminder by target time
        if event == "Thanks":
            target_hr = int(values['_TARGET_HR_'])
            target_min = int(values['_TARGET_MIN_'])
            time_end = dt.time(target_hr, target_min)
                
        # set reminder for a period of time
        elif event == "Please":
            length_hr = int(values['_LENGTH_HR_'])
            length_min = int(values['_LENGTH_MIN_'])

            total_min = length_hr * 60 + length_min
            time_start = dt.datetime.now()
            time_delta = dt.timedelta(0, total_min * 60)
            time_end_details = time_start + time_delta
            time_end = dt.time(time_end_details.hour, time_end_details.minute)
            print(time_end)

        task = values['_CONTENT_']
        active_reminders[task] = time_end

        # sort the list of reminders to put the closest the first
        active_reminders = {k: v for k, v in sorted(active_reminders.items(), key=lambda item: item[1])}

        # generate the text for the reminders to print out in the window
        upcoming_reminders_text = ""
        for reminder in active_reminders:
            reminder_text = f"{reminder} at {active_reminders[reminder].hour}:{active_reminders[reminder].minute} \n"
            upcoming_reminders_text += reminder_text            
        window['_UPCOMING_REMINDERS_'].update(upcoming_reminders_text)
    
    # if there are active reminders
    if active_reminders != {}:
        current_time_details = dt.datetime.now()
        current_time = dt.time(current_time_details.hour, current_time_details.minute)
        print("current time", current_time)
        print("reminder time", list(active_reminders.values())[0])
        # if the first one (closest one) gets to the end time
        if list(active_reminders.values())[0] == current_time:
            # show notification
            print("done")
            toaster.show_toast('Reminder', values['_CONTENT_'], icon_path='icon.ico', duration=10, threaded=True)
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
             


