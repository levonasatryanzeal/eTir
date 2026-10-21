def up(database, migrator):
    database.execute_sql(
        "INSERT INTO project (project_name, project_status, users_count) "
        "SELECT 'qa1', 'active', 0 "
        "WHERE NOT EXISTS ("
        "SELECT 1 FROM project WHERE project_name = 'qa1'"
        ")"
    )
