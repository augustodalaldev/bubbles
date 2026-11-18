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

# Dog photos come per breed, so a post about a golden retriever shows a golden retriever.
# key -> Dog CEO breed path. The plain "dog" pool (any breed) is used for community art.
BREEDS = {
    "golden": "retriever/golden",
    "labrador": "labrador",
    "husky": "husky",
    "pug": "pug",
    "beagle": "beagle",
    "corgi": "corgi/cardigan",
    "poodle": "poodle/toy",
    "border": "collie/border",
    "frances": "bulldog/french",
    "chihuahua": "chihuahua",
    "shiba": "shiba",
    "dachshund": "dachshund",
    "boxer": "boxer",
    "cocker": "spaniel/cocker",
    "yorkshire": "terrier/yorkshire",
    "maltes": "maltese",
    "samoyed": "samoyed",
}


def breed_pool(breed: str) -> str:
    return f"dog:{breed}"


class WebImageProvider:
    """Real network access. Tests replace this with an in-memory fake."""

    def _get(self, url: str) -> bytes:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=15) as response:  # noqa: S310 - fixed https URLs
            return response.read(MAX_DOWNLOAD_BYTES + 1)

    def urls(self, species: str, count: int) -> list[str]:
        """`species` is a pool: "cat", "dog" (any breed) or "dog:<breed key>"."""
        urls: list[str] = []
        if species.startswith("dog"):
            path = BREEDS.get(species.partition(":")[2])
            endpoint = (
                f"https://dog.ceo/api/breed/{path}/images/random"
                if path
                else "https://dog.ceo/api/breeds/image/random"
            )
            for _ in range(8):  # random picks can repeat: ask again until there are enough
                payload = json.loads(self._get(f"{endpoint}/{min(count - len(urls) + 3, 50)}"))
                urls += [u for u in payload["message"] if u not in urls]
                if len(urls) >= count:
                    break
            return urls[:count]
        for _ in range(12):  # the cat API serves at most 10 per call without a key
            batch = json.loads(self._get("https://api.thecatapi.com/v1/images/search?limit=10"))
            urls += [item["url"] for item in batch if item["url"] not in urls]
            if len(urls) >= count:
                break
        return urls[:count]

    def download(self, url: str) -> bytes:
        data = self._get(url)
        if len(data) > MAX_DOWNLOAD_BYTES:
            raise ValueError("image too large")
        return data


class ImageLibrary:
    """Cached photo pools plus the profile pictures.

    Pools: "cat", "dog" (any breed) and "dog:<breed>". `take` hands out each photo of a pool once
    (in a fixed shuffled order) so no two posts show the same picture; `pick` is the old random
    choice used for community art.
    """

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
        self.root = Path(cache_dir)
        self.cache_dir = self.root / "images"
        self.avatar_dir = self.root / "avatars"
        self.enabled = enabled
        self.download = download
        self.per_species = per_species  # download cap per pool
        self.provider = provider or WebImageProvider()
        self.warn = warn
        self.available: dict[str, list[Path]] = {}
        self._cursor: dict[str, int] = {}

    def _folder(self, pool: str) -> Path:
        return self.cache_dir / pool.replace(":", "_").replace("/", "-")

    def prepare(self, needs: dict[str, int] | None = None) -> None:
        """Make sure each pool holds enough photos (never fails the seed).

        `needs` maps pool -> photos wanted; each is capped by `per_species`. Without it the two
        generic pools get `per_species` photos.
        """
        if not self.enabled:
            return
        wanted = {"cat": self.per_species, "dog": min(12, self.per_species)}
        for pool, count in (needs or {}).items():
            wanted[pool] = max(wanted.get(pool, 0), min(count + 2, self.per_species))
        for pool, count in wanted.items():
            folder = self._folder(pool)
            folder.mkdir(parents=True, exist_ok=True)
            files = sorted(p for p in folder.iterdir() if p.is_file())
            missing = count - len(files)
            if missing > 0 and self.download:
                try:
                    for url in self.provider.urls(pool, missing):
                        files.append(
                            self._save(folder, pool, self.provider.download(url), len(files))
                        )
                except Exception as exc:  # noqa: BLE001 - offline, rate limit, bad payload...
                    self.warn(
                        f"Could not download {pool} photos ({type(exc).__name__}: {exc}); "
                        "using the cache."
                    )
            self.available[pool] = files
            if not files:
                self.warn(f"No {pool} photos available: related content is created without images.")

    def _save(self, folder: Path, pool: str, data: bytes, index: int) -> Path:
        with Image.open(BytesIO(data)) as image:
            extension = EXTENSIONS.get(image.format or "", ".jpg")
        path = folder / f"{pool.replace(':', '_').replace('/', '-')}_{index:03d}{extension}"
        path.write_bytes(data)
        return path

    def _upload(self, path: Path):
        upload = ContentFile(path.read_bytes(), name=path.name)
        try:
            validate_image_upload(upload)  # the same rules as the API: type and 10 MB
        except ValidationError:
            return None
        return upload

    def take(self, pool: str):
        """The next unused photo of `pool` (wraps around only when the pool is exhausted)."""
        if not self.enabled:
            return None
        files = self.available.get(pool) or []
        if not files:
            return None
        order = list(files)
        random.Random(pool).shuffle(order)
        index = self._cursor.get(pool, 0)
        self._cursor[pool] = index + 1
        return self._upload(order[index % len(order)])

    def pick(self, species: str, rng: random.Random):
        """A random photo for `species` (cat, dog or both); None when unavailable."""
        if not self.enabled:
            return None
        chosen = rng.choice(SPECIES) if species == "both" else species
        pools = [p for p in sorted(self.available) if p == chosen] or [
            p for p in sorted(self.available) if p.split(":")[0] == chosen
        ]
        files = [f for p in pools for f in self.available[p]]
        if not files:
            return None
        return self._upload(rng.choice(files))

    # ------------------------------------------------------------------ profile pictures
    def avatar(self, spec: str):
        """A profile picture.

        `spec` is a file stem in `avatars/` ("spongebob"), `fish:<hue>` (the generic fish from
        `tom.png` with its colors rotated by <hue> degrees) or `bubble:<seed>` (generated).
        Missing files fall back to generated art, so the seed never breaks.
        """
        if not self.enabled:
            return None
        kind, _, arg = spec.partition(":")
        if kind == "fish":
            upload = self._fish(int(arg))
            if upload:
                return upload
            return banner_square(f"fish_{arg}")
        if kind == "bubble":
            return banner_square(arg)
        path = next((p for p in self.avatar_dir.glob(f"{spec}.*")), None)
        if path is None:
            self.warn(f"Avatar {spec!r} not found in {self.avatar_dir}; using generated art.")
            return banner_square(spec)
        return self._upload(path)

    def _fish(self, hue: int):
        path = next((p for p in self.avatar_dir.glob("tom.*")), None)
        if path is None:
            return None
        with Image.open(path) as source:
            image = source.convert("RGBA")
        alpha = image.getchannel("A")
        hsv = image.convert("RGB").convert("HSV")
        h, s, v = hsv.split()
        shift = int(hue / 360 * 255)
        h = h.point(lambda x: (x + shift) % 256)
        rgb = Image.merge("HSV", (h, s, v)).convert("RGB")
        rgb.putalpha(alpha)
        buffer = BytesIO()
        rgb.save(buffer, "PNG")
        return ContentFile(buffer.getvalue(), name=f"fish_{hue}.png")


