-- Выбрать наиболее и наименее счастливых пользователей
SELECT
	inner_q.name, tweet_text
	,CASE grumpy WHEN 1 THEN 'Y' ELSE 'N' END grumpy
	,CASE happy WHEN 1 THEN 'Y' ELSE 'N' END happy
FROM (
	SELECT
		name
		,rank() over (order by avg(tweet_sentiment) asc) grumpy
		,rank() over (order by avg(tweet_sentiment) desc) happy
	FROM tweet
	WHERE tweet_sentiment is not null
	GROUP BY name
) as inner_q
INNER JOIN tweet ON (tweet.name = inner_q.name)
WHERE 1 in (grumpy, happy)
ORDER BY inner_q.name
;