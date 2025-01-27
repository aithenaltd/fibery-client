import os

from dotenv import load_dotenv


class FiberyConfig:
    def __init__(
        self,
        token: str | None = None,
        account : str | None = None,
    ):
        load_dotenv()
        self.token = token or os.getenv('FIBERY_TOKEN')
        self.account = account or os.getenv('FIBERY_ACCOUNT')

        if not self.token or not self.account:
            raise ValueError('FIBERY_TOKEN and FIBERY_ACCOUNT must be set in .env file or passed as arguments')

        self.base_url = f'https://{self.account}.fibery.io'
        self.headers = {
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json'
        }
