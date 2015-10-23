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
