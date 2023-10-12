import os

# Define the list of available languages
languages = ["english", "japanese", "hindi", "tamil", "sinhala", "french", "bangla", "chinese", "nepali", "russian", "indonesia", "marathi", "telugu", "ua", "urdu", "punjabi", "brasil", "spanish", "gujarati", "pashto"]

print("Available languages are: ", languages)

# Just for demo purpose nepali is hardcoded
# User can append/modify below list with any of the above languages
# the scraping code will run for the languages present in "languages_list"
language_names = ['nepali']

# Loop through the selected language names
for language_name in language_names:
    # Construct the path to the spider file
    lang_path = os.path.join("scrapy-code", language_name)
    for root, dirs, files in os.walk(lang_path):
        for dir in dirs:
            # check for folder with bbc as prefix
            if dir.startswith("bbc"):
                spiders_path = os.path.join(root, dir, "spiders")
                # "spiders" folder inside folder with prefix "bbc" contains the spider file
                if os.path.exists(spiders_path):
                    os.chdir(spiders_path)
                    os.system(f"scrapy runspider bbcspider.py")
