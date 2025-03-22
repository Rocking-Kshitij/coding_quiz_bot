select * from skills order by skillid;
select * from questionbank order by question_id

select distinct subject from skills;

select * from skills where performance > 0;

-- Update skills
-- set performance = 0, updated_at = current_timestamp

SELECT count(*) FROM pg_stat_activity;

SELECT pid, state, application_name, client_addr, backend_start 
FROM pg_stat_activity;

SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'ai_test_db' 
AND pid!=40;


SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'ai_test_db';


-- check query last
SELECT pid, query, state, backend_start, query_start, application_name 
FROM pg_stat_activity
 order by backend_start desc
