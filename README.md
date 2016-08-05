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
  - `article=[string]` seed article for personalized recommendations. Can be a list of seeds seperated by |
  - `pageviews=[true|false]` whether to include pageview counts in the response (default true)
  - `search=[wiki|google|morelike]` which search algorithm to use (default morelike)



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


*  **Running the API**

  To start the api, execute
  ```
  python api/api.py 
  ```

  Then navigate here to see the UI:
  ```
  http://localhost:5000/
  ```

  To check out the API, go to:
  ```
  http://localhost:5000/api?s=en&t=fr&n=3&article=Apple
  ```

  You should get the same response as above

  
