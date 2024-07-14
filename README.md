# Sonic Channel Scraper

Mass download Sonic Channel Wallpapers

## Installation

Install with `pip install sonic-channel-scraper` or with `poetry install`.

## Usage

```text
usage: sonic_channel_scraper [-h] [-p PAGES] [--tar] [--pc | --mobile] [-c CHARACTER] dir

positional arguments:
  dir                   Directory to save into.

options:
  -h, --help            show this help message and exit
  -p PAGES, --pages PAGES
  --tar                 Save all images into .tar.gz archive.
  --pc                  Download only PC wallpapers.
  --mobile              Download only mobile wallpapers.
  -c CHARACTER, --character CHARACTER
                        Filter for character. Can be repeated for multiple.
```
