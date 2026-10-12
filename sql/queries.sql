
-- 1. Overall request count and token consumption
SELECT
    COUNT(*) AS total_requests,
    SUM(total_tokens) AS total_tokens,
    ROUND(AVG(latency_ms), 2) AS avg_latency_ms
FROM llm_usage;

-- 2. Success and failure counts by model
SELECT
    model,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) AS successes,
    SUM(CASE WHEN status = 'failure' THEN 1 ELSE 0 END) AS failures
FROM llm_usage
GROUP BY model;

-- 3. Daily usage
SELECT
    date,
    COUNT(*) AS requests,
    SUM(total_tokens) AS total_tokens
FROM llm_usage
GROUP BY date
ORDER BY date;

-- 4. Rank users by token consumption
SELECT
    user_id,
    SUM(total_tokens) AS total_tokens,
    RANK() OVER (ORDER BY SUM(total_tokens) DESC) AS usage_rank
FROM llm_usage
GROUP BY user_id;
