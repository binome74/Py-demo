-- Выбрать наиболее и наименее счастливые локации
SELECT
	name, country_cd
	,CASE grumpy_location WHEN 1 THEN 'Y' ELSE 'N' END grumpy_location
	,CASE happy_location WHEN 1 THEN 'Y' ELSE 'N' END happy_location
FROM (
	SELECT
		l.name, l.country_cd
		,rank() over (order by avg(t.tweet_sentiment) asc) grumpy_location
		,rank() over (order by avg(t.tweet_sentiment) desc) happy_location
	FROM tweet t
	INNER JOIN location l on (l.id = t.location_id)
	WHERE t.tweet_sentiment is not null
	GROUP BY t.location_id
) as inner_q
WHERE 1 in (grumpy_location, happy_location)
;
