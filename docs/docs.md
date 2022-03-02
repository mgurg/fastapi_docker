# fastapi_docker
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
    uuid: uuid.UUID
    # author_id: int
    assignee_id: Optional[int]
    title: str
    description: str
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    duration: Optional[int]
    is_active: Optional[bool]
    priority: str
    type: str
    tasks_fk: Optional[UserIndexResponse] # nazwa taka jak relacji, nie musi być to taka sama nazwa jak nazwa w BD 
```



---





### Users:

Tabela z użytkownikami

```sql
CREATE TABLE users (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    uuid uuid UNIQUE,
    client_id int,
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

### LoginHistory:

Historia logowań (niepoprawnych i udanych)

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

### Files:

Tablica z plikami.

```sql
CREATE TABLE files (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    uuid uuid UNIQUE,
    client_id int,
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

  * 



```sql
CREATE TABLE tasks (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    uuid uuid UNIQUE,
    client_id int,
    author_id int,
    assignee_id int,
    title varchar(128),
    description varchar(256),   
    event_id int,
    duration int,
    is_active boolean,
    priority varchar(128),
    type varchar(128),
    connected_tasks int,
    date_from timestamptz, 	-- needed?
    date_to timestamptz, 	-- neded?
    time_from time with time zone NULL;
    time_to time with time zone NULL;
    all_day bool NULL;
    recurring bool NULL;
    deleted_at timestamptz,
    created_at timestamptz,
    updated_at timestamptz
);

ALTER TABLE public.tasks ADD CONSTRAINT tasks_assignee_fk FOREIGN KEY (assignee_id) REFERENCES public.users(id);
ALTER TABLE public.tasks ADD CONSTRAINT task_event_fk FOREIGN KEY (event_id) REFERENCES events(id);

```



### Events:

Da powtarzających się zadań: 

  * *Reminder Count*  - The maximum number of reminders that can be triggered for the event.
  * *Reminder Interval*  - The reminder interval.
  * *Reminder Unit* - The reminder unit to identify the reminder interval in minutes, hours, or days.
  * *Created At* - It stores the date and time at which the event is created.
  * *Updated At*  - It stores the date and time at which the event is updated.
  * *Scheduled At* -It stores the date and time on the Calendar.
  * *Triggered At* - It stores the date and time at which the event was triggered.
  * *Content* - The column used to store the event content.

Predefiniowane tryby:

- Codziennie
- Codzinnie Pon - Pt
- Co tydzień, czwartek
- Co miesiąc 3.XX
- Co roku 3.02.XXX



Pola:

- recurring
- start_at - data rozpoczęcia
- ends_at - data zakończenia
- interval - liczba jednostek
- at_Mo
- at_Tu
- at_We
- at_Th
- at_Fr
- at_Sa
- at_Su
- all_day
- duration




```sql
CREATE TABLE events (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    uuid uuid UNIQUE,
    client_id int,
    recurring boolean, 
	interval int,  	-- The reminder interval.
	unit varchar(8), -- The reminder unit to identify the reminder interval in minutes, hours, or days.
    at_Mo boolean, 	-- The reminder days (single): Monday
    at_Tu boolean, 	-- The reminder days (single): Tuesday
    at_We boolean, 	-- The reminder days (single): Wednesday
    at_Th boolean, 	-- The reminder days (single): Thursday
    at_Fr boolean, 	-- The reminder days (single): Friday
    at_Sa boolean, 	-- The reminder days (single): Saturday
    at_Su boolean, 	-- The reminder days (single): Sunday
	start_at timestamptz, 	-- It stores the date and time at which the event is created.
    whole_day boolean,
    end_type varchar(8),		-- None, date, after n occurences
    ends_at timestamptz,
    reminder_count int  		-- The maximum number of reminders that can be triggered for the event.
    );
    
 	content -- The column used to store the event content.
    scheduled_at timestamptz, 	-- It stores the date and time on the Calendar.
	triggered_at timestamptz, 	-- It stores the date and time at which the event was triggered.
     	updated_at timestamptz,  	-- It stores the date and time at which the event is updated.

```





Comments:

```sql
CREATE TABLE comments (
    id int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    uuid uuid UNIQUE,
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