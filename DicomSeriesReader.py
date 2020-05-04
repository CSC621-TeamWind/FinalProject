#!/usr/bin/env python
#=========================================================================
#
#  Copyright Insight Software Consortium
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0.txt
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#=========================================================================


import SimpleITK as sitk
import sys, os

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
