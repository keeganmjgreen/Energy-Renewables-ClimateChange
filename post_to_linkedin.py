import os
import requests
from argparse import ArgumentParser

from post_collection import PostCollection
from dotenv import load_dotenv

load_dotenv()


def post_to_linkedin(post_text: str, image_path: str):
    access_token = os.environ["LINKEDIN_ACCESS_TOKEN"]
    author_urn = os.environ["LINKEDIN_AUTHOR_URN"]

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    register_upload_payload = {
        "registerUploadRequest": {
            "owner": author_urn,
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "serviceRelationships": [
                {
                    "identifier": "urn:li:userGeneratedContent",
                    "relationshipType": "OWNER",
                }
            ],
        }
    }

    response = requests.post(
        "https://api.linkedin.com/v2/assets?action=registerUpload",
        headers=headers,
        json=register_upload_payload,
    )

    upload_resp = response.json()
    upload_url = upload_resp["value"]["uploadMechanism"][
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
    ]["uploadUrl"]
    asset = upload_resp["value"]["asset"]

    with open(image_path, "rb") as f:
        image_data = f.read()

    upload_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "image/jpeg",
    }

    upload_response = requests.put(upload_url, headers=upload_headers, data=image_data)

    if upload_response.status_code == 201:
        print("Image uploaded successfully.")
    else:
        print("Image upload failed:", upload_response.text)

    post_payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": post_text},
                "shareMediaCategory": "IMAGE",
                "media": [
                    {
                        "status": "READY",
                        "description": {"text": "Image description"},
                        "media": asset,
                        "title": {"text": "Image Title"},
                    }
                ],
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    post_response = requests.post(
        "https://api.linkedin.com/v2/ugcPosts", headers=headers, json=post_payload
    )

    print(post_response.status_code, post_response.text)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--yaml-file")
    parser.add_argument("--post-index")
    args = parser.parse_args()
    post_index = int(args.post_index)
    post_collection = PostCollection.from_yaml_file(args.yaml_file)
    post = post_collection.posts[post_index]
    post_to_linkedin(post.text, image_path=post.post_image_fname)
