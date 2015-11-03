**Article Creation API**
----
  Given an source and target wiki, the API provides source articles missing in the target.

* **URL**

  http://recommend.wmflabs.org/api


  
*  **URL Params**


   **Required:**
 
  - `s=[string]` source wiki project language code (e.g. en)
  - `t=[string]` target wiki project language code (e.g. fr)

   **Optional:**
 
  - `n=[int]`  # of recommendations to fetch (default 10)
  - `article=[string]` seed for article for personalized recommendations
  - `pageviews=[true|false]` whether to include pageview counts in the response (default true)



* **Sample Call:**

  http://recommend.wmflabs.org/api?s=en&t=fr&n=3&seed=Apple

  
  ```

  {
    "articles": [
        {
            "pageviews": 233735,
            "title": "Lincoln's_Lost_Speech",
            "wikidata_id": "Q6550353"
        },
        {
            "pageviews": 120015,
            "title": "Tracking_(education)",
            "wikidata_id": "Q466845"
        },
        {
            "pageviews": 70513,
            "title": "Hillary_Clinton_presidential_campaign,_2016",
            "wikidata_id": "Q19872173"
        }
    ]
  }
  ```


*  **Running the API**

  To start the api with a small test data set, execute
  ```
  python api/recommender_api.py --translation_directions test_translation_directions.json
  ```

  Then navigate here to see the UI:
  ```
  http://localhost:5000/
  ```

  To check out the API, go to:
  ```
  http://localhost:5000/?s=test_source&t=test_target&article=Bannana
  ```

  You should get this response:

  ```
  {
    "articles": [
      {
        "pageviews": 15209,
        "title": "Bannana"
      },
      {
        "pageviews": 11726,
        "title": "Pear"
      },
      {
        "pageviews": 33621,
        "title": "Apple"
      }
    ]
  }
  ```
