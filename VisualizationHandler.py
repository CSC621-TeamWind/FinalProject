# References: 
# https://simpleitk.readthedocs.io/en/master/link_DicomSeriesReader_docs.html
# https://www.raddq.com/dicom-processing-segmentation-visualization-in-python/
# https://vtk.org/gitweb?p=VTK.git;a=blob;f=Examples/Medical/Python/Medical4.py

import SimpleITK as sitk
import sys, os, vtk
import numpy as np
import pydicom as dicom
import matplotlib.pyplot as plt

def dicom_series_reader(input_dir, output_file):
    print( "Reading Dicom directory:", input_dir )
    reader = sitk.ImageSeriesReader()

    dicom_names = reader.GetGDCMSeriesFileNames( input_dir )
    reader.SetFileNames(dicom_names)

    image = reader.Execute()

    size = image.GetSize()
    print( "Image size:", size[0], size[1], size[2] )

    print( "Writing image:", output_file )

    sitk.WriteImage( image, output_file )

def load_dicom_series(input_dir):
    slices = []
    images_path = os.listdir(input_dir)
    images_path.sort()
    for image in images_path:
        filename = os.path.join(input_dir, image)
        slice = dicom.dcmread(filename)
        slices.append(slice)
    try:
        slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
    except:
        slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)
        
    for s in slices:
        s.SliceThickness = slice_thickness
        
    return slices

def get_pixels_hu(scans):
    image = np.stack([s.pixel_array for s in scans])
    image = image.astype(np.int16)

    image[image == -2000] = 0

    intercept = scans[0].RescaleIntercept
    slope = scans[0].RescaleSlope
    
    if slope != 1:
        image = slope * image.astype(np.float64)
        image = image.astype(np.int16)
        
    image += np.int16(intercept)
    
    return np.array(image, dtype=np.int16)

def view_histogram(imgs):
    plt.hist(imgs.flatten(), bins=50, color='c')
    plt.xlabel("Hounsfield Units (HU)")
    plt.ylabel("Frequency")
    plt.show(block=False)

def view_dicom_img(img_title, img, c_label):
    plt.title(img_title)
    plt.axis('off')
    plt.draw()
    if c_label == True:
        plt.imshow(img)
    else:
        plt.imshow(img, 'gray')
    plt.show(block=False)

def view_3d(filename): 
    # Create the renderer, the render window, and the interactor. The renderer
    # draws into the render window, the interactor enables mouse- and
    # keyboard-based interaction with the scene.
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # The following reader is used to read a Nrrd file
    v16 = vtk.vtkNrrdReader()
    v16.SetFileName(filename)
    v16.Update()   

    # The volume will be displayed by ray-cast alpha compositing.
    # A ray-cast mapper is needed to do the ray-casting, and a
    # compositing function is needed to do the compositing along the ray.
    volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
    volumeMapper.SetInputConnection(v16.GetOutputPort())
    volumeMapper.SetBlendModeToComposite()

    # The color transfer function maps voxel intensities to colors.
    # It is modality-specific, and often anatomy-specific as well.
    # The goal is to one color for flesh (between 300 and 1000)
    # and another color for bone (1150 and over).
    volumeColor = vtk.vtkColorTransferFunction()
    volumeColor.AddRGBPoint(0,    0.0, 0.0, 0.0)
    volumeColor.AddRGBPoint(300,  1.0, 0.5, 0.3)
    volumeColor.AddRGBPoint(1000, 1.0, 0.5, 0.3)
    volumeColor.AddRGBPoint(1150, 1.0, 1.0, 0.9)

    # The opacity transfer function is used to control the opacity
    # of different tissue types.
    volumeScalarOpacity = vtk.vtkPiecewiseFunction()
    volumeScalarOpacity.AddPoint(0,    0.00)
    volumeScalarOpacity.AddPoint(300,  0.15)
    volumeScalarOpacity.AddPoint(1000, 0.15)
    volumeScalarOpacity.AddPoint(1150, 0.85)

    # The gradient opacity function is used to decrease the opacity
    # in the "flat" regions of the volume while maintaining the opacity
    # at the boundaries between tissue types.  The gradient is measured
    # as the amount by which the intensity changes over unit distance.
    # For most medical data, the unit distance is 1mm.
    volumeGradientOpacity = vtk.vtkPiecewiseFunction()
    volumeGradientOpacity.AddPoint(0,   0.0)
    volumeGradientOpacity.AddPoint(90,  0.5)
    volumeGradientOpacity.AddPoint(100, 1.0)

    # The VolumeProperty attaches the color and opacity functions to the
    # volume, and sets other volume properties.  The interpolation should
    # be set to linear to do a high-quality rendering.  The ShadeOn option
    # turns on directional lighting, which will usually enhance the
    # appearance of the volume and make it look more "3D".  However,
    # the quality of the shading depends on how accurately the gradient
    # of the volume can be calculated, and for noisy data the gradient
    # estimation will be very poor.  The impact of the shading can be
    # decreased by increasing the Ambient coefficient while decreasing
    # the Diffuse and Specular coefficient.  To increase the impact
    # of shading, decrease the Ambient and increase the Diffuse and Specular.
    volumeProperty = vtk.vtkVolumeProperty()
    volumeProperty.SetColor(volumeColor)
    volumeProperty.SetScalarOpacity(volumeScalarOpacity)
    volumeProperty.SetGradientOpacity(volumeGradientOpacity)
    volumeProperty.SetInterpolationTypeToLinear()
    volumeProperty.ShadeOn()
    volumeProperty.SetAmbient(0.4)
    volumeProperty.SetDiffuse(0.6)
    volumeProperty.SetSpecular(0.2)

    # The vtkVolume is a vtkProp3D (like a vtkActor) and controls the position
    # and orientation of the volume in world coordinates.
    volume = vtk.vtkVolume()
    volume.SetMapper(volumeMapper)
    volume.SetProperty(volumeProperty)

    # Finally, add the volume to the renderer
    ren.AddViewProp(volume)

    # Set up an initial view of the volume.  The focal point will be the
    # center of the volume, and the camera position will be 400mm to the
    # patient's left (which is our right).
    camera =  ren.GetActiveCamera()
    c = volume.GetCenter()
    camera.SetFocalPoint(c[0], c[1], c[2])
    camera.SetPosition(c[0] + 400, c[1], c[2])
    camera.SetViewUp(0, 0, -1)

    # Increase the size of the render window
    renWin.SetSize(1000, 800)

    # Interact with the data.
    iren.Initialize()
    renWin.Render()
    iren.Start()