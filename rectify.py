import numpy as np
import os
import cv2
import sys

def order_points(corners):
    ordered = np.zeros((4, 2), dtype="float32")
    cornersum = corners.sum(axis=1) #sum x and y vals to see which top left and bottom right
    ordered[0] = corners[np.argmin(cornersum)] #top left smallest
    ordered[2] = corners[np.argmax(cornersum)] #bottom right biggest
    
    diff = np.diff(corners, axis=1) #subtract to see which top right and bottom left
    ordered[1] = corners[np.argmax(diff)] #top right x large y small x-y -> large pos
    ordered[3] = corners[np.argmin(diff)] #bottom left x small y big x-y -> large neg

    return ordered

def process_image(img):
    
    #preprocessing and binarization
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #convert to gray
    blur_img = cv2.GaussianBlur(gray_img, (5,5), 0) #blur

    #wasn't having great results with these:
    # thresh = cv2.adaptiveThreshold(blur_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 10)

    # blur_img = cv2.GaussianBlur(blur_img, (11,11), 0) #matt
    # _, blur_img = cv2.threshold(blur_img, 0, 255, cv2.THRESH_BINARY +cv2.THRESH_OTSU)


    #feature and contor extraction
    edges = cv2.Canny(blur_img, 100, 200)

    # make detected edges bolder and more connected
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    edges = cv2.dilate(edges, kernel, iterations=1)
    
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #we want contour of edges of page
    # add if no contour print no contour
    if not contours:
        print("no contour")
        return

    page = max(contours, key=cv2.contourArea) #the contour of the page is biggest contour

    #what i found to work the best
    page = cv2.convexHull(page)
    perimeter = cv2.arcLength(page, True)
    for i in np.linspace(.005, .08, 24):
        eps = i * perimeter
        poly = cv2.approxPolyDP(page, eps, True)
        n = len(poly)
        if n == 4:
            approx = poly
            break
    
    # just in case
    if approx is None:
        rect = cv2.minAreaRect(page)
        approx = cv2.boxPoints(rect)
        approx = approx.astype(int)
    
    corners = approx.reshape(4,2) #412 -> 42
    ordered_corners = order_points(corners)

    #draw corners got rid of for testing
    # cv2.drawContours(img, [approx],-1,(0,255,0),2)

    # for x, y in corners:
    #     cv2.circle(img, (x,y), 5, (0,0,255), -1)
    
    
    width, height = 550, 425
    destination_points = np.array([
        [0,0], #top left
        [width-1, 0], #top right
        [width-1, height-1], #bottom right
        [0, height-1] #bottom left
    ], dtype = "float32") #need float32 to put in func, wasnt working
    
    #homography computeation
    H, _ = cv2.findHomography(ordered_corners, destination_points)
    rectified_page = cv2.warpPerspective(img, H, (width,height))
    #print("success")
    return rectified_page



def main():
    #making sure folder is in command line
    if len(sys.argv) < 2:
        print("Usage: python3 rectify.py <input_folder>")
        return

    input_folder = sys.argv[1]
    output_folder = "outputs"
    os.makedirs(output_folder, exist_ok=True)

    #loop thru images
    i = 1
    for filename in sorted(os.listdir(input_folder)):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            path = os.path.join(input_folder, filename)
            img = cv2.imread(path)
            rectified = process_image(img)
            output = f"output{i}.jpg"
            cv2.imwrite(os.path.join(output_folder, output), rectified)
            i+=1

if __name__ == "__main__":
    main()
