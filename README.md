# Sonic Channel Scraper

Mass download Sonic Channel files.

## Installation

Install with `pip install sonic-channel-scraper` or with `poetry install`.

## Usage

```text
usage: sonic_channel_scraper [-h] (--all | --wallpaper | --icon | --calendar | --coloring | --papercraft | --letterset) [--tar] [-c CHARACTER] [--pc | --mobile] dir

positional arguments:
  dir                   Directory to save into.

options:
  -h, --help            show this help message and exit

Types:
  --all                 Scrape all resource types.
  --wallpaper           Scrape wallpapers.
  --icon                Scrape icons.
  --calendar            Scrape calendar pages.
  --coloring            Scrape coloring pages.
  --papercraft          Scrape papercraft sets.
  --letterset           Scrape lettering sets.

Options:
  --tar                 Save all images into .tar.gz archive.
  -c CHARACTER, --character CHARACTER
                        Filter for character. Can be repeated for multiple.
  --pc                  Download only PC wallpapers.
  --mobile              Download only mobile wallpapers.
```
