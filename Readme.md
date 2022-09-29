# fastapi_docker
Backend for simple TODO list app hosted on AWS cloud

## Multitenancy

Based on [Multitenancy with FastAPI, SQLAlchemy and PostgreSQL](https://mergeboard.com/blog/6-multitenancy-fastapi-sqlalchemy-postgresql/)

Main differences: Alembic behavior. All tables are created using migrations. Each tenant schema has his own `alembic_version` table with information about current migration revision.

### Workflow
 - FastAPI runs on each startup migration `d6ba8c13303e` (create default Tables in PG public schema if not exists)
   - Can be run manual: `alembic -x tenant=public upgrade d6ba8c13303e`

 - Create new schema (ex: `a`) and store information about it:  ``GET /create?name=a&schema=a&host=a`
 - Apply all migrations: `GET /upgrade?schema=a`
   - manual test `alembic -x dry_run=True -x tenant=a upgrade head`
   - Manual run: `alembic -x tenant=a upgrade head`

### Load test
```bash
siege --concurrent=20 --reps=5 --header="tenant:v2_6c0ad5866ea249d78abd861625eca82a" http://url.com/
```

```bash
ab -k -c 100 -n 5000 -H "tenant:polski_koncern_naftowy_orlen_fc26bff5f7b540d9b8d6bc68382e97a0" -H "Authorization:Bearer 24cd13a1bbf07d0cab6dcfd93ca9a1e04a339c880db21eeeeae108d6b0555cf5460ff0fa4818a41b5f125ec00e924b61c6d64f2de18c95114962120f581e7960" -v 1 https://api.url.pl/users/
```



Wyniki:

`Uvicorn, Debug`

```
	"transactions":			         200,
	"availability":			      100.00,
	"elapsed_time":			        1.87,
	"data_transferred":		        0.00,
	"response_time":		        0.17,
	"transaction_rate":		      106.95,
	"throughput":			        0.00,
	"concurrency":			       17.71,
	"successful_transactions":	         100,
	"failed_transactions":		           0,
	"longest_transaction":		        0.37,
	"shortest_transaction":		        0.06

```



### Alembic

Auto generating migrations (❌ - please, don't use in this project!)
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

### pyTest
```bash
(.venv) fastapi-multitenant-example-app$ coverage run -m pytest -v tests && coverage report -m
```

```bash
coverage html
```

### Postgres

```sql
CREATE TABLE shared.shared_users (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    email varchar(256) UNIQUE NOT NULL,  
    tenant_id int NOT NULL,
	is_active bool NOT NULL DEFAULT false,
    created_at timestamptz NOT NULL DEFAULT timezone('utc', now()),
    updated_at timestamptz
);
```



```sql
CREATE TABLE tenant_default.users (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    email varchar(256) UNIQUE,  
    first_name varchar(100),
    last_name varchar(100),
    user_role_id int,
    created_at timestamptz,
    updated_at timestamptz
);

CREATE TABLE tenant_default.permissions (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    uuid uuid UNIQUE,
    account_id int,
    name varchar(100),
    title varchar(100),
    description varchar(100)
);


CREATE TABLE tenant_default.roles (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    role_name varchar(100),
    role_description varchar(100)
);

CREATE TABLE tenant_default.roles_permissions_link (
    role_id int,
    permission_id int,
    PRIMARY KEY(role_id, permission_id)
);

ALTER TABLE tenant_default.roles_permissions_link ADD CONSTRAINT roles_permissions_link_fk FOREIGN KEY (permission_id) REFERENCES tenant_default.permissions(id);
ALTER TABLE tenant_default.roles_permissions_link ADD CONSTRAINT roles_permissions_link_fk_1 FOREIGN KEY (role_id) REFERENCES tenant_default.roles(id);
ALTER TABLE tenant_default.users ADD CONSTRAINT role_FK FOREIGN KEY (user_role_id) REFERENCES tenant_default.roles(id);
```

