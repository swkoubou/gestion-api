"""便利関数とか"""
import base64
import uuid


def generate_token():
    """アクセストークンの生成."""
    return base64.b64encode(uuid.uuid4().bytes).decode()
