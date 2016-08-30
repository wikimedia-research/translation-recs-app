[![Build Status](https://travis-ci.org/wikimedia-research/translation-recs-app.svg?branch=master)](https://travis-ci.org/wikimedia-research/translation-recs-app)

**Article Creation API**
----
  Given a source and target wiki, the API provides source articles missing in the target.

* **URL**
  * http://recommend.wmflabs.org/api  
* **URL Params**
  * **Required:** 
    * `s=[string]` source wiki project language code (e.g. `en`)
    * `t=[string]` target wiki project language code (e.g. `fr`)
  * **Optional:**
    * `n=[int]` number of recommendations to fetch (default `10`)
    * `article=[string]` seed article for personalized recommendations. Can be a list of 
      seeds separated by `|`
    * `pageviews=[true|false]` whether to include pageview counts in the response (default `true`)
    * `search=[wiki|google|morelike]` which search algorithm to use (default `morelike`)
* **Sample Call:**

  http://recommend.wmflabs.org/api?s=en&t=fr&n=3&article=Apple

  ```
  {
    "articles": [
        {
            "pageviews": 3221,
            "title": "Mutsu_(apple)",
            "wikidata_id": "Q2613423"
        },
        {
            "pageviews": 127,
            "title": "Liveland_Raspberry_apple",
            "wikidata_id": "Q19597760"
        },
        {
            "pageviews": 91,
            "title": "Eva_(apple)",
            "wikidata_id": "Q5414989"
        }
    ]
  }
  ```

* **Running the API**

  There is a `wsgi` file provided at `recommendation/data/recommendation.wsgi`. This can be run
  using a tool like `uwsgi` as follows:
  ```
  # Inside a virtualenv and in the root directory of the repo
  pip install -e .
  pip install uwsgi
  uwsgi --http :5000 --wsgi-file recommendation/data/recommendation.wsgi --venv my-venv
  ```

  Then navigate here to see the UI:
  ```
  http://localhost:5000/
  ```

  To check out the API, go to:
  ```
  http://localhost:5000/api?s=en&t=fr&n=3&article=Apple
  ```

  You should get a similar response to the **Sample Call** above
