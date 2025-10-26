import requests, os

token = os.getenv("VK_TOKEN")
resp = requests.get("https://api.vk.com/method/users.get", params={
    "access_token": token,
    "v": "5.131"
})
print(resp.json())
