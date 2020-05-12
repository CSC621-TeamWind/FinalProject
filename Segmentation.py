# References: 
# https://www.raddq.com/dicom-processing-segmentation-visualization-in-python/

import numpy as np
import cv2
import scipy.ndimage
from skimage import morphology
from skimage import measure
from skimage.transform import resize
from sklearn.cluster import KMeans

def resample(image, scan, new_spacing=[1,1,1]):
    spacing = map(float, ([scan[0].SliceThickness] + list(scan[0].PixelSpacing)))
    spacing = np.array(list(spacing))

    resize_factor = spacing / new_spacing
    new_real_shape = image.shape * resize_factor
    new_shape = np.round(new_real_shape)
    real_resize_factor = new_shape / image.shape
    new_spacing = spacing / real_resize_factor
    
    image = scipy.ndimage.interpolation.zoom(image, real_resize_factor)
    return image

def run_smoothing(imgs):
    s_imgs = []
    for img in imgs:
        s_img = cv2.medianBlur(img, 5)
        s_imgs.append(s_img)
    return s_imgs

def thresholding(img):
    row_size= img.shape[0]
    col_size = img.shape[1]
    
    mean = np.mean(img)
    std = np.std(img)
    img = img-mean
    img = img/std
    
    middle = img[int(col_size/5):int(col_size/5*4),int(row_size/5):int(row_size/5*4)] 
    mean = np.mean(middle)  
    max = np.max(img)
    min = np.min(img)

    img[img==max]=mean
    img[img==min]=mean
    
    kmeans = KMeans(n_clusters=2).fit(np.reshape(middle,[np.prod(middle.shape),1]))
    centers = sorted(kmeans.cluster_centers_.flatten())
    threshold = np.mean(centers)
    thresh_img = np.where(img<threshold,1.0,0.0)  # threshold the image
    return thresh_img

def run_thresholding(imgs):
    thresh_imgs = []
    for img in imgs:
        thresh_img = thresholding(img)
        thresh_imgs.append(thresh_img)
    return thresh_imgs

def opening(img):
    eroded_img = morphology.erosion(img, np.ones([3,3]))
    dilated_img = morphology.dilation(eroded_img, np.ones([8,8]))
    return dilated_img

def run_opening(imgs):
    opened_imgs = []
    for img in imgs:
        opened_img = opening(img)
        opened_imgs.append(opened_img)
    return opened_imgs

def color_labeling(img):
    thresh_img = thresholding(img)
    opened_img = opening(thresh_img)
    cl_img = measure.label(opened_img)
    return cl_img

def run_color_labeling(imgs):
    cl_imgs = []
    for img in imgs:
        cl_img = color_labeling(img)
        cl_imgs.append(cl_img)
    return cl_imgs


def create_mask(img):
    row_size= img.shape[0]
    col_size = img.shape[1]
    c_img = color_labeling(img)
    regions = measure.regionprops(c_img)
    good_labels = []
    for prop in regions:
        B = prop.bbox
        if B[2]-B[0]<row_size/10*9 and B[3]-B[1]<col_size/10*9 and B[0]>row_size/5 and B[2]<col_size/5*4:
            good_labels.append(prop.label)
    mask = np.ndarray([row_size,col_size],dtype=np.int8)
    mask[:] = 0

    for N in good_labels:
        mask = mask + np.where(c_img==N,1,0)
    mask = morphology.dilation(mask,np.ones([10,10])) 
    return mask

def run_masking(imgs):
    masked_imgs = []
    for img in imgs:
        mask = create_mask(img)
        masked_img = mask*img
        masked_imgs.append(masked_img)
    return masked_imgs