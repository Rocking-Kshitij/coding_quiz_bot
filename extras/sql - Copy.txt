select * from skills order by skillid limit 1;
select * from questionbank order by created_at desc limit 1

select * from questionbank where is_asked = false

select skills.subject, count(questionbank.skillid) from questionbank join skills on questionbank.skillid = skills.skillid
where questionbank.is_asked = false group by skills.subject

select skills.subject, count(questionbank.question_id), avg(skills.performance)  from questionbank join skills on questionbank.skillid = skills.skillid
where skills.performance > 0 group by skills.subject

select skills.subject, count(questionbank.question_id)  from questionbank join skills on questionbank.skillid = skills.skillid
where questionbank.is_asked = false group by skills.subject




select distinct subject from skills;
select * from skills where performance >0 order by performance desc
select * from skills order by subject

select * from skills where content IS NOT NULL
ALTER TABLE skills RENAME COLUMN "Content" TO content;
select * from subject_importance

select * from skills where performance > 0 order by performance desc;

select avg(performance) from skills;
select subject, avg(performance) from skills group by subject;

Update skills
set performance = 0, updated_at = current_timestamp

update questionbank
set is_asked = true


--check activity
-- SELECT count(*) FROM pg_stat_activity;

SELECT pid, state, application_name, client_addr, backend_start 
FROM pg_stat_activity;

-- SELECT pg_terminate_backend(pid) 
-- FROM pg_stat_activity 
-- WHERE datname = 'ai_test_db' 
-- AND pid!=40;


-- SELECT pg_terminate_backend(pid) 
-- FROM pg_stat_activity 
-- WHERE datname = 'ai_test_db';


-- check query last
SELECT pid, query, state, backend_start, query_start, application_name 
FROM pg_stat_activity
 order by backend_start desc

 --update constraints
-- SELECT conname
-- FROM pg_constraint 
-- WHERE conrelid = 'Skills'::regclass;


-- SELECT conname
-- FROM pg_constraint
-- WHERE conrelid = 'QuestionBank'::regclass;


-- ALTER TABLE Skills DROP CONSTRAINT skills_performance_check;

-- ALTER TABLE Skills ADD CONSTRAINT skills_performance_check CHECK (performance BETWEEN 0 AND 100);

alter table questionbank
add column is_asked boolean default false;