# ---------------------------------------------------------------------------- generated art
# Wallpapers and banners are drawn offline with Pillow: the demo needs them even without network
# (and they are staff-made catalog art, not user photos).


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _bubbles(image: Image.Image, rng: random.Random, count: int) -> None:
    """Soft translucent circles, like soap bubbles."""
    from PIL import ImageDraw

    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    width, height = image.size
    for _ in range(count):
        radius = rng.randint(max(8, height // 14), max(16, height // 5))
        x, y = rng.randint(0, width), rng.randint(0, height)
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=(255, 255, 255, 46),
            outline=(255, 255, 255, 120),
            width=2,
        )
        draw.ellipse(
            (x - radius * 0.55, y - radius * 0.6, x - radius * 0.25, y - radius * 0.3),
            fill=(255, 255, 255, 110),
        )
    image.paste(layer, (0, 0), layer)


def gradient_art(
    seed: str, top: str, bottom: str, size: tuple[int, int], bubbles: int
) -> ContentFile:
    """A vertical gradient with bubbles, as a JPEG upload (`ContentFile`)."""
    rng = random.Random(seed)
    width, height = size
    (r1, g1, b1), (r2, g2, b2) = _hex_to_rgb(top), _hex_to_rgb(bottom)
    # One column of the gradient, stretched to the full width: much faster than pixel by pixel.
    column = Image.new("RGB", (1, height))
    column.putdata(
        [
            (
                int(r1 + (r2 - r1) * y / max(1, height - 1)),
                int(g1 + (g2 - g1) * y / max(1, height - 1)),
                int(b1 + (b2 - b1) * y / max(1, height - 1)),
            )
            for y in range(height)
        ]
    )
    image = column.resize((width, height))
    _bubbles(image, rng, bubbles)
    buffer = BytesIO()
    image.save(buffer, "JPEG", quality=82)
    return ContentFile(buffer.getvalue(), name=f"{seed}.jpg")


def wallpaper_image(seed: str, top: str, bottom: str, fit: str) -> ContentFile:
    """Full-page wallpaper (`cover`) or a small seamless-looking tile (`tile`)."""
    if fit == "tile":
        return gradient_art(seed, top, bottom, (180, 180), 4)
    return gradient_art(seed, top, bottom, (1280, 720), 26)


def banner_image(seed: str, top: str, bottom: str) -> ContentFile:
    return gradient_art(seed, top, bottom, (1200, 300), 14)


def banner_square(seed: str) -> ContentFile:
    """Generated 400x400 avatar (used when a character image is missing, and for the admin)."""
    rng = random.Random(seed)
    palette = [
        ("#BAE6FD", "#F5D0FE"),
        ("#BBF7D0", "#FEF9C3"),
        ("#FED7AA", "#FBCFE8"),
        ("#C7D2FE", "#A5F3FC"),
    ]
    top, bottom = rng.choice(palette)
    return gradient_art(f"avatar_{seed}", top, bottom, (400, 400), 9)
