import jwt
import datetime

payload = {
    "iss": "test-key",
    "exp": datetime.datetime.now() + datetime.timedelta(hours=1)
}
token = jwt.encode(payload, "test-secret", algorithm="HS256")
print(token)