http://quarry.wmflabs.org/query/794

db -e " \
SELECT im.page_title, max(im.score) FROM \
(SELECT page_title, \
CASE  \
  WHEN importance = 'Top' then 4 \
  WHEN importance = 'High' then 3 \
  WHEN importance = 'Mid' then 2 \
  WHEN importance = 'Low' then 1 \
  ELSE 0 \
END  AS score \
FROM staging.importance_classification) im \
GROUP BY im.page_title; \
" > 'importance.tsv'

hive -e \
"set mapreduce.job.queuename=priority; \
SELECT  \
page_title, \
country, \
SUM(view_count) \
FROM wmf.pageview_hourly  \
WHERE \
year = 2015 \
AND project = 'en.wikipedia' \
GROUP BY page_title, country
HAVING SUM(view_count) >= 50;" \
> enwiki_views_reduced.tsv 

set year=2015;
set month=4;
set sqoop_date=jun_19;
set clickstream_version = clickstream_v0_6;
set mapreduce.job.queuename=priority;


CREATE TABLE pagelinks_readable AS
SELECT
en_page_${hiveconf:sqoop_date}.page_title AS l_from,
en_pagelinks_${hiveconf:sqoop_date}.pl_title AS l_to
FROM en_pagelinks_${hiveconf:sqoop_date} INNER JOIN en_page_${hiveconf:sqoop_date}
ON en_pagelinks_${hiveconf:sqoop_date}.pl_from = en_page_${hiveconf:sqoop_date}.page_id;