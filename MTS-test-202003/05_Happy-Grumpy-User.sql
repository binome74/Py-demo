-- Выбрать наиболее и наименее счастливых пользователей
SELECT
	name, tweet_text
	,grumpy
	,happy
	,CASE grumpy WHEN 1 THEN 'Y' ELSE 'N' END grumpy
	,CASE happy WHEN 1 THEN 'Y' ELSE 'N' END happy
FROM (
	SELECT
		name
		,tweet_text
		,rank() over (order by avg_user_sentiment asc) grumpy
		,rank() over (order by avg_user_sentiment desc) happy
	FROM (
		SELECT
			name
			,tweet_text
			,avg(tweet_sentiment) over (partition by name order by null) avg_user_sentiment
		FROM tweet
	)
	WHERE avg_user_sentiment IS NOT NULL
) as inner_q
WHERE 1 in (grumpy, happy)
ORDER BY name
;