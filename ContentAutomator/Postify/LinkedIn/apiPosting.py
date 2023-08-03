import json

import requests

access_token="AQUHl_E7hHOy8NetEGphppwDXRCQfA8wCkFWzX4LbvqRXsGAjZfrHUFDw1exvMIityminyxEbsugbBX3IabgsO_t50M8L-JYrnhEmVF8sxGa085f98Cw05qsTcGrQ_ZSm0oBjTOywX0NEIM9JqrMHMpULwEvaxthoJYjB4U2APDG5IyYvUWeKhgCxN_dNXG8JpA_av24AvdMOzaehtDPZ7o4eDpuS4yFd_p58RH-iw4OKIZo8bqXslZsvLwrLZzAtXnarhtbrSHjG68HkpKP_N0FGHAWEJ2Ul_dAOxXmUBIR1tPh2x_BNn7Ct238fgIiIaT3mcodxQDo9XpHgxXR5xOrKIfQMQ"

def get_url():
    api_url = 'https://api.linkedin.com/v2/assets?action=registerUpload'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Connection': 'Keep-Alive',
        'Content-Type': 'application/json',
    }
    """https://www.linkedin.com/company/35430256/admin/feed/posts/"""
    post_body = {
        "registerUploadRequest": {
            "recipes": [
                "urn:li:digitalmediaRecipe:feedshare-image"
            ],
            "owner": "urn:li:company:35430256",
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }
            ]
        }
    }

    response = requests.post(api_url, headers=headers, json=post_body)
    if response.status_code == 200:
        print('Url successfully created!\n')
        print(response.text)
        # Parse the JSON string into a Python dictionary
        data = json.loads(response.text)

        # Extract the 'uploadUrl' and 'asset' values
        upload_url = data['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest'][
            'uploadUrl']
        asset = data['value']['asset']

        print("Upload URL:", upload_url)
        print("Asset:", asset)
        return  upload_url,asset
    else:
        print(f'Post creation failed with status code {response.status_code}: {response.text}')

def add_hashtags_location(input_string):
    # Remove leading and trailing whitespaces and split the string by commas and spaces
    parts = input_string.strip().split(", ")

    # Extract the attraction and location names
    attraction = parts[0]
    location = parts[1]

    # Remove spaces from attraction name and add a '#' in front of it
    attraction_hashtag = "#" + attraction.replace(" ", "")

    # Remove spaces from location name and add a '#' in front of it
    location_hashtag = "#" + location.replace(" ", "")

    # Concatenate the attraction and location hashtags
    result_string = attraction_hashtag + " " + location_hashtag

    return result_string
def upload_binary(image_path, upload_url):
    # Replace 'YOUR_IMAGE_PATH' with the path to your image file
    image_path = image_path

    # Replace 'YOUR_UPLOAD_URL' with the upload URL received from Step 1
    upload_url = upload_url

   # Read the image as binary
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()

    # Set the headers for the request
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/octet-stream',
    }

    # Send the POST request with the image data
    response = requests.post(upload_url, data=image_data, headers=headers)

    # Print the response status code and content (if needed)
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content}")
def add_hashtags_to_words(input_string):
    words = input_string.split()  # Split the string into words
    modified_words = ['#' + word for word in words]  # Add '#' to each word
    result_string = ' '.join(modified_words)  # Join the modified words back into a single string
    return result_string

api_url = 'https://api.linkedin.com/v2/ugcPosts'
with open('text1.json', 'r') as file:
    data = json.load(file)

hashtags= "#CheapTripGuru #travel #cheaptrip #budgettravel #travelonabudget #lowcosttravel #affordabletravel #backpackerlife #travelhacks #cheapholidays #travelbudgeting #frugaltravel #savvytraveler #travelblogger #traveltips #traveladvice #travelhacks #travelinspiration #wanderlust #explore #seetheworld"
text = data['text']
hashtags +=' '+ ' '.join(data['hashtags'])
location = data['location']
location = add_hashtags_location(location)
post_text = f"{location}\n{text}\n\nFind out more at https://cheaptrip.guru\n\n{hashtags}"
url,urn=get_url()
upload_binary(r"C:\Users\faisal\Desktop\CheapTripData\ContentAutomator\Postify\LinkedIn\image1.jpg",url)


headers = {
    'Authorization': f'Bearer {access_token}',
    'Connection': 'Keep-Alive',
    'Content-Type': 'application/json',
}
"""https://www.linkedin.com/company/35430256/admin/feed/posts/"""
post_body = {
    'author': 'urn:li:company:35430256',
    'lifecycleState': 'PUBLISHED',
    'specificContent': {
        'com.linkedin.ugc.ShareContent': {
            'shareCommentary': {
                'text': post_text,
            },
            'shareMediaCategory': 'IMAGE',
            'media': [
                {
                    'status': 'READY',
                    'description': {
                        'text': 'Aalborg Zoo',
                    },
                    "media": urn,
                    "title": {
                        "text": "Aalborg Zoo"
                    }
                },
            ],
        },
    },
    'visibility': {
        'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC',
    },
}

response = requests.post(api_url, headers=headers, json=post_body)
if response.status_code == 201:
    print('Post successfully created!')
else:
    print(f'Post creation failed with status code {response.status_code}: {response.text}')


