"""Cat and dog photos for the demo data, downloaded once and cached on disk.

Sources (free, no API key): The Cat API and the Dog CEO API. Photos are saved in a git-ignored
cache directory and reused by later runs; with no network the seed falls back to the cache, or
to no images at all (with a clear warning).
"""

import json
import random
import urllib.request
from collections.abc import Callable
from io import BytesIO
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image

from apps.core.uploads import validate_image_upload

SPECIES = ("cat", "dog")
MAX_DOWNLOAD_BYTES = 8 * 1024 * 1024
USER_AGENT = "bubbles-demo-seed"
EXTENSIONS = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp", "GIF": ".gif"}


class WebImageProvider:
    """Real network access. Tests replace this with an in-memory fake."""

    def _get(self, url: str) -> bytes:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=15) as response:  # noqa: S310 - fixed https URLs
            return response.read(MAX_DOWNLOAD_BYTES + 1)

    def urls(self, species: str, count: int) -> list[str]:
        if species == "dog":
            payload = json.loads(
                self._get(f"https://dog.ceo/api/breeds/image/random/{min(count, 50)}")
            )
            return list(payload["message"])
        urls: list[str] = []
        while len(urls) < count:  # the cat API serves at most 10 per call without a key
            batch = json.loads(
                self._get(
                    f"https://api.thecatapi.com/v1/images/search?limit={min(count - len(urls), 10)}"
                )
            )
            urls.extend(item["url"] for item in batch)
        return urls

    def download(self, url: str) -> bytes:
        data = self._get(url)
        if len(data) > MAX_DOWNLOAD_BYTES:
            raise ValueError("image too large")
        return data


class ImageLibrary:
    def __init__(
        self,
        cache_dir: Path,
        *,
        enabled: bool = True,
        download: bool = True,
        per_species: int = 12,
        provider=None,
        warn: Callable[[str], None] = print,
    ):
        self.cache_dir = Path(cache_dir) / "images"
        self.enabled = enabled
        self.download = download
        self.per_species = per_species
        self.provider = provider or WebImageProvider()
        self.warn = warn
        self.available: dict[str, list[Path]] = {s: [] for s in SPECIES}

    def prepare(self) -> None:
        """Make sure the cache holds enough photos; never fails the seed."""
        if not self.enabled:
            return
        for species in SPECIES:
            folder = self.cache_dir / species
            folder.mkdir(parents=True, exist_ok=True)
            files = sorted(p for p in folder.iterdir() if p.is_file())
            missing = self.per_species - len(files)
            if missing > 0 and self.download:
                try:
                    for url in self.provider.urls(species, missing):
                        files.append(
                            self._save(folder, species, self.provider.download(url), len(files))
                        )
                except Exception as exc:  # noqa: BLE001 - offline, rate limit, bad payload...
                    self.warn(
                        f"Could not download {species} photos ({type(exc).__name__}: {exc}); "
                        "using the cache."
                    )
            self.available[species] = [p for p in files if p is not None]
            if not self.available[species]:
                self.warn(
                    f"No {species} photos available: related content is created without images."
                )

    def _save(self, folder: Path, species: str, data: bytes, index: int) -> Path:
        with Image.open(BytesIO(data)) as image:
            extension = EXTENSIONS.get(image.format or "", ".jpg")
        path = folder / f"{species}_{index:03d}{extension}"
        path.write_bytes(data)
        return path

    def pick(self, species: str, rng: random.Random):
        """A fresh, validated upload for `species` (cat, dog or both); None when unavailable."""
        if not self.enabled:
            return None
        chosen = rng.choice(SPECIES) if species == "both" else species
        files = self.available.get(chosen) or []
        if not files:
            return None
        path = rng.choice(files)
        upload = ContentFile(path.read_bytes(), name=path.name)
        try:
            validate_image_upload(upload)  # the same rules as the API: type and 10 MB
        except ValidationError:
            return None
        return upload
