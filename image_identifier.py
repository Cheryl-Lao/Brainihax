import http.client, urllib.request, urllib.parse, urllib.error, base64, requests, time, json

import sys

def find_L(predictions):
    #TODO -- turn this into a python max heap 
    
    biggest_L = None
    biggest_N = None

    for prediction in predictions:
        if prediction['tagName'] == "L":
            #If there has been no leukocoria entry yet, this entry is the most likely by default
            if not biggest_L:
                biggest_L = prediction
            else:
                #Take the new entry if we're more confident in it
                if float(prediction['probability']) > float(biggest_L['probability']):
                    biggest_L = prediction
        else:
            #If there has been no normal entry yet, this entry is the most likely by default
            if not biggest_N:
                biggest_N = prediction
            else:
                #Take the new entry if we're more confident in it
                if float(prediction['probability']) > float(biggest_N['probability']):
                    biggest_N = prediction
           
    return (biggest_L, biggest_N)
    
    
#Determines which eye has the leukocoria
"""
One eye with L, one eye without

More than one L:
-Take top 2 and then compare their percentages. if the discrepancy is huge, ignore the smaller one

No L identification: normal


Overlap detection:
-look at whether something is in a ___% margin of another box ()


-{'left': 0.05884423, 'top': 0.435253441, 'width': 0.170019567, 'height': 0.1491468}


-normal and L are in a queue from most to least likely.
Check that the 


left and right eye -- how to we differentiate them

"""

def area_from_tuple(boundingBox):
    width = boundingBox['width']
    height = boundingBox['height']
    return float(width) * float(height)
    
    
def coords_from_tuple(boundingBox):
    #top left is (0,0)
    left = boundingBox['left']
    top = boundingBox['top']
    width = boundingBox['width']
    height = boundingBox['height']
    
    top_left = tuple(left, top)
    top_right = tuple(left + width, top)
    bottom_left = tuple(left, top + height)
    bottom_right = tuple(left + width, top + height)
    return [top_left, top_right, bottom_left, bottom_right]

    
def is_overlapping(boundingBox1, boundingBox2):

    box1 = coords_from_tuple(boundingBox1)
    box2 = coords_from_tuple(boundingBox2)
    dx = min(box1[3][0], box2[3][0]) - max(box1[2][0], box2[2][0])
    dy = min(box1[1][1], box2[1][1]) - max(box1[0][1], box2[0][1])
    
    overlapping_area = dy*dx
    
    #Check if the overlapping area is larger than 80% of either 
    overlap_percentage1 = overlapping_area / area_from_tuple(boundingBox1)
    overlap_percentage2 = overlapping_area / area_from_tuple(boundingBox2)
    
    if (overlap_percentage1 > 0.8 or overlap_percentage2 > 0.8):
        return True
    

#Returns the side that has the Leukocoria
def orientation_determination(L_location, N_location):
    
    
    if L_location['left'] > N_location['left']:
        print(L_location['left'])
        print(N_location['left'])
        return 'left'
    else:
        print(L_location['left'])
        print(N_location['left'])
        return 'right'

    
    
    
#---Setting up the connection---
project_id = '922a5f49-caba-4765-9c93-f477802076ef'
# without flips   iteration_id = 'b6349a1d-8acd-4038-9967-3123fc2dd393'
# with flips iteration_id = '433c5b96-513d-47b6-b47d-129eba02a47b'
iteration_id = '067cafec-c7d1-4adb-9a53-333c1ecac28d'
endpoint = 'https://southcentralus.api.cognitive.microsoft.com/customvision/v2.0/Prediction/{0}/url?iterationId={1}'.format(project_id, iteration_id)

prediction_key = '0cda307794064acca38bb0f860932935'

# HTTP request to send to the API
# Look at the RecognizeText function from Microsoft
headers = {
    # Request headers.
    # Another valid content type is "application/octet-stream".
    'Prediction-Key': prediction_key,
    'Content-Type': 'application/json',
}

#Gets the first argument as the url of the picture to process
#body = {'url' : sys.argv[1]}
body = {'url' : 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQY-xnN5ybvgu3o9LKD2yBHpQln7An4IIgb3HoaB1MMx1Wupe6D'}
#body = {'url' : 'https://www.medscape.com/content/2004/00/49/13/491384/art-cc491384.fig2.jpg'}


#Try sending the image to the CV API
try:
    print('Getting response...')
    #response = requests.request('POST ', endpoint, json=body, data=None, headers=headers, params=params)
    response = requests.request('POST ', endpoint, json=body, data=None, headers=headers)

    #2__ is the success status code
    if not str(response.status_code).startswith("2"):
        # Display JSON data and exit if the REST API call was not successful.
        parsed = json.loads(response.text)
        print ("Error:" + str(response.status_code))
        print (json.dumps(parsed, sort_keys=True, indent=2))
        exit()

    #It will take a little bit of time to load so just make the user wait
    time.sleep(3)

    # Contains the JSON data. The following formats the JSON data for display.
    parsed = json.loads(response.text)
    predictions = parsed['predictions']
    
    L, N = find_L(predictions)
    L_eye = L
    if L_eye:
        print('Leukocoria probability: ' + str(float(L_eye['probability']) * 100) + '%')
    else:
       print('Eyes are normal')

    if N:
        print('N probability: ' + str(float(N['probability']) * 100) + '%')
    else:
       print('Eyes are normal')
	   
	   
    orientation_determination(L, N)
    
    # Get the transcribed lines of text
    #print(parsed)
    
#Catch any exceptions that might happen
except Exception as e:
    print('Error:')
    print(e)
