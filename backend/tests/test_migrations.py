from peewee import SqliteDatabase

from migrations.runner import Migration, apply_migrations, discover_migrations


def test_apply_migrations_runs_pending_migration_and_records_it(tmp_path):
    db = SqliteDatabase(str(tmp_path / "test.db"))
    calls = []

    def up(database, migrator):
        calls.append("up")
        database.execute_sql("CREATE TABLE sample (id INTEGER PRIMARY KEY)")

    migration = Migration(name="0001_sample", up=up)

    apply_migrations(db, [migration])

    assert calls == ["up"]
    assert "sample" in db.get_tables()
    assert "etir_migrations" in db.get_tables()
    db.close()


def test_apply_migrations_skips_already_applied_migration(tmp_path):
    db = SqliteDatabase(str(tmp_path / "test.db"))
    calls = []

    def up(database, migrator):
        calls.append("up")

    migration = Migration(name="0001_sample", up=up)

    apply_migrations(db, [migration])
    apply_migrations(db, [migration])

    assert calls == ["up"]
    db.close()


def test_apply_migrations_runs_in_filename_order(tmp_path):
    db = SqliteDatabase(str(tmp_path / "test.db"))
    calls = []

    def make_up(name):
        def up(database, migrator):
            calls.append(name)

        return up

    migrations = [
        Migration(name="0001_first", up=make_up("first")),
        Migration(name="0002_second", up=make_up("second")),
    ]

    apply_migrations(db, migrations)

    assert calls == ["first", "second"]
    db.close()


def test_discover_migrations_finds_initial_migration():
    names = [migration.name for migration in discover_migrations()]

    assert "0001_initial" in names


def test_project_migration_creates_project_table(tmp_path):
    db = SqliteDatabase(str(tmp_path / "test.db"))
    migration = next(
        m for m in discover_migrations() if m.name == "0002_project"
    )

    apply_migrations(db, [migration])

    assert "project" in db.get_tables()
    columns = {column.name for column in db.get_columns("project")}
    assert columns == {
        "project_id",
        "project_name",
        "project_status",
        "users_count",
    }
    db.close()


def test_user_migration_creates_user_table(tmp_path):
    db = SqliteDatabase(str(tmp_path / "test.db"))
    migrations = [
        migration
        for migration in discover_migrations()
        if migration.name in {"0002_project", "0003_user"}
    ]

    apply_migrations(db, migrations)

    assert "user" in db.get_tables()
    columns = {column.name for column in db.get_columns("user")}
    assert columns == {"user_id", "project_id", "fname", "lname"}
    foreign_keys = db.get_foreign_keys("user")
    assert any(fk.column == "project_id" for fk in foreign_keys)
    db.close()


def test_user_credentials_migration_adds_email_and_password_hash(tmp_path):
    db = SqliteDatabase(str(tmp_path / "test.db"))
    migrations = [
        migration
        for migration in discover_migrations()
        if migration.name in {"0002_project", "0003_user", "0004_user_credentials"}
    ]

    apply_migrations(db, migrations)

    columns = {column.name for column in db.get_columns("user")}
    assert {"email", "password_hash"} <= columns
    db.close()


def test_seed_migration_creates_qa1_project(tmp_path):
    db = SqliteDatabase(str(tmp_path / "test.db"))
    migrations = [
        migration
        for migration in discover_migrations()
        if migration.name in {"0002_project", "0005_seed_qa1_project"}
    ]

    apply_migrations(db, migrations)

    rows = list(
        db.execute_sql(
            "SELECT project_name, project_status, users_count FROM project"
        )
    )
    assert rows == [("qa1", "active", 0)]
    db.close()
