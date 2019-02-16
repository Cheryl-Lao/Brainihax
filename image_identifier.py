import http.client, urllib.request, urllib.parse, urllib.error, base64, requests, time, json, heapq

import sys

def area_from_tuple(boundingBox):
    width = boundingBox['width']
    height = boundingBox['height']
    return float(width) * float(height)

    
def coords_from_tuple(boundingBox):
    left = boundingBox['left']
    top = boundingBox['top']
    width = boundingBox['width']
    height = boundingBox['height']
    
    top_left = (left, top)
    top_right = (left + width, top)
    bottom_left = (left, top + height)
    bottom_right = (left + width, top + height)
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
    return False
   
def categorize_eyes(predictions):

    heap = []

    for prediction in predictions:
        heapq.heappush(heap, (-1 * float(prediction['probability']), prediction))

    most_likely = heapq.heappop(heap)[1]
    second_most_likely = heapq.heappop(heap)[1]
    
    #If the top two choices overlap, pick another one
    while(is_overlapping(most_likely['boundingBox'], second_most_likely['boundingBox'])):
        second_most_likely = heapq.heappop(heap)[1]

    return (most_likely, second_most_likely)
       

#Orders the eyes from left to right
def order_L_to_R(L, N):
    L_left = L['boundingBox']['left']
    N_left = N['boundingBox']['left']

    if L_left > N_left:
        return (L, N)
    else:
        return (N, L)
    
    
def report_diagnosis(eye1, eye2):
    if (eye1['tagName'] == 'L' and eye2['tagName'] == 'L'):
        return 'Both eyes appear to have Leukocoria'
    elif (eye1['tagName'] == 'L' or eye2['tagName'] == 'L'):
        eyes = order_L_to_R(eye1, eye2)
        if eyes[0]['tagName'] == 'L':
            return 'We are {0}% confident that the left eye has Leukocoria'.format(round(100 * float(eyes[0]['probability']), 2))
        if eyes[1]['tagName'] == 'L':
            return 'We are {0}% confident that the right eye has Leukocoria'.format(round(100 * float(eyes[1]['probability']), 2))
    else:
        return 'No Leukocoria detected'
            
            
            
#---Setting up the connection---
project_id = '922a5f49-caba-4765-9c93-f477802076ef'
iteration_id = '319f3179-6b76-4c44-bfee-2703f527d34d'
prediction_key = '0cda307794064acca38bb0f860932935'
endpoint = 'https://southcentralus.api.cognitive.microsoft.com/customvision/v2.0/Prediction/{0}/url?iterationId={1}'.format(project_id, iteration_id)

# HTTP request to send to the API
headers = {
    # Request headers.
    'Prediction-Key': prediction_key,
    'Content-Type': 'application/json',
}

#Gets the first argument as the url of the picture to process
body = {'url' : sys.argv[1]}

#Try sending the image to the CV API
try:
    print('Getting response...')
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

    eye1, eye2 = categorize_eyes(predictions)

    print(report_diagnosis(eye1, eye2))
    
    
#Catch any exceptions that might happen
except Exception as e:
    print('Error:')
    print(e)
