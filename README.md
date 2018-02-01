# Image scraper for Flickr using Multiprocessing in Python
Python library to scrape images in parallel from Flickr based on given list of locations like rome, paris and so on.
It extracts the filename and geo information about the images and inserts into SQLite database. In case of missing geo
information, it uses GoogleMaps API to extract this information based on the generic location (example, paris) that was
searched.

# Requirements
1. [Python3](https://www.python.org/downloads/release/python-364/)
2. [Pip3: python3 get-pip.py](https://bootstrap.pypa.io/get-pip.py)
3. API keys: Get the Flickr and GoogleMaps API keys from below links and insert it into scrape-flickr/config.py
    * [Flickr API keys](https://www.flickr.com/services/api/misc.api_keys.html)
    * [GoogleMaps API key](https://developers.google.com/maps/documentation/geocoding/get-api-key)


# SQLite database
The following tables get created in this code:
1. __image_metadata:__ used to store image information such as filename and geo information and consists of following fields:
    * id: unique image id
    * filename: title of the image
    * latitude: latitude of the location in the image
    * longitude: longitude of the location in the image
2. __default_geo_info:__ used to store missing geo information of images using GoogleMaps API
    * search_text: location that was searched on Flickr
    * latitude: latitude of the location
    * longitude: longitude of the location

# Running the code (Note: Please run all of these commands from project directory py-scrape-flickr)
This code is tested on Mac and Windows 10.
1. Run the shell script which creates a virtual environment named scraper and installs the needed python packages

        sh setup.sh

2. Activate virtualenv, if not activated already

        . scraper/bin/activate

3. Run the code from the project directory py-scrape-flickr

        python scrape-flickr/scrape_flickr.py paris rome "new york" [--photos_per_page] [-h]

   It takes the following arguments:
    * list of locations each separated by space and put double quotes around locations containing space
    * optional --photos_per_page: number of photos to be retrieved at same time (max=500)
    * optional -h: check usage

   The database scraper.db gets created in the project folder (py-scrape-flickr) when running it for the first time.

4. Check results

        sqlite3 scraper.db
        select * from image_metadata;

5. Time in minutes for various input sizes on a 4 processors system
    * 3 locations: 16 mins
    * 6 locations: 60 mins
    * 10 locations: 104 mins

   This time will vary depending on what locations were searched and how many images they have and also on the number of
   processors on the system and how strong is the internet connection.

6. Run unit tests

        python -m unittest discover scrape-flickr/

# References
[Multiprocessing](https://docs.python.org/3/library/multiprocessing.html)

[Sub-processes in multiprocessing](https://stackoverflow.com/a/8963618)

[Flickr Photos Search](https://www.flickr.com/services/api/flickr.photos.search.html)

[GoogleMaps Geocoding](https://developers.google.com/maps/documentation/geocoding/intro)
