import requests

api_url = 'https://api.linkedin.com/v2/ugcPosts'
access_token="AQUHl_E7hHOy8NetEGphppwDXRCQfA8wCkFWzX4LbvqRXsGAjZfrHUFDw1exvMIityminyxEbsugbBX3IabgsO_t50M8L-JYrnhEmVF8sxGa085f98Cw05qsTcGrQ_ZSm0oBjTOywX0NEIM9JqrMHMpULwEvaxthoJYjB4U2APDG5IyYvUWeKhgCxN_dNXG8JpA_av24AvdMOzaehtDPZ7o4eDpuS4yFd_p58RH-iw4OKIZo8bqXslZsvLwrLZzAtXnarhtbrSHjG68HkpKP_N0FGHAWEJ2Ul_dAOxXmUBIR1tPh2x_BNn7Ct238fgIiIaT3mcodxQDo9XpHgxXR5xOrKIfQMQ"

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
                'text': 'Check out our latest blog post!',
            },
            'shareMediaCategory': 'ARTICLE',
            'media': [
                {
                    'status': 'READY',
                    'description': {
                        'text': 'Read our latest blog post about LinkedIn API!',
                    },
                    'originalUrl': '<your_blog_post_url>',
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