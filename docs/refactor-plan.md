# Refactor plan

Incremental cleanup of the TodoApp architecture. Each step is planned, implemented, tested
(`pytest TodoApp/test` against the docker-compose test DB), reviewed as a diff, and committed
on its own so it can be studied in isolation.

## Done

| Step | Change | Commit |
|---|---|---|
| A | One `get_db` in `database.py`, `DbSession` alias in `dependencies.py`; tests override it once from `test/conftest.py` | `183bc1c` |
| B | Auth helpers moved out of the routers (`security.py`, `dependencies.py`); admin router guarded by a router-level `require_admin` (403); unreachable `if user is None` checks removed | `49e400b` |
| C | Pydantic models collected in `schemas.py`; `TodoResponse` / `UserResponse` response models, so `GET /users/` no longer returns `hashed_password` | `017c28d` |
| D | Typed `Settings` in `config.py` loaded from `.env`; `SECRET_KEY` rotated out of the source; token lifetime configurable; startup fails fast on missing settings | `1b633ce` |

## Next

### E: Separate pages from the API
- Cookie-based auth dependency that raises a `NotAuthenticated` exception, plus one
  `@app.exception_handler` that redirects to the login page. This replaces the bare `try/except:`
  in the page routes, which currently turns *any* error (database, template) into a login redirect.
- Move the HTML routes into `routers/pages.py` with a single `Jinja2Templates` instance
  (currently duplicated in `routers/auth.py` and `routers/todos.py`).
- Templates: `{% extends 'layout.html' %}` + `{% block content %}` instead of `{% include %}`
  (page content currently renders after `</html>`).
- Edit-todo page: filter by owner (currently any logged-in user can open any todo by id).

### F: Housekeeping
- Routes that make sync SQLAlchemy calls: `async def` → `def` (sync calls inside `async def`
  block the event loop).
- Move the test DB setup and fixtures from `test/utils.py` into `test/conftest.py`; drop
  `from .utils import *`; remove the tutorial leftover `test/test_example.py`.
- Remove unused and duplicate imports; `declarative_base()` → `sqlalchemy.orm.DeclarativeBase`.
- Deletes: `db.delete(todo_model)` instead of querying the row twice.

## Backlog (not scheduled yet)

- **Security:** registration lets anyone pick their `role`, including admin; a duplicate
  username/email gives a 500 (unhandled `IntegrityError`); emails aren't validated (`EmailStr`);
  the JWT sits in a non-HttpOnly cookie and `static/js/base.js` logs it; `base.js` reads
  `errorData.message` but FastAPI sends `detail`.
- **Database:** make Alembic the only source of the schema (baseline migration, drop the
  `create_all` calls); add `nullable=False` and a `relationship()` between `Users` and `Todos`.
- **Dependencies:** replace the unmaintained `python-jose` and `passlib` (e.g. PyJWT, pwdlib);
  pin versions in `requirements.txt`.
