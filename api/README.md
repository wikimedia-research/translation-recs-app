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

  To start the api, execute
  ```
  python api/recommender_api.py 
  ```

  Then navigate here to see the UI:
  ```
  http://localhost:5000/
  ```

  To check out the API, go to:
  ```
  http://localhost:5000/api?s=en&t=fr&n=3&seed=Apple
  ```

  You should get the same response as above

  
