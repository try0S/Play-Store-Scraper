# Post Quantum TLS for Android

https://eprint.iacr.org/2023/734

## Play Store Scraper

Scrapes the app IDs from the various Google Play categories.

### Install

1. Install Firefox

2. Download Gecko Drivers and place them in `PATH`
    https://github.com/mozilla/geckodriver/releases

3. Usage example can be found in launcher.ipynb

## Graph Generator

Creates graph from .pcap files showing the number of client hellos, resumptions and repeatedly accessed servers.
After the first execution, three .json files are created as an intermediate step. 
In further executions, the graphs are generated from the data in the json files to skip the time-consuming pcap parsing.