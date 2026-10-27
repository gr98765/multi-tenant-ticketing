"""Tables must not be readable through a database-level API (e.g. Supabase)."""
from sqlalchemy import text

from app.database import Base, engine
from app.main import enable_row_level_security


def test_row_level_security_enabled_on_every_table(client):
    # the client fixture starts the app, which runs the startup hook
    names = [t.name for t in Base.metadata.sorted_tables]
    with engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT relname, relrowsecurity FROM pg_class WHERE relname = ANY(:n)"
        ), {"n": names}).all()
    assert {name for name, on in rows if on} == set(names)


def test_rls_blocks_other_roles_but_not_the_app(client):
    client.post("/auth/signup", json={"email": "a@a.com", "password": "pw123456",
                                      "organization_name": "A"})
    with engine.begin() as conn:
        conn.execute(text("DROP ROLE IF EXISTS api_visitor"))
        conn.execute(text("CREATE ROLE api_visitor"))
        conn.execute(text("GRANT SELECT ON users TO api_visitor"))
        conn.execute(text("SET LOCAL ROLE api_visitor"))
        visible = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
        conn.execute(text("RESET ROLE"))
        conn.execute(text("REVOKE ALL ON users FROM api_visitor"))
        conn.execute(text("DROP ROLE api_visitor"))
    assert visible == 0  # like Supabase's public API key: sees nothing
    me = client.post("/auth/login", data={"username": "a@a.com", "password": "pw123456"})
    assert me.status_code == 200  # the app itself still works


def test_enabling_twice_is_safe(client):
    enable_row_level_security()
    enable_row_level_security()