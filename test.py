import base64
import json

with open('cookies.json', 'r') as f:
    data = json.load(f)

encoded_cookie = base64.b64encode(json.dumps(data).encode()).decode()

# Then paste encoded_cookie into your secrets.toml
print(encoded_cookie)
