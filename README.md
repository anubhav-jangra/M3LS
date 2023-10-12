# M3LS
Dataset and code for the paper "Large Scale Multi-lingual Multi-modal Summarization dataset".

This repository contains data and code for our EACL 2023 paper "Large Scale Multi-lingual Multi-modal Summarization dataset". Please feel free to contact me at [anubhav0603@gmail.com](mailto:anubhav0603@gmail.com) for any question.

Please cite this paper if you use our code or data.

```
@misc{verma2023large,
title={Large Scale Multi-Lingual Multi-Modal Summarization Dataset},
author={Yash Verma and Anubhav Jangra and Raghvendra Kumar and Sriparna Saha},
year={2023},
eprint={2302.06560},
archivePrefix={arXiv},
primaryClass={cs.CL}
}
```
citation bibtex will change post the conference.

## GOOGLE DRIVE LINK TO DATASET
You can access and download zipped files of various languages [here](https://drive.google.com/drive/folders/109esyywmS7iud8Fz7AK-Us21bWoVd2rx?usp=sharing).

## CODE TO WEB CRAWL DATASET
- Kindly clone the repo or download zip of the repo.
- Ensure that runscrapy.py file and scrapy-code folder are present in the same directory.
- run `python3 runscrapy.py` on terminal or the console you use run python programs

## REQUIREMENTS TO RUN CRAWLER
- `pip install scrapy==2.5.1`
- **NOTE: Scrapy 2.5.1 is compatible with Python 3.6, 3.7, 3.8, and 3.9. It is not compatible with Python 2.x.**

## runscrapy.py description

Just for demo purposes the **line11 of runscrapy.py** is set as `language_names = ['nepali']`
The user can change it to the language which he/she desires to crawl/download.

This code is written in Python and uses the Scrapy library to perform web scraping on BBC news articles for a list of languages.

The code first imports the 'os' library for file and directory manipulation. It defines a list called 'languages' containing the names of several languages. It then prints out the list of available languages.

The variable 'language_names' contains a list of selected languages for which the scraping will be performed. Currently, it contains only the name of the Nepali language, but the user can append or modify this list to include any of the languages present in the 'languages' list.

The code then loops through each language name in the 'language_names' list. For each language, it constructs a path to the directory where the scraping code is located by joining the 'scrapy-code' directory with the language name using the 'os.path.join' function.

It then searches for a directory in this path with the prefix 'bbc' using the 'os.walk' function. If it finds a directory with this prefix, it looks for a 'spiders' subdirectory within it, which contains the spider file that will perform the scraping.

If this 'spiders' directory exists, the code changes the current directory to it using the 'os.chdir' function and runs the spider file using the 'os.system' function with the command "scrapy runspider bbcspider.py". This will start the web scraping process on the BBC news articles for the selected language.