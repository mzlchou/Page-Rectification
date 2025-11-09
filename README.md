Document Rectication Pipeline
Michael Chou
October 2025
Computer Vision CS-132

This project implements an automatic document rectification pipeline that detects a document within an image, finds its corners, and applies a homography transform to produce a top down, flattened version of the page. 

The pipeline processes all images in an input folder and outputs rectified versions to an outputs directory

Usage:
python3 rectify.py <input_folder>

Pipeline Description

1. Preprocessing and Binarization
- Convert to grayscale
- Apply gaussian blur to get rid of noise
    -  Produced smoother edges and better Canny response
- I tried adaptive thresholding and Otsu's method, but I decided not to use because they didn't give as good results

2. Edge and Contour Extraction
- Apply Canny edge detection to find strong gradients which correspond to the edges of the page
    - With thresholds (100, 200), I got stable edges with low false positives across the different textures (except grass that was too difficult)
- Use morphological dilation to make the edges thicker and more connected, improving the contour continuity
- Extract the contours using cv2.findContours and selecting the largest one, assuming that the largest one is the document (ie. no like big box on the side)

3. Finding Corners
- Apply cv2.approxPolyDP (uses the Ramer Douglas Peuker algorithm) with a epsilon of .5-8% of the perimeter to approximate the contour as a polygon
    - I increased the paramters until 4 corners were detecting
- Choose the first approximation that yields 4 vertices (which are the corners of the page)
- If 4 corners aren't found, then use cv2.minAreaRect as a backup
- order_points() arranges the corners in a consistent order: top left, top right, bottom right, bottom left

4. Homography and Rectification
- Compute a homography matrix with cv2.findHomography mapping the detected corners to a fixed rectangle (550x425 pixels as asked for)
- Warp the original image using cv2.warpPerspective to obtain the top down rectified view!

5. Additional Code
- The script processes all .jpg, .jpeg, and .png images in the specified folder and saves the results in an outputs directory