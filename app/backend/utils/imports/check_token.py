import base64
import json
import time

def decode_jwt_payload(jwt_token: str):
    # JWT format: header.payload.signature
    try:
        payload_part = jwt_token.split('.')[1]
        
        # Add missing padding if needed
        rem = len(payload_part) % 4
        if rem > 0:
            payload_part += '=' * (4 - rem)

        decoded_bytes = base64.urlsafe_b64decode(payload_part)
        payload = json.loads(decoded_bytes)
        return payload
    except Exception as e:
        print("Error decoding token:", e)
        return None

def is_token_valid(jwt_token: str):
    payload = decode_jwt_payload(jwt_token)
    if not payload:
        return False

    current_time = int(time.time())
    iat = payload.get("iat")
    exp = payload.get("exp")

    print(f"Issued at: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(iat))}")
    print(f"Expires at: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(exp))}")
    print(f"Current UTC time: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(current_time))}")

    if iat <= current_time <= exp:
        print("✅ Token is still valid.")
        return True
    else:
        print("❌ Token has expired or is not yet valid.")
        return False
