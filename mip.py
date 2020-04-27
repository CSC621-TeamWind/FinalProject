import PySimpleGUI as sg
from PIL import Image
import io

import pydicom as dicom
import matplotlib.pyplot as plt
import os

sg.theme('BrownBlue')  

folder_path = ''
files_path = []
num_of_files = 0
import_success = False

def get_files():
    images_path = os.listdir(folder_path)
    images_path.sort()
    for image in images_path:
        filename = '{}/{}'.format(folder_path, image)
        files_path.append(filename)
    return len(files_path)


def view_dcm(image_path):
    ds = dicom.dcmread(image_path)
    plt.imshow(ds.pixel_array)
    plt.show()

button_prop = {'size':(8,1), 'font':('Helevetica', 12)}
# All the elements inside the popup window. 
layout = [[sg.Text('Choose Image folder:', size=(20,1), font=('Helevetica', 14))],
          [sg.Input(key='folder_path', size=(40,1), font=('Helevetica', 12)), 
            sg.FolderBrowse(target="folder_path", **button_prop)],
          [sg.Button('Import', **button_prop), sg.Button('Cancel', **button_prop)]]

# Create the popup window
popup = sg.Window('Choose Image folder', layout, size=(450, 120))

# Event Loop to process events
while True:             
    event, values = popup.read()
    if event in (None, 'Cancel'):
        import_success = False
        break
    if event in ('Import'):
        folder_path = values['folder_path']
        if folder_path != '':
            num_of_files = get_files()
            import_success = True
            break
popup.close()

if import_success:

    title = {'size':(35, 1), 'font':('Helvetica', 16)}
    slider_prop = {'range':(0, num_of_files), 'orientation':'h', 'size':(35, 20), 'default_value':0}
    window_prop = {'margins':(0,0), 'size':(625, 335), 'return_keyboard_events':True}
    buttons_prop = {'size':(30, 1), 'font':('Helvetica', 12)}

    col1 = [[sg.Text('Original Image', **title)],
            [sg.Button('View Original Image', **buttons_prop)],
            [sg.Slider(key='orig_image_slider', **slider_prop)],
            [sg.Text('_'  * 50, size=(40, 1))],
            [sg.Text('Segmentation:', size=(20,1), font=('Helvetica', 14))],
            [sg.Radio('Boundary Extraction', 'loss', **buttons_prop)],
            [sg.Radio('Region Filling', 'loss', **buttons_prop)],
            [sg.Radio('Thresholding', 'loss', **buttons_prop)],
            [sg.Button('Run Segmentation', **buttons_prop)]]
    
    col2 = [[sg.Text('Transformed Image', **title)],
            [sg.Button('View Transformed Image', **buttons_prop)],
            [sg.Slider(key='new_image_slider', **slider_prop)],
            [sg.Text('_'  * 50, size=(40, 1))],
            [sg.Text('Quantification:', size=(20,1), font=('Helvetica', 14))],
            [sg.Radio('Quantification method1', 'loss', **buttons_prop)],
            [sg.Radio('Quantification method2', 'loss', **buttons_prop)],
            [sg.Radio('Quantification method3', 'loss', **buttons_prop)],
            [sg.Button('Run Quantification', **buttons_prop)]]

    # All the elements inside the window. 
    layout = [[sg.Column(col1), sg.Column(col2)],
              [sg.Text('', size=(400, 1))],
              [sg.Button('View Histogram', size=(100, 1.5))]]

    # Create the window
    window = sg.Window('Medical Image Processor', layout, **window_prop)

    
    # Event Loop to process events
    while True:             
        event, values = window.read()
        if event in (None, 'Cancel'):
            break
        if event in ('View Original Image'):
            index = int(values['orig_image_slider'])
            view_dcm(files_path[index]) 
    window.close()