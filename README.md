# fastapi_docker
**Hobby project** - backend for simple TODO list app hosted on AWS cloud

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
### Alembic

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

## 🏋️‍♂️Load test

```bash
siege --concurrent=20 --reps=5 --header="tenant:bakery_ad094154c48" --header="Authorization:Bearer 123456" https://url.com/users/
```

[ Quick and simple load testing with Apache Bench ](https://diamantidis.github.io/2020/07/15/load-testing-with-apache-bench)
```bash
ab -k -c 100 -n 5000 -H "tenant:polski_koncern_naftowy_orlen_fc26bff5f7b540d9b8d6bc68382e97a0" -H "Authorization:Bearer 24cd13a1bbf07d0cab6dcfd93ca9a1e04a339c880db21eeeeae108d6b0555cf5460ff0fa4818a41b5f125ec00e924b61c6d64f2de18c95114962120f581e7960" -v 1 https://api.url.pl/users/
```



### AB Results:

Python 3.10, Uvicorn (single instance)
settings: `ab -k -c 100 -n 5000`

```
Document Path:          /users/
Document Length:        337 bytes

Concurrency Level:      100
Time taken for tests:   195.826 seconds
Complete requests:      5000
Failed requests:        0
Keep-Alive requests:    0
Total transferred:      4480000 bytes
HTML transferred:       1685000 bytes
Requests per second:    25.53 [#/sec] (mean)
Time per request:       3916.515 [ms] (mean)
Time per request:       39.165 [ms] (mean, across all concurrent requests)
Transfer rate:          22.34 [Kbytes/sec] received


```

```
Document Path:          /users/
Document Length:        337 bytes

Concurrency Level:      100
Time taken for tests:   261.628 seconds
Complete requests:      5000
Failed requests:        382
   (Connect: 0, Receive: 0, Length: 382, Exceptions: 0)
Non-2xx responses:      382
Keep-Alive requests:    0
Total transferred:      10132516 bytes
HTML transferred:       7336924 bytes
Requests per second:    19.11 [#/sec] (mean)
Time per request:       5232.569 [ms] (mean)
Time per request:       52.326 [ms] (mean, across all concurrent requests)
Transfer rate:          37.82 [Kbytes/sec] received

```