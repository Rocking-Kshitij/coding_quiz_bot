db backup done
C:\Program Files\PostgreSQL\17\bin\pg_dump.exe --file "D:\\daily project\\code_practice_chatbot\\extras\\test_db_0409.sql" --host "localhost" --port "5435" --username "data_pgvector_user" --no-password --format=c --large-objects --section=pre-data --section=data --section=post-data --verbose "ai_test_db"

findings:
    - idea of getting feedback and feedback score is not working as:
    - feedback score is already short so less tokens.
    - unpredicatable outputs like
        
        Based on the provided answer, the rating_score is:
    {
        "rating_score":"0"
    }