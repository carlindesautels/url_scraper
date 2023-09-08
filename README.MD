This code will scrape the url that is inputed via the urls.json file.  To run the code you need to run:
```pip install -r requirements.txt```
Then run:
```playwright install```

Once scraped it will save the output to an html file (will change to .gz) under a directory named for the url.  A sub-directory will be timestamped when the scraper is run.  The html file will be saved there.

