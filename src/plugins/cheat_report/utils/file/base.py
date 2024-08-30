import httpx
from enum import Enum


class FileSaverType(Enum):
    LOCAL = "local"
    COS = "cos"


class FileSaver:
    type: FileSaverType
    resource_root_url: str

    def __init__(self, resource_root_url: str, type: FileSaverType):
        self.resource_root_url = resource_root_url
        self.type = type
        self.resource_type_suffices = {
            "image": ["jpg", "jpeg", "png", "gif"],
            "video": ["mp4"],
            "reply": ["reply"]
        }
        self.resource_types = list(self.resource_type_suffices.keys())
        self.resource_suffix_to_type = {suffix: resource_type for resource_type, suffixes in
                                        self.resource_type_suffices.items() for suffix in suffixes}

    def get_file_save_path(self, name: str) -> str:
        resource_name, resource_suffix = name.split(".")
        resource_type = self.resource_suffix_to_type.get(resource_suffix)
        resource_name += f".{resource_type}"

        save_path = f"{resource_type}s/{resource_name}"
        return save_path

    async def save_file(self, name: str, url: str) -> str:
        content = url.encode("utf-8")
        if url.startswith("http"):
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(url)
            content = response.content
        save_path = self.get_file_save_path(name)
        await self._save_file(content=content,
                              save_path=save_path)
        return f"{self.resource_root_url}/{save_path}"

    async def _save_file(self, content: bytes, save_path: str):
        pass
