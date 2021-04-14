import cv2, numpy as np
from skimage import measure

#https://stackoverflow.com/questions/25008458/how-to-apply-clahe-on-rgb-color-images
# https://stackoverflow.com/questions/46390779/automatic-white-balancing-with-grayworld-assumption
def white_balance(img):
	result = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
	avg_a = np.average(result[:, :, 1])
	avg_b = np.average(result[:, :, 2])
	clahe = cv2.createCLAHE(clipLimit=1.25, tileGridSize=(8,8))
	result[:, :, 0] = clahe.apply(result[:, :, 0])
	result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
	result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)
	result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
	return result

def extract_YCrCb(img):
    img_ycr = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)
    y = img_ycr[:,:,0]
    cr = img_ycr[:,:,1]
    cb = img_ycr[:,:,2]
    return (y,cr,cb)

def extract_RGB(img):
    b = img[:,:,0]
    g = img[:,:,1]
    r = img[:,:,2]
    return (r,g,b)

def extract_HSV(img):
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h = img_hsv[:,:,0]
    s = img_hsv[:,:,1]
    v = img_hsv[:,:,2]
    return (h,s,v)

def get_RGB_mask(img):
    (r,g,b) = extract_RGB(img)
    face_rg = (r>(b*0.95))
    face_rb = (r>(g*0.95))
    face_rgb = np.logical_and(face_rg,face_rb)
    return face_rgb

def get_YCbCr_mask(img):
    (y,cr,cb) = extract_YCrCb(img)
    face_cb = np.array(np.logical_and(cb > 70, cb < 135), dtype=np.uint8) 
    face_cr = np.array(np.logical_and(cr > 130, cr < 170), dtype=np.uint8) 
    face_cbcr = np.logical_and(face_cb,face_cr)
    return face_cbcr

def get_HSV_mask(img):
    (h,s,v) = extract_HSV(img)
    face_h = np.array(np.logical_or(h < 70, h > 160), dtype=np.uint8) 
    return face_h

def apply_fast_morphology(mask):
    strel_50 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(50,50))
    strel_100 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(100,100))
    mask = np.array(mask, dtype=np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, strel_50) 
    mask = remove_small_regions(mask)
    mask = cv2.dilate(mask, strel_100)
    return mask

def remove_small_regions(bin_img):
    (h,w) = bin_img.shape
    labelled_regions = measure.label(bin_img, background=0)
    unique, counts = np.unique(labelled_regions, return_counts=True)
    for i in unique:
        if (counts[i]/bin_img.size) < 0.0045:
            bin_img[labelled_regions==i] = 0     
    return bin_img

def apply_skin_mask(frame):
    #
    #  get skin region
    #
    # white balance and contrast normalization (CLAHE)
    img_bal = white_balance(frame)
    # apply RGB criteria
    mask_rgb = get_RGB_mask(img_bal)
    # apply YCbCr criteria
    mask_cbcr = get_YCbCr_mask(img_bal)
    # combine colour-space masks
    skin_mask = np.logical_and(mask_rgb, mask_cbcr)
    # apply morphology to mask
    img_morph = apply_fast_morphology(skin_mask)
    # apply mask to initial image
    #img_masked = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) * img_morph    
    img_masked = frame * np.expand_dims(img_morph,3)    

    return img_masked

def find_biggest_valid_region(bin_img, all_regions=False):
    (h,w) = bin_img.shape
    labelled_regions = measure.label(bin_img, background=0)
    unique, counts = np.unique(labelled_regions, return_counts=True)
    counts[0]=0
    candidate=False
    while(not candidate): 
        biggest_region = np.argmax(counts)
        region = np.array(labelled_regions==biggest_region, dtype=np.uint8)
        x_bb,y_bb,w_bb,h_bb = cv2.boundingRect(region)
        if (np.max(counts) == 0):
            candidate = True
            print("All regions checked, none valid")
        elif (h_bb>w_bb*2.5 or w_bb>h_bb*2.5): #w_bb>w*0.95 or h_bb>h*0.95 or w_bb<w*0.05 or h_bb<h*0.05 or 
            print("biggest region: ", biggest_region, "  (h/w: ", h_bb, w_bb, float(h_bb)/float(w_bb),")")
            counts[biggest_region] = 0
        else:
            candidate = True
        
    if (np.max(counts) == 0):
        region = np.array(labelled_regions==0, dtype=np.uint8)
    
    if(all_regions):
        return (region, labelled_regions)
    else:
        return region
