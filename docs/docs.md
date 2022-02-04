# fastapi_docker
## Configuration


Poetry:
```
poetry config virtualenvs.in-project true
```

export do pliku requirements.txt:
```bash
poetry export -f requirements.txt --output requirements.txt
```

## Tests

Code coverage:
```
coverage run -m pytest -v tests && coverage report -m

coverage run -m pytest tests
coverage report
coverage html
```

## Performance tests:
```
sudo siege -t10S -c100 0.0.0.0:5000
```

## Authorization

Simple token stored in DB, queried each time from Database.





## DB Tables:

Users:
```sql
CREATE TABLE users (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    uuid uuid,
    client_id int,
    password varchar(256) NOT NULL,
    email varchar(256) UNIQUE,
    phone varchar(16) UNIQUE,    
    first_name varchar(100),
    last_name varchar(100),
    auth_token varchar(128),
    auth_token_valid_to timestamptz,
    is_active boolean NOT NULL,
    is_mail_valid boolean NOT NULL,
    is_phone_valid boolean NOT NULL,
    qr_id varchar(100),
    service_token varchar(100),
    service_token_valid_to timestamptz,
    tz varchar(64) NOT NULL,
    lang varchar(8) NOT NULL,
    user_role_id int,
    tos boolean,
    deleted_at timestamptz,
    created_at timestamptz,
    updated_at timestamptz
);

```

LoginHistory:
```sql
CREATE TABLE login_history (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    client_id int,
    login_date timestamptz NOT NULL,
    ip_address varchar(16),
    user_agent varchar(256),
    os varchar(32),
    browser varchar(32),
    browser_lang varchar(32),
    ipinfo json,
    failed boolean NOT NULL,
    failed_login varchar(256),
    failed_passwd varchar(256)
);

```

Files:

```sql
CREATE TABLE files (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    uuid uuid,
    client_id int,
    owner_id int,
    file_name varchar(256),
    file_id varchar(256),
    extension varchar(8),
    mimetype varchar(256),
    size int,
    deleted_at timestamptz,
    created_at timestamptz,
    updated_at timestamptz
);

```
Tasks:

```sql
CREATE TABLE tasks (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    uuid uuid,
    client_id int,
    author_id int,
    title varchar(128),
    description varchar(256),
    date_from timestamptz,
    date_to timestamptz,
    priority varchar(128),
    type varchar(128),
    connected_tasks int,
    deleted_at timestamptz,
    created_at timestamptz,
    updated_at timestamptz
);
```


Comments:

```sql
CREATE TABLE comments (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    uuid uuid,
    client_id int,
    message varchar(256),
);
```

Tasks files link
```sql
CREATE TABLE task_files_link (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    task_id int,
    file_id int,
);
```

Tasks persons link
```sql
CREATE TABLE task_person_link (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    task_id int,
    person_id int,
);
```