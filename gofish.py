import json
import requests

debug = True

url = "https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1"

payload={}
headers = {
  'Cookie': '__cfduid=d2328867035c577f6b29e7f1a33089ee31613535704'
}

response = requests.request("GET", url, headers=headers, data=payload)

if debug: print(response.text)

deck_info = json.loads(response.text)
'''
{
    "success": true,
    "deck_id": "txllr1m8yzod",
    "remaining": 52,
    "shuffled": true
}
'''
deck_id = deck_info["deck_id"]
remaining = deck_info["remaining"]

print("You are playing with a deck identified as {} and has {} cards remaining".format(deck_id, remaining))

draw_count = 5
count = 1


url = "https://deckofcardsapi.com/api/deck/{}/draw/?count={}".format(deck_id, count)

'''
draw_count = 1
{
    "success": true,
    "deck_id": "txllr1m8yzod",
    "cards": [
        {
            "code": "5H",
            "image": "https://deckofcardsapi.com/static/img/5H.png",
            "images": {
                "svg": "https://deckofcardsapi.com/static/img/5H.svg",
                "png": "https://deckofcardsapi.com/static/img/5H.png"
            },
            "value": "5",
            "suit": "HEARTS"
        }
    ],
    "remaining": 51
}
'''
response = requests.request("GET", url, headers=headers, data=payload)

draw_info = json.loads(response.text)

print(draw_info["cards"])
print(draw_info["cards"][0])
card_info = draw_info["cards"][0]
print(card_info["code"], card_info["value"], card_info["suit"], card_info["images"]["png"], sep="\n")