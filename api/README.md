**Article Creation API**
----
  Given an source and target wiki, the API provides source articles missing in the target.

* **URL**

  http://recommend.wmflabs.org/api


  
*  **URL Params**


   **Required:**
 
   `s=[string]` source wiki project language code (e.g. en)
   `t=[string]` target wiki project language code (e.g. fr)

   **Optional:**
 
   `n=[int]`  # of recommendations to fetch (default 10)
   `article=[string]` seed for article for personalized recommendations
   `pageviews=[true|false]` whether to include pageview counts in the response (default true)


* **Success Response:**
  
  <_What should the status code be on success and is there any returned data? This is useful when people need to to know what their callbacks should expect!_>

  * **Code:** 200 <br />
    **Content:** `{ articles : [{"wikidata_id": "Q1", "pageviews": 233735, "title": "Universe"}, ] }`
 


* **Sample Call:**

  http://recommend.wmflabs.org/api?s=en&t=fr&n=3&seed=Apple

  {"articles": [{"wikidata_id": "", "pageviews": 3221, "title": "Mutsu_(apple)"}, {"wikidata_id": "", "pageviews": 127, "title": "Liveland_Raspberry_apple"}, {"wikidata_id": "", "pageviews": 91, "title": "Eva_(apple)"}]}


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
