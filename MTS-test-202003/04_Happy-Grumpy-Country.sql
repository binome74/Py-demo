-- Выбрать наиболее и наименее счастливые страны
SELECT
	country_cd
	,CASE grumpy_country WHEN 1 THEN 'Y' ELSE 'N' END grumpy_country
	,CASE happy_country WHEN 1 THEN 'Y' ELSE 'N' END happy_country
FROM (
	SELECT
		l.country_cd
		,rank() over (order by avg(t.tweet_sentiment) asc) grumpy_country
		,rank() over (order by avg(t.tweet_sentiment) desc) happy_country
	FROM tweet t
	INNER JOIN location l on (l.id = t.location_id)
	WHERE t.tweet_sentiment is not null
	GROUP BY l.country_cd
) as inner_q
WHERE 1 in (grumpy_country, happy_country)
;