from pydantic_settings import BaseSettings
from pydantic import SecretStr, Field
from typing import List

class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    ADMINS: str  
    GROUP_ID: str
    CHANNEL: str
    
    @property
    def admin_list(self) -> list[int]:
        return [int(x.strip()) for x in self.ADMINS.split(',') if x.strip()]
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'ignore'

config = Settings()