import time
import requests
import json


MODEL_URL = "http://127.0.0.1:9090/api/v1/models/"
IMAGE_URL = "http://127.0.0.1:9090/api/v1/images/"
SESSION_URL = "http://127.0.0.1:9090/api/v1/sessions/"

HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en,de;q=0.9,de-DE;q=0.8,en-US;q=0.7",
    "Connection": "keep-alive",
    "Host": "127.0.0.1:9090",
    "Referer": "http://127.0.0.1:9090/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "sec-ch-ua": "\"Chromium\";v=\"116\", \"Not)A;Brand\";v=\"24\", \"Google Chrome\";v=\"116\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows"
}


def uploadImage(image, name):
    files_image = {
        'file': (f"{name}.png", open(image, 'rb'), 'image/png')
    }

    upload_image = requests.post(
        IMAGE_URL + 'upload?image_category=user&is_intermediate=false',
        headers=HEADERS,
        files=files_image
    )

    if upload_image.status_code == 201:
        location = upload_image.headers.get('location')
        print(f"{name} uploaded successfully. Location: {location}")
        imageId = upload_image.json()['image_name']
        #print(f"Image has the Id {imageId}")
        return imageId
    else:
        print(f"Uploading {image} failed with status code: {upload_image.status_code}")
        return None

def prepareJSON(imageId,maskId,jsonFilePath):
    with open(jsonFilePath) as json_file:
        json_data = json.load(json_file)

    imageNode1 = json_data["nodes"]["28b3d363-00e7-4bcc-a450-c0650b6fd643"]
    image1 = imageNode1["image"]
    image1["image_name"] = imageId
    image1["image_url"] = f"/api/v1/images/i/{imageId}/full"
    image1["thumbnail_url"] = f"/api/v1/images/i/{imageId}/thumbnail"

    imageNode2 = json_data["nodes"]["00ea33db-d1a1-48ea-9337-66fbcc6a18c8"]
    image2 = imageNode2["image"]
    image2["image_name"] = maskId
    image2["image_url"] = f"/api/v1/images/i/{maskId}/full"
    image2["thumbnail_url"] = f"/api/v1/images/i/{maskId}/thumbnail"

    return json.dumps(json_data)

def createSession(imageId, maskId, jsonFilePath='workflow/inpaintingv6.json'):
    jsonData = prepareJSON(imageId,maskId,jsonFilePath)

    create_session = requests.post(SESSION_URL, data=jsonData, headers=HEADERS)

    if create_session.status_code == 200:
        print(f"Creating Session was successful: {create_session.status_code}")
        return create_session.json()['id']
    else:
        print(f"Creation Session failed with status code: {create_session.status_code}")
        print(f"Creation Session failed with json: {create_session.json()}")
        return None


def invokeSession(sessionId):
    invoke_session = requests.put(SESSION_URL + sessionId + '/invoke?all=true')

    if invoke_session.status_code == 200 or invoke_session.status_code == 202:
        print(f"Invoking Session was successful: {invoke_session.status_code}")
    else:
        print(f"Invoking Session failed with status code: {invoke_session.status_code}")
        print(f"Invoking Session failed with json: {invoke_session.json()}")


def downloadResult(numberOfLatents2ImageNodes, outputPath='images/outputImages'):
    imageCount = numberOfPicturesOnServer()
    time.sleep(15)

    while numberOfPicturesOnServer() < imageCount + numberOfLatents2ImageNodes:
        time.sleep(3)

    #The extra break is taken to prevent RuntimeError: Response content longer than Content-Length
    time.sleep(1)
    resultId = extractOutputImageId()
    download_result = requests.get(IMAGE_URL + f'i/{resultId}/full')

    if download_result.status_code == 200:
        filename = 'resultPiece'
        full_output_path = f'{outputPath}/{filename}.png'

        with open(full_output_path, 'wb') as f:
            f.write(download_result.content)
        print(f"Image downloaded and saved as '{full_output_path}'")
    else:
        print(f"Failed to download image. Status code: {download_result.status_code}")


def numberOfPicturesOnServer():
    list_images = requests.get(IMAGE_URL + '?offset=0&limit=10')

    if list_images.status_code == 200:
        imageList = list_images.json()
        #print(imageList)
        imageCount = imageList['total']
        return imageCount
    else:
        print(f"Failed to retrieve image list. Status code: {list_images.status_code}")
        return None


def extractOutputImageId():
    list_images = requests.get(IMAGE_URL + '?offset=0&limit=10')

    if list_images.status_code == 200:
        imageList = list_images.json()

        if 'items' in imageList and imageList['items']:
            result_id = imageList['items'][0]['image_name']
            return result_id
        else:
            print("No images found in the response.")
            return None
    else:
        print(f"Failed to retrieve image list. Status code: {list_images.status_code}")
        return None

