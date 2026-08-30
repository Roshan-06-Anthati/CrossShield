from pydantic import BaseModel

class SandboxRequest(BaseModel):
    url: str