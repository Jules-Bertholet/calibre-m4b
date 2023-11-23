from datetime import date
import io

from calibre.customize import MetadataReaderPlugin
from calibre.ebooks.metadata.book.base import Metadata
from PIL import Image
from .tinytag import TinyTag


class ReadM4BMetadata(MetadataReaderPlugin):
    name = "Read M4B Metadata"
    description = "Read metadata from M4b files"
    supported_platforms = [
        "windows",
        "osx",
        "linux",
    ]  # Platforms this plugin will run on
    author = "Jules Bertholet"  # The author of this plugin
    version = (1, 0, 0)  # The version number of this plugin
    file_types = {"m4b"}  # The file types that this plugin will be applied to
    on_postprocess = True  # Run this plugin after conversion is complete
    minimum_calibre_version = (7, 0, 0)

    def get_metadata(self, stream, type) -> Metadata:
        tag = TinyTag.get(file_obj=stream, image=True)
        title = tag.title
        if tag.album is not None:
            album_title = tag.album.strip().rstrip(" (Unabridged)")
            if title is None or len(album_title) > len(title):
                title = album_title

        meta = Metadata(title)
        if tag.artist is not None and tag.artist.strip() != "":
            meta.authors = tag.artist.split(", ")
        elif tag.albumartist is not None and tag.albumartist.strip() != "":
            meta.authors = tag.albumartist.split(", ")

        if tag.year is not None:
            meta.pubdate = date(int(tag.year), 1, 1)
        image_bytes = tag.get_image()
        if image_bytes is not None:
            image = Image.open(io.BytesIO(image_bytes))
            if image.format is not None:
                format = image.format.lower()
                meta.cover_data = (format, image_bytes)
        if tag.extra is not None and "copyright" in tag.extra:
            meta.rights = tag.extra["copyright"]
        if tag.genre is not None:
            meta.tags = tuple(tag.genre.split(", "))
        meta.comments = tag.comment

        return meta
