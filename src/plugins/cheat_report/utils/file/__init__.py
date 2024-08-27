from .cos import CosFileSaver
from .local import LocalFileSaver
from .base import FileSaver, FileSaverType


file_saver_dict = {
    FileSaverType.LOCAL: LocalFileSaver,
    FileSaverType.COS: CosFileSaver
}


def get_file_saver(file_saver_type: str,
                   resource_root_url: str,
                   **kwargs) -> FileSaver:
    return file_saver_dict[FileSaverType(file_saver_type)](resource_root_url, **kwargs)