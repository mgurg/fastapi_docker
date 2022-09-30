# fastapi_docker

## Naming

Tables: plural (Multiple users are listed in the users table.)
  - Users
  - Ideas

Models: singular (A singular user can be selected from the users table.)
  - User
  - Idea

Controllers: plural (http://myapp.com/users would list multiple users.)



## Configuration


Poetry, tworzenie środowiska wirtualnego w obrębie projektu:
```bash
poetry config virtualenvs.in-project true
```

Eksport do pliku *requirements.txt*:
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

Flake check

```
flake8 ./app --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

## Performance tests:
```
sudo siege -t10S -c100 0.0.0.0:5000
```

## Authorization

Simple token stored in DB, queried each time from Database.

### Docker

```bash
docker ps
docker exec -it 64a05bfedffb sh

```

### Status
 - pending
 - rejected
 - new
 - accepted
 - cancelled


### Events

```json
  events: [
                {
                    id: 1,
                    title: '1st of the Month',
                    details: 'Everything is funny as long as it is happening to someone else',
                    start: '2022-03-01',
                    end: '2022-03-01',
                    bgcolor: 'orange'
                },
                {
                    id: 2,
                    title: 'Sisters Birthday',
                    details: 'Buy a nice present',
                    start: getCurrentDay(4),
                    end: getCurrentDay(4),
                    bgcolor: 'green',
                    icon: 'fas fa-birthday-cake'
                },
                {
                    id: 3,
                    title: 'Meeting',
                    details: 'Time to pitch my idea to the company',
                    start: getCurrentDay(10),
                    end: getCurrentDay(10),
                    time: '10:00',
                    duration: 120,
                    bgcolor: 'red',
                    icon: 'fas fa-handshake'
                },
                {
                    id: 4,
                    title: 'Lunch',
                    details: 'Company is paying!',
                    start: getCurrentDay(10),
                    end: getCurrentDay(10),
                    time: '11:30',
                    duration: 90,
                    bgcolor: 'teal',
                    icon: 'fas fa-hamburger'
                },
                {
                    id: 5,
                    title: 'Visit mom',
                    details: 'Always a nice chat with mom',
                    start: getCurrentDay(20),
                    end: getCurrentDay(20),
                    time: '17:00',
                    duration: 90,
                    bgcolor: 'grey',
                    icon: 'fas fa-car'
                },
                {
                    id: 6,
                    title: 'Conference',
                    details: 'Teaching Javascript 101',
                    start: getCurrentDay(22),
                    end: getCurrentDay(22),
                    time: '08:00',
                    duration: 540,
                    bgcolor: 'blue',
                    icon: 'fas fa-chalkboard-teacher'
                },
                {
                    id: 7,
                    title: 'Girlfriend',
                    details: 'Meet GF for dinner at Swanky Restaurant',
                    start: getCurrentDay(22),
                    end: getCurrentDay(22),
                    time: '19:00',
                    duration: 180,
                    bgcolor: 'teal',
                    icon: 'fas fa-utensils'
                },
                {
                    id: 8,
                    title: 'Rowing',
                    details: 'Stay in shape!',
                    start: getCurrentDay(27),
                    end: getCurrentDay(28),
                    bgcolor: 'purple',
                    icon: 'rowing'
                },
                {
                    id: 9,
                    title: 'Fishing',
                    details: 'Time for some weekend R&R',
                    start: getCurrentDay(22),
                    end: getCurrentDay(29),
                    bgcolor: 'purple',
                    icon: 'fas fa-fish'
                },
                {
                    id: 10,
                    title: 'Vacation',
                    details: 'Trails and hikes, going camping! Don\'t forget to bring bear spray!',
                    start: getCurrentDay(22),
                    end: getCurrentDay(29),
                    bgcolor: 'purple',
                    icon: 'fas fa-plane'
                }
            ]
        }
```



## DB Tables:



Kopia bazy danych:

```
pg_dump -h [host address] -Fc -o -U [database user] <database name> > [dump file]
```

```
pg_dumpall -U myuser -h 67.8.78.10 --clean --file=mydb_backup.dump
pg_dump --dbname=postgresql://username:password@127.0.0.1:5432/mydatabase
```



### Alembic

Utowrzenie poczatkowej migracji z bazy danych

```
alembic revision --autogenerate -m "Initial"
alembic upgrade head
```



---



Relacje pomiędzy tabelami `1:1` (Users & Task):

Tabela `Tasks` ma powiązanie (`author_id`) do tabeli `Users` skąd pobieram dodatkowe dane o użytkowniku. Ustalenie relacji w DB: 

![FK](./img/FK_Tasks_Users.png)

```sql
ALTER TABLE public.tasks ADD CONSTRAINT tasks_fk FOREIGN KEY (author_id) REFERENCES public.users(id);

