import PySimpleGUI as sg
from PIL import Image
import io

import pyvista as pv
import os
import vtk
from VisualizationHandler import *
from Segmentation import *


sg.theme('BrownBlue')  

folder_path = ''
files_path = []
num_of_files = 0
nrrd_file = './ct_lungs.nrrd' 
import_success = False
images = []
resampled_images = []
t_images = []
c_label = False

button_prop = {'size':(8,1), 'font':('Helevetica', 12)}
# All the elements inside the popup window. 
layout = [[sg.Text('Choose Dicom Series of Lungs:', size=(25,1), font=('Helevetica', 14))],
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
            patient = load_dicom_series(folder_path)
            images = get_pixels_hu(patient)
            resampled_images = resample(images, patient)
            num_of_files = len(images)
            dicom_series_reader(folder_path, nrrd_file)
            import_success = True
            break
popup.close()


if import_success:
    t_images = images
    slider_prop = {'range':(0, num_of_files-1), 'orientation':'h', 'size':(70, 20), 'default_value':0}
    window_prop = {'margins':(0,0), 'size':(520, 420), 'return_keyboard_events':True}
    buttons_prop = {'size':(35, 1), 'font':('Helvetica', 12)}
    radios_prop = {'size':(30, 1), 'font':('Helvetica', 12)}

    col1 = [[sg.Button('View Original Image', **buttons_prop)],
            [sg.Button('View Histogram', key='o_histo', **buttons_prop)],
            [sg.Button('View in 3D', key='original_3d', **buttons_prop)]]

    col2 = [[sg.Button('View Transformed Image', **buttons_prop)],
            [sg.Button('View Histogram', key='n_histo', **buttons_prop)],
            [sg.Button('View in 3D', key="transformed_3d", **buttons_prop)]]      

    col3 = [[sg.Text('Segmentation:', size=(30,1), font=('Helvetica', 14))],
            [sg.Radio('Smoothing + Thresholding', 'seg', key='op1', **radios_prop)],
            [sg.Radio('Masking', 'seg', key='op2', **radios_prop)],
            [sg.Radio('Color Labeling', 'seg', key='op3', **radios_prop)],
            [sg.Button('Run Segmentation', **buttons_prop)],
            [sg.Button('Reset', **buttons_prop)]]

    # All the elements inside the window. 
    layout = [[sg.Text('Move through images:', size=(35, 1), font=('Helvetica', 16))],
              [sg.Slider(key='image_slider', **slider_prop)],
              [sg.Column(col1), sg.Column(col2)],
              [sg.Text('_'  * 100, size=(100, 1))],
              [sg.Column(col3)]]

    # Create the window
    window = sg.Window('Medical Image Processor', layout, **window_prop)

    # Event Loop to process events
    while True:             
        event, values = window.read()
        if event in (None, 'Cancel'):
            break
        if event in ('View Original Image'):
            index = int(values['image_slider'])
            view_dicom_img('Original Image', images[index], c_label) 
        if event in ('View Transformed Image'):
            index = int(values['image_slider'])
            if len(t_images) > 0:
                view_dicom_img('Transformed Image', t_images[index], c_label) 
            else:
                view_dicom_img('Transformed Image', images[index], c_label) 
        if event in ('original_3d'):
            view_3d(nrrd_file)
        if event in ('Run Segmentation'):
            print('Running Segmentation...')
            if values['op1'] == True:
                t_images = run_smoothing(resampled_images)
                t_images = run_thresholding(t_images)
                c_label = False
            if values['op2'] == True:
                t_images = run_masking(resampled_images)
                c_label = False
            if values['op3'] == True:
                t_images = run_color_labeling(resampled_images)
                c_label = True
        if event in ('Reset'):
            t_images = images
        if event in ('o_histo'):
            view_histogram(images)
    window.close()