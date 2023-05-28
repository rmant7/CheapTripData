import requests
# generate access token
url = 'https://www.linkedin.com/oauth/v2/accessToken'
params = {
    'grant_type': 'authorization_code',
    'code': 'replace with your authorization_code',
    'redirect_uri': 'replace with your redirect_uri',
    'client_id': 'replace with your client id',
    'client_secret': 'replace with your client secret'
}
response = requests.post(url, data=params)

if response.status_code == 200:
    access_token = response.json()['access_token']
    print('Access token:', access_token)
    api_url = 'https://api.linkedin.com/v2/me'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Connection': 'Keep-Alive',
        'Content-Type': 'application/json',
    }
    # verify the access token
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        print('Access token is valid!')
        api_url = 'https://api.linkedin.com/v2/ugcPosts'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Connection': 'Keep-Alive',
            'Content-Type': 'application/json',
        }
        #create post
        post_body = {
            'author': 'urn:li:company:<replace with your company id>',
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {
                        'text': 'Check out our latest blog post!',
                    },
                    'shareMediaCategory': 'ARTICLE',
                    'media': [
                        {
                            'status': 'READY',
                            'description': {
                                'text': 'Read our latest blog post about LinkedIn API!',
                            },
                            'originalUrl': '<https://www.example.com/blog-post>',
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
    else:
        print(f'Access token is invalid or has expired. txt {response.text}')
else:
    print('Error:', response.status_code, response.text)