# fastapi_docker
**Hobby project** - backend for simple TODO list app hosted on [Render.com](render.com)

## 🗂️ Multitenancy

Based on [Multitenancy with FastAPI, SQLAlchemy and PostgreSQL](https://mergeboard.com/blog/6-multitenancy-fastapi-sqlalchemy-postgresql/)

Main differences: Alembic behavior. All tables are created using migrations. Each tenant schema has his own `alembic_version` table with information about current migration revision.

### 🌊 Workflow
 - FastAPI runs on each startup migration `d6ba8c13303e` (create default Tables in PG public schema if not exists)
   - Can be run manual: `alembic -x tenant=public upgrade d6ba8c13303e`

 - Create new schema (ex: `a`) and store information about it:  ``GET /create?name=a&schema=a&host=a`
 - Apply all migrations: `GET /upgrade?schema=a`
   - manual test `alembic -x dry_run=True -x tenant=a upgrade head`
   - Manual run: `alembic -x tenant=a upgrade head`

There is a `/cc/` group of endpoints which allows to: 
  - get list of all tenants
  - run migration for single tenant
  - run migrations for all tenants 

⚠️ Important - after adding a new migration rebuild of docker image is required (to copy new migration)   
### ⚗️ Alembic

Auto generating migrations (❌ - please, don't use it in this project!)
```bash
alembic revision --autogenerate -m "Add description"
```

Manual generating migrations (✅ - yes, please ☺️)

```bash
alembic revision -m "Add manual change"
```

Execute All Migrations ⏩:

```bash
alembic upgrade head
```

Migration Rollback ↩️ (by one step) 
```bash
alembic downgrade -1
```
### 🧪 Tests

To run tests locally in VS Code export environment variable first:
```bash
export PYTHONPATH=$PWD
set -a; source ./app/.env; set +a
export DB_HOST=localhost DB_PORT=5432 DB_DATABASE=pg_db DB_USERNAME=postgres DB_PASSWORD=postgres
``` 

Test execution (with code coverage):

```bash
(.venv) fastapi-multitenant-example-app$ coverage run -m pytest -v tests && coverage report -m
```

```bash
coverage html
```

Databese clean-up:
```sql
DELETE FROM public.public_users WHERE email LIKE 'faker_000_%';
DELETE FROM public.public_companies  WHERE city  LIKE 'faker_000_%';
DROP SCHEMA IF EXISTS "fake_tenant_company_for_test_00000000000000000000000000000000" CASCADE;
```

## 💾 Backup of DB (Work in Progress)

Initial Code:
``` bash
export PYTHONPATH=$PWD
cd ./commands/db_backup

```

### Usage

- List databases on a postgresql server

```bash
python3 commands/db_backup/manage_postgres_db.py --configfile sample.config --action list_dbs --verbose true
```

- Create database backup and store it (based on config file details)

```bash
python3 commands/db_backup/manage_postgres_db.py --configfile sample.config --action backup --verbose true
```

- List previously created database backups available on storage engine

```bash
python3 commands/db_backup/manage_postgres_db.py --configfile sample.config --action list --verbose true
```
- Restore previously created database backups available on storage engine (check available dates with _list_ action)

```bash
python3 commands/db_backup/manage_postgres_db.py --configfile sample.config --action restore --date "YYYY-MM-dd" --verbose true
```

- Restore previously created database backups into a new destination database

```bash
python3 commands/db_backup/manage_postgres_db.py --configfile sample.config --action restore --date "YYYY-MM-dd" --dest-db new_DB_name
```


## 🏋️‍♂️ Load test

```bash
siege --concurrent=20 --reps=5 --header="tenant:bakery_ad094154c48" --header="Authorization:Bearer 123456" https://url.com/users/
```

[ Quick and simple load testing with Apache Bench ](https://diamantidis.github.io/2020/07/15/load-testing-with-apache-bench)
```bash
ab -k -c 100 -n 5000 -H "tenant:polski_koncern_naftowy_orlen_fc26bff5f7b540d9b8d6bc68382e97a0" -H "Authorization:Bearer 24cd13a1bbf07d0cab6dcfd93ca9a1e04a339c880db21eeeeae108d6b0555cf5460ff0fa4818a41b5f125ec00e924b61c6d64f2de18c95114962120f581e7960" -v 1 https://api.url.pl/users/
```



### AB Results:


Python 3.10, Uvicorn (single instance)
settings: `ab -k -c 40 -n 5000`

```
Document Path:          /users/
Document Length:        602 bytes

Concurrency Level:      40
Time taken for tests:   343.097 seconds
Complete requests:      5000
Failed requests:        0
Keep-Alive requests:    0
Total transferred:      5685000 bytes
HTML transferred:       3010000 bytes
Requests per second:    14.57 [#/sec] (mean)
Time per request:       2744.776 [ms] (mean)
Time per request:       68.619 [ms] (mean, across all concurrent requests)
Transfer rate:          16.18 [Kbytes/sec] received

```

### Pydantic V2
`ab -k -c 40 -n 5000`

slower than previous?

```
Document Path:          /users/
Document Length:        602 bytes

Concurrency Level:      40
Time taken for tests:   303.484 seconds
Complete requests:      5000
Failed requests:        0
Keep-Alive requests:    0
Total transferred:      5685000 bytes
HTML transferred:       3010000 bytes
Requests per second:    16.48 [#/sec] (mean)
Time per request:       2427.872 [ms] (mean)
Time per request:       60.697 [ms] (mean, across all concurrent requests)
Transfer rate:          18.29 [Kbytes/sec] received

```

#### async branch:

Test branch for async code:

```
Document Path:          /users/
Document Length:        337 bytes

Concurrency Level:      100
Time taken for tests:   159.392 seconds
Complete requests:      5000
Failed requests:        0
Keep-Alive requests:    0
Total transferred:      4480000 bytes
HTML transferred:       1685000 bytes
Requests per second:    31.37 [#/sec] (mean)
Time per request:       3187.839 [ms] (mean)
Time per request:       31.878 [ms] (mean, across all concurrent requests)
Transfer rate:          27.45 [Kbytes/sec] received
```

Probably above `30` Requests per second comparing to `20` - `25` in sync version 