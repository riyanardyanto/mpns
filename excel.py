import json
import pprint

with open("settings_app.json", "r") as f:
    data = json.load(f)
    pprint.pprint(data)
