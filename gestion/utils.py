"""便利関数とか"""
import base64
import uuid
import json


class Token():
    """アクセストークン.
    仕様: 以下のJSONオブジェクトをbase64エンコードしたもの
    {"user_id": <int:user_id>, "group_id": <int:group_id>, "token": <int:token>}
    """
    def __init__(self, raw_token):
        try:
            token_seed = json.loads(base64.b64decode(raw_token).decode())
            self.user_id = token_seed['user_id']
            self.group_id = token_seed['group_id']
            self.token = token_seed['token']
        except:
            raise Exception('不正なトークン形式です')

    def update(self):
        self.token = self.generate_token()

    def tokenize(self):
        return self.generate(self.user_id, self.group_id)

    @staticmethod
    def generate_token():
        """アクセストークンの生成."""
        # return base64.b64encode(uuid.uuid4().bytes).decode()
        return uuid.uuid4().int

    @classmethod
    def generate(cls, user_id, group_id):
        token_seed = {
            'user_id': user_id,
            'group_id': group_id,
            'token': cls.generate_token(),
        }
        return base64.b64encode(json.dumps(token_seed).encode()).decode()