ALTER TABLE public.tasks ADD CONSTRAINT tasks_assignee_fk FOREIGN KEY (assignee_id) REFERENCES public.users(id);

```

Modyfikacja modeli

`Tasks`:

```python
    author_id: Optional[int] = Field(default=None, foreign_key="users.id") # kolumna w tabeli Tasks
    tasks_fk: Optional[Users] = Relationship(back_populates="usr_FK") # relacja 
```



`Users`:

```python
usr_FK: List["Tasks"] = Relationship(back_populates="tasks_fk")
```

Listowanie wyników razem z relacjami

```python
class TaskIndexResponse(SQLModel):
    uuid: UUID
    # author_id: int
    assignee_id: Optional[int]
    title: str
    description: str
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    duration: Optional[int]
    is_active: Optional[bool]
    priority: str
    mode: str
    tasks_fk: Optional[UserIndexResponse] # nazwa taka jak relacji, nie musi być to taka sama nazwa jak nazwa w BD 
```



---





### Users:

Tabela z użytkownikami

```sql
CREATE TABLE users (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    uuid uuid UNIQUE,
    account_id int,
    password varchar(256) NOT NULL,
    email varchar(256) UNIQUE,
    phone varchar(16) UNIQUE,    
    first_name varchar(100),
    last_name varchar(100),
    auth_token varchar(128),
    auth_token_valid_to timestamptz,
    is_active boolean NOT NULL,
    is_mail_valid boolean NOT NULL DEFAULT FALSE,
    is_phone_valid boolean NOT NULL DEFAULT FALSE,
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

Uprawnienia:

```sql
CREATE TABLE permissions (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    uuid uuid UNIQUE,
    account_id int,
    name varchar(100),
    title varchar(100),
    description varchar(100),
    deleted_at timestamptz,
    created_at timestamptz,
    updated_at timestamptz
);


CREATE TABLE roles (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    uuid uuid UNIQUE,
    account_id int,
    role_name varchar(100),
    role_description varchar(100),
    hidden int,
    deleted_at timestamptz,
    created_at timestamptz,
    updated_at timestamptz
);

CREATE TABLE roles_permissions_link (
    role_id int,
    permission_id int,
    PRIMARY KEY(role_id, permission_id)
);

ALTER TABLE public.task_files_link ADD CONSTRAINT task_files_link_fk FOREIGN KEY (task_id) REFERENCES public.tasks(id);
ALTER TABLE public.task_files_link ADD CONSTRAINT task_files_link_fk_1 FOREIGN KEY (file_id) REFERENCES public.files(id);


-- USERS:
ALTER TABLE public.users ADD CONSTRAINT role_FK FOREIGN KEY (user_role_id) REFERENCES public.roles(id);



```



### LoginHistory:

Historia logowań (niepoprawnych i udanych)

```sql
CREATE TABLE login_history (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    account_id int,
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

### Files:

Tablica z plikami.

```sql
CREATE TABLE files (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    uuid uuid UNIQUE,
    account_id int,
    owner_id int,
    file_name varchar(256),
    extension varchar(8),
    mimetype varchar(256),
    size int,
    deleted_at timestamptz,
    created_at timestamptz,
    updated_at timestamptz
);

CREATE TABLE task_files_link (
    task_id int,
    file_id int,
    PRIMARY KEY(task_id, file_id)
);

ALTER TABLE public.task_files_link ADD CONSTRAINT task_files_link_fk FOREIGN KEY (task_id) REFERENCES public.tasks(id);
ALTER TABLE public.task_files_link ADD CONSTRAINT task_files_link_fk_1 FOREIGN KEY (file_id) REFERENCES public.files(id);


```



Powiązanie Files <-> Tasks

```python
class TaskFileLink(SQLModel, table=True):
    task_id: Optional[int] = Field(default=None, foreign_key="task.id", primary_key=True)
    file_id: Optional[int] = Field(default=None, foreign_key="file.id", primary_key=True)
```



### Tasks:

Lista wszystkich zadań.



```sql
CREATE TABLE tasks (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    uuid uuid UNIQUE,
    account_id int,
    author_id int,
    assignee_id int,
    title varchar(256),
    description text NULL,
    color varchar(8),
    date_from timestamptz, 	-- needed?
    date_to timestamptz NULL, 	-- neded?
    time_from time with time zone NULL;
    time_to time with time zone NULL;
    duration int NULL,
    recurring bool NOT NULL DEFAULT 0;
    all_day bool NOT NULL DEFAULT 1;
    is_active boolean,
    priority varchar(32),
    mode varchar(128),  
    deleted_at timestamptz,
    created_at timestamptz,
    updated_at timestamptz
);

ALTER TABLE public.tasks ADD CONSTRAINT tasks_assignee_fk FOREIGN KEY (assignee_id) REFERENCES public.users(id);
-- ALTER TABLE public.tasks ADD CONSTRAINT task_event_fk FOREIGN KEY (event_id) REFERENCES events(id);

```

task_duration:

```sql
CREATE TABLE task_duration (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    uuid uuid UNIQUE,
    start_at timestamptz,
    end_at timestamptz,
    duration int
    );
```

### Ideas

```sql
CREATE TABLE ideas (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    uuid uuid UNIQUE,
    account_id int,
    author_id int,
    upvotes int,
    downvotes int,
    title varchar(256),
    description text NULL,
    color varchar(8),
    created_at timestamptz,
    updated_at timestamptz,
    deleted_at timestamptz
);

CREATE TABLE ideas_files_link (
    idea_id int,
    file_id int,
    PRIMARY KEY(idea_id, file_id)
);

ALTER TABLE public.ideas_files_link ADD CONSTRAINT ideas_files_link_fk FOREIGN KEY (idea_id) REFERENCES public.ideas(id);
ALTER TABLE public.ideas_files_link ADD CONSTRAINT ideas_files_link_fk_1 FOREIGN KEY (file_id) REFERENCES public.files(id);

CREATE TABLE ideas_votes (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    uuid uuid
    account_id int,
    idea_id int,
    user_id int,
    vote varchar(16),
    created_at timestamptz,
);

```



### Events:

Da powtarzających się zadań, predefiniowane tryby:

- Codziennie
- Codzinnie Pon - Pt
- Co tydzień, czwartek
- Co miesiąc 3.XX
- Co roku 3.02.XXX




```sql
CREATE TABLE events (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    uuid uuid UNIQUE,
    account_id int,
    freq varchar(8), -- The reminder unit to identify the reminder interval in minutes, hours, or days.
    interval int(4),  	-- The reminder interval.
    date_from timestamptz, 		-- needed?
    date_to timestamptz NULL, 	-- neded?
    occurrence_number: int NULL,
    recurring bool NOT NULL DEFAULT 0;
    all_day bool NOT NULL DEFAULT 1;
    time_from time with time zone NULL;
    time_to time with time zone NULL;
    duration int NULL,
    at_Mo boolean, 	-- The reminder days (single): Monday
    at_Tu boolean, 	-- The reminder days (single): Tuesday
    at_We boolean, 	-- The reminder days (single): Wednesday
    at_Th boolean, 	-- The reminder days (single): Thursday
    at_Fr boolean, 	-- The reminder days (single): Friday
    at_Sa boolean, 	-- The reminder days (single): Saturday
    at_Su boolean, 	-- The reminder days (single): Sunday
    );
    

```

```
CREATE TABLE task_events_link (
    task_id int,
    event_id int,
    PRIMARY KEY(task_id, event_id)
);

ALTER TABLE public.task_events_link ADD CONSTRAINT task_events_link_fk FOREIGN KEY (task_id) REFERENCES public.tasks(id);
ALTER TABLE public.task_events_link ADD CONSTRAINT task_events_link_fk_1 FOREIGN KEY (event_id) REFERENCES public.events(id);

class TaskEventLink(SQLModel, table=True):
    task_id: Optional[int] = Field(default=None, foreign_key="task.id", primary_key=True)
    event_id: Optional[int] = Field(default=None, foreign_key="event.id", primary_key=True)
```





### Comments:

```sql
CREATE TABLE comments (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    uuid uuid UNIQUE,
    user_id int,
    message varchar(256),
);
```



```sql
CREATE TABLE task_comments_link (
    task_id int,
    comment_id int,
    PRIMARY KEY(task_id, file_id)
);

ALTER TABLE public.task_comments_link ADD CONSTRAINT task_comments_link_fk FOREIGN KEY (task_id) REFERENCES public.tasks(id);
ALTER TABLE public.task_comments_link ADD CONSTRAINT task_comments_link_fk_1 FOREIGN KEY (comment_id) REFERENCES public.comments(id);
```



---



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

### Settings:

```sql
CREATE TABLE settings (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    account_id int,
    entity varchar(64),
    value varchar(64),
    value_type varchar(64),
    created_at timestamptz,
    updated_at timestamptz
);
```

