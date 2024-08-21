"""Sonic Channel Scraper."""

import argparse
import tarfile
from concurrent.futures import Future, ProcessPoolExecutor, ThreadPoolExecutor
from itertools import chain
from pathlib import Path
from urllib.parse import urlparse

import bs4
import requests

MAX_THREADS = 16

BASE_URL = "https://sonic.sega.jp"
LIST_URL = BASE_URL + "/SonicChannel/enjoy/"

session = requests.session()


def arg_dir(p: str) -> Path:
    """Validate argparse dir path."""
    path = Path(p)
    try:
        path.mkdir(exist_ok=True)
    except FileExistsError as e:
        raise ValueError("Provided path is not a directory.") from e
    return path


parser = argparse.ArgumentParser()

parser.add_argument("dir", type=arg_dir, help="Directory to save into.")

types_group = parser.add_argument_group(title="Types")
types = types_group.add_mutually_exclusive_group(required=True)

types.add_argument(
    "--all",
    action="store_const",
    const="",
    dest="type",
    help="Scrape all resource types.",
)
types.add_argument(
    "--wallpaper",
    action="store_const",
    const="wallpaper/",
    dest="type",
    help="Scrape wallpapers.",
)
types.add_argument(
    "--icon",
    action="store_const",
    const="icon/",
    dest="type",
    help="Scrape icons.",
)
types.add_argument(
    "--calendar",
    action="store_const",
    const="calendar/",
    dest="type",
    help="Scrape calendar pages.",
)
types.add_argument(
    "--coloring",
    action="store_const",
    const="coloring/",
    dest="type",
    help="Scrape coloring pages.",
)
types.add_argument(
    "--papercraft",
    action="store_const",
    const="papercraft/",
    dest="type",
    help="Scrape papercraft sets.",
)
types.add_argument(
    "--letterset",
    action="store_const",
    const="letterset/",
    dest="type",
    help="Scrape lettering sets.",
)

options = parser.add_argument_group(title="Options")

archives = options.add_mutually_exclusive_group()

archives.add_argument(
    "--tar",
    action="store_true",
    help="Save all images into .tar.gz archive.",
)

options.add_argument(
    "-c",
    "--character",
    action="append",
    help="Filter for character. Can be repeated for multiple.",
)

wallpaper_types = options.add_mutually_exclusive_group()

wallpaper_types.add_argument(
    "--pc",
    action="store_true",
    help="Download only PC wallpapers.",
)
wallpaper_types.add_argument(
    "--mobile",
    action="store_true",
    help="Download only mobile wallpapers.",
)


args = parser.parse_args()


def get_page(page: int = 1) -> bytes:
    """Get content of page.

    Args:
        page (int): Page to get. Defaults to 1.

    Returns:
        bytes: Content of page.
    """
    index = f"index_{page}.html" if page != 1 else "index.html"
    res: requests.Response = session.get(LIST_URL + args.type + index)
    res.raise_for_status()
    return res.content


def get_image_urls(page: bytes) -> list[str]:
    """Get all images URLs in page.

    Args:
        page (bytes): Page content in bytes.

    Returns:
        list[str]: List of all image URLs found.
    """
    bs = bs4.BeautifulSoup(page, "html.parser")
    results = bs.find_all(name="a", class_="enjoyDownload", href=True)
    return [BASE_URL + result.get("href") for result in results]


def download_image(path: Path, url: str) -> Path:
    """Download image from url to provided path.

    Args:
        path (Path): Path to output dir
        url (str): URL of image to download

    Returns:
        Path: Path of saved image
    """
    res = session.get(url)
    res.raise_for_status()
    filename = Path(urlparse(url).path).name
    with open(path / filename, "w+b") as f:
        f.write(res.content)
    return path / filename


def main():
    """Main."""
    pages = []

    def _save_future(future: Future):
        if future.done():
            pages.append(future.result())

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as exc:
        page = 1
        while True:
            try:
                future = exc.submit(get_page, page)
                exception = future.exception()
                if exception is not None:
                    raise exception
            except requests.HTTPError as e:
                if e.response.status_code == 404:
                    break
            future.add_done_callback(_save_future)
            page += 1
    with ProcessPoolExecutor() as exc:
        res = exc.map(get_image_urls, pages)
    urls = chain.from_iterable(res)
    filtered = []
    for url in urls:
        name = Path(urlparse(url).path).stem
        if args.pc or args.mobile:
            suffix = "pc" if args.pc else "sp"
            if not name.endswith(suffix):
                continue
        if args.character:
            if not any(character in name for character in args.character):
                continue
        filtered.append(url)
    print(f"Downloading {len(filtered)} images.")

    def _download(url: str):
        download_image(args.dir, url)

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as exc:
        exc.map(_download, filtered)
    if args.tar:
        with tarfile.open(f"{args.dir.name}.tar.gz", "w:gz") as tar:
            tar.add(args.dir, arcname=args.dir.name)
        print(f"tar.gz file saved in {args.dir.name}.tar.gz")
    print("✨All done!✨")


if __name__ == "__main__":
    main()
