To start the api with a small test data set, execute
```
cd translation-recs-app/api
python recommender_api.py
```

Then navigate to:
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
