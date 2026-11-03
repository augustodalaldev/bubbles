import uuid
from pathlib import PurePath

from django.utils.deconstruct import deconstructible


@deconstructible
class UploadTo:
    """`upload_to` callable that stores files as `<folder>/<random uuid><ext>`.

    A class (not a closure) so migrations can serialize it. The original filename
    is discarded: it may be hostile (path tricks) or leak personal information.
    """

    def __init__(self, folder: str):
        self.folder = folder

    def __call__(self, instance, filename: str) -> str:
        extension = PurePath(filename).suffix.lower()
        return f"{self.folder}/{uuid.uuid4().hex}{extension}"
