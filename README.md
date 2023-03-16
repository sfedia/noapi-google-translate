# No-API Google Translate
* Provides the ability to translate .html documents with Google Translate without using the Google Translate API.
* lxml, Selenium and Chromium Webdriver are required
## Pipeline and usage
1. To translate a document, first simplify the XML-structure of the document:
```bash
python3 html_simplifier.py
```
2. Then run the translate script:
```bash
python3 google_translate.py
```
I don't recommend to change the default parameters, but increasing `workers_count` could potentially increase the translation speed.
3. Translate script will produce multiple files, which are parts of the original document translated in parallel by different threads. They need to be merged in one file:
```bash
python3 merge_translations.py
```
So, finally you get, for example, `mydocument-merged.html`, which is the translated version of your original document.
