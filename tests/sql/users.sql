-- public schema

CREATE TABLE public.public_users (
	id int4 GENERATED BY DEFAULT AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE) NOT NULL,
	"uuid" uuid NOT NULL,
	first_name varchar(100) NULL,
	last_name varchar(100) NULL,
	email varchar(256) NULL,
	phone varchar(16) NULL,
	"password" varchar(256) NULL,
	service_token varchar(256) NULL,
	service_token_valid_to timestamptz NULL,
	is_active bool NOT NULL,
	is_verified bool NOT NULL,
	tos bool NOT NULL,
	tenant_id varchar(64) NULL,
	tz varchar(64) NULL,
	lang varchar(8) NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	updated_at timestamptz NULL,
	deleted_at timestamptz NULL,
	CONSTRAINT public_users_pkey PRIMARY KEY (id),
	CONSTRAINT public_users_uuid_key UNIQUE (uuid)
);
CREATE INDEX public_users_tenant_id_idx ON public.public_users USING btree (tenant_id);


CREATE TABLE public.public_companies (
	id int4 GENERATED BY DEFAULT AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE) NOT NULL,
	"uuid" uuid NULL,
	"name" varchar(256) NULL,
	short_name varchar(256) NULL,
	nip varchar(16) NULL,
	city varchar(128) NULL,
	street varchar(256) NULL,
	country varchar(128) NULL,
	tenant_id varchar(64) NULL,
	qr_id varchar(32) NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	updated_at timestamptz NULL,
	deleted_at timestamptz NULL,
	CONSTRAINT public_companies_pkey PRIMARY KEY (id),
	CONSTRAINT public_companies_qr_id_key UNIQUE (qr_id),
	CONSTRAINT public_companies_tenant_id_key UNIQUE (tenant_id),
	CONSTRAINT public_companies_uuid_key UNIQUE (uuid)
);

INSERT INTO public.public_companies ("uuid","name",short_name,nip,city,street,country,tenant_id,qr_id,created_at,updated_at,deleted_at) VALUES
	 ('05eab889-2bea-4db1-8c3f-f73222e073ee','string','string','9542752600','string',NULL,'pl','string_05eab8892bea4db18c3ff73222e073ee','epm','2023-07-14 13:33:55.645',NULL,NULL);

INSERT INTO public.public_users ("uuid",first_name,last_name,email,phone,"password",service_token,service_token_valid_to,is_active,is_verified,tos,tenant_id,tz,lang,created_at,updated_at,deleted_at) VALUES
	 ('59e49dd8-efb0-4201-b767-607257fd13de','string','string','user@example.com',NULL,NULL,NULL,NULL,true,true,true,'string_05eab8892bea4db18c3ff73222e073ee','Europe/Warsaw','pl','2023-07-14 13:33:55.867',NULL,NULL),
	 ('94ca4f7e-e4ae-4921-8758-94e672fe201d','Maciej','Nowak','maciej.xx@gmail.com',NULL,NULL,NULL,NULL,true,true,true,'string_05eab8892bea4db18c3ff73222e073ee','Europe/Warsaw','pl','2023-11-14 18:37:56.832','2023-11-21 16:35:11.449',NULL);


-- fake_tenant_company_for_test_00000000000000000000000000000000.users definition

-- Drop table

-- DROP TABLE fake_tenant_company_for_test_00000000000000000000000000000000.users;
CREATE SCHEMA fake_tenant_company_for_test_00000000000000000000000000000000;

CREATE TABLE fake_tenant_company_for_test_00000000000000000000000000000000.roles
(
    id               int4 GENERATED BY DEFAULT AS IDENTITY ( INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE) NOT NULL,
    "uuid"           uuid                                                                                                            NOT NULL,
    is_custom        bool                                                                                                            NULL,
    is_visible       bool                                                                                                            NULL,
    is_system        bool                                                                                                            NULL,
    role_name        varchar(100)                                                                                                    NOT NULL,
    role_title       varchar(100)                                                                                                    NOT NULL,
    role_description varchar(100)                                                                                                    NULL,
    created_at       timestamptz                                                                                                     NULL,
    updated_at       timestamptz                                                                                                     NULL,
    deleted_at       timestamptz                                                                                                     NULL,
    CONSTRAINT role_title_key UNIQUE NULLS NOT DISTINCT (role_title, deleted_at),
    CONSTRAINT roles_pkey PRIMARY KEY (id)
);
CREATE INDEX ix_roles_uuid ON fake_tenant_company_for_test_00000000000000000000000000000000.roles USING btree (uuid);


CREATE TABLE fake_tenant_company_for_test_00000000000000000000000000000000.users
(
    id                     int4 GENERATED BY DEFAULT AS IDENTITY ( INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE) NOT NULL,
    "uuid"                 uuid                                                                                                            NOT NULL,
    email                  varchar(256)                                                                                                    NOT NULL,
    phone                  varchar(16)                                                                                                     NULL,
    "password"             varchar(256)                                                                                                    NULL,
    tos                    bool                                                                                                            NULL,
    first_name             varchar(100)                                                                                                    NULL,
    last_name              varchar(100)                                                                                                    NULL,
    user_role_id           int4                                                                                                            NULL,
    auth_token             varchar(128)                                                                                                    NULL,
    auth_token_valid_to    timestamptz                                                                                                     NULL,
    is_active              bool                                                                                                            NOT NULL,
    is_verified            bool                                                                                                            NOT NULL,
    is_visible             bool                                                                                                            NULL,
    service_token          varchar(100)                                                                                                    NULL,
    service_token_valid_to timestamptz                                                                                                     NULL,
    tz                     varchar(64)                                                                                                     NOT NULL,
    lang                   varchar(8)                                                                                                      NOT NULL,
    tenant_id              varchar(64)                                                                                                     NULL,
    created_at             timestamptz                                                                                                     NULL,
    updated_at             timestamptz                                                                                                     NULL,
    deleted_at             timestamptz                                                                                                     NULL,
    CONSTRAINT users_auth_token_key UNIQUE (auth_token),
    CONSTRAINT users_pkey PRIMARY KEY (id),
    CONSTRAINT users_service_token_key UNIQUE (service_token),
    CONSTRAINT role_fk FOREIGN KEY (user_role_id) REFERENCES fake_tenant_company_for_test_00000000000000000000000000000000.roles (id)
);
CREATE INDEX ix_users_uuid ON fake_tenant_company_for_test_00000000000000000000000000000000.users USING btree (uuid);



CREATE TABLE fake_tenant_company_for_test_00000000000000000000000000000000.permissions
(
    id          int4 GENERATED BY DEFAULT AS IDENTITY ( INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE) NOT NULL,
    "uuid"      uuid                                                                                                            NOT NULL,
    "name"      varchar(100)                                                                                                    NULL,
    title       varchar(100)                                                                                                    NULL,
    description varchar(100)                                                                                                    NULL,
    is_visible  bool                                                                                                            NULL,
    "group"     varchar(100)                                                                                                    NULL,
    CONSTRAINT permissions_pkey PRIMARY KEY (id),
    CONSTRAINT permissions_uuid_key UNIQUE (uuid)
);
CREATE INDEX ix_permissions_uuid ON fake_tenant_company_for_test_00000000000000000000000000000000.permissions USING btree (uuid);

CREATE TABLE fake_tenant_company_for_test_00000000000000000000000000000000.roles_permissions_link
(
    role_id       int4 GENERATED BY DEFAULT AS IDENTITY ( INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE) NOT NULL,
    permission_id int4                                                                                                            NOT NULL,
    CONSTRAINT roles_permissions_link_pkey PRIMARY KEY (role_id, permission_id),
    CONSTRAINT roles_permissions_link_fk FOREIGN KEY (permission_id) REFERENCES fake_tenant_company_for_test_00000000000000000000000000000000.permissions (id),
    CONSTRAINT roles_permissions_link_fk_1 FOREIGN KEY (role_id) REFERENCES fake_tenant_company_for_test_00000000000000000000000000000000.roles (id)
);


INSERT INTO fake_tenant_company_for_test_00000000000000000000000000000000.permissions ("uuid", "name", title, description, is_visible, "group")
VALUES ('2c0b9a7a-4249-49ea-87f8-55cbda812ab7', 'OWNER_ACCESS', 'Master permission', 'Master permission', false,
        'service'),
       ('7298b761-db6b-4cac-b779-5178b369037f', 'USER_VIEW', 'Show users list', 'User can view list of other users',
        true, 'users'),
       ('7e3a27d6-3163-4d26-af80-96ab80817082', 'USER_ADD', 'Adding users', 'User can create new user accounts', true,
        'users'),
       ('64781bb4-b3f1-4aa4-96d5-88ba4b4b907d', 'USER_EDIT', 'Users editing', 'User can edit other users accounts',
        true, 'users'),
       ('c86e650b-08d7-46f2-bcaa-982e171eafc1', 'USER_EDIT_SELF', 'Account editing', 'Allow to edit my user account',
        true, 'users'),
       ('b056782e-95d9-4aaf-99b7-463cb57881cd', 'USER_DELETE', 'Removing users',
        'User can delete others users accounts', true, 'users'),
       ('2576bcf3-83e0-4f68-8fd1-566dbeb8b54e', 'USER_IMPORT', 'Importing users',
        'User can import  users data from CSV file', true, 'users'),
       ('fa484527-c8eb-4b59-96f3-cd03ad1e5aee', 'USER_EXPORT', 'Exporting users', 'User can export users data to CSV',
        true, 'users'),
       ('f8d967fa-c179-463a-863e-a44fb3f127f3', 'ISSUE_VIEW', 'Show issues list', 'User can view list of issues', true,
        'issues'),
       ('5fc6a488-acfb-459e-b9c2-d0367f461284', 'ISSUE_ADD', 'Adding issues', 'User can create new issues', true,
        'issues'),
       ('71a801cd-e4c4-4959-a821-f13eba70585b', 'ISSUE_EDIT', 'Issue editing', 'User can edit issue', true, 'issues'),
       ('177bd9a7-8522-452f-a19b-11993ad706ca', 'ISSUE_DELETE', 'Removing issues', 'User can delete existing issues',
        true, 'issues'),
       ('d071a124-62e2-44a5-bbe3-e459f29b8c7f', 'ISSUE_EXCLUDE', 'Exclude issues', 'Exclude issues from statistics',
        true, 'issues'),
       ('70aee0b0-d9e3-4a2f-adab-cf40f771aacf', 'ISSUE_MANAGE', 'Manage work', 'Allow to Start, Pause and Finish  work',
        true, 'issues'),
       ('d84c50c5-fb5e-4dc0-a350-b394dd920475', 'ISSUE_SHOw_HISTORY', 'Show issue history', 'Show issue history graph',
        true, 'issues'),
       ('c64f8231-9993-4d88-a1bd-da885fbf38c1', 'ISSUE_REPLACED_PARTS', 'Show replaced parts',
        'Allow to show, add, remove list of replaced parts', true, 'issues'),
       ('0c8d6757-174f-4790-a89b-f4d9d9bc4785', 'ISSUE_EXPORT', 'Exporting users', 'User can export users data to CSV',
        true, 'issues'),
       ('b865e9ec-ee92-4182-8018-2c35dcb27062', 'ITEM_VIEW', 'Show items list', 'User can view list of items', true,
        'items'),
       ('a4f298ff-dec2-453e-a3fb-9d72bde782dd', 'ITEM_ADD', 'Adding items', 'User can create new items', true, 'items'),
       ('f7fa2832-46ef-443d-bec1-13513539114c', 'ITEM_EDIT', 'Item editing', 'User can edit item', true, 'items'),
       ('5572eb8c-ee15-49cb-b3f7-7898d28ad6a5', 'ITEM_HIDE', 'Hide items', 'User can hide existing item', true,
        'items'),
       ('a79dd165-cf56-4994-8009-91d8f33e8508', 'ITEM_DELETE', 'Removing items', 'User can delete existing item', true,
        'items'),
       ('652f43e0-23de-4e4a-9de6-ac48d24884d0', 'ITEM_SHOW_QR', 'Show QR in Item', 'Show QR in Item', true, 'items'),
       ('62967bd4-4d88-4ee4-83ab-a45d8318e56d', 'ITEM_SHOw_HISTORY', 'Show item history', 'Show item history graph',
        true, 'items'),
       ('5211b87f-d814-43cb-8650-d1a3b7fb66d0', 'ITEM_IMPORT', 'Importing items',
        'User can import items data from CSV file', true, 'items'),
       ('9bde0e1b-e0fe-40f4-9e40-c25be822c0b8', 'ITEM_EXPORT', 'Exporting items', 'User can export items data to CSV',
        true, 'items'),
       ('9b412d44-b91f-44bc-aa0e-787d8a51fa0f', 'TAG_ADD', 'Add tag', 'Add tag', true, 'tags'),
       ('d24120d2-ce39-472d-90d1-2dfd0f5e6823', 'TAG_EDIT', 'Edit tag', 'Edit tag', true, 'tags'),
       ('26df05e0-ca39-445f-90e3-97e489fb9c4c', 'TAG_HIDE', 'Hide tag', 'Hide tag', true, 'tags'),
       ('2812b218-d3fc-483a-8d41-83be1f027380', 'TAG_DELETE', 'Delete tag', 'Delete tag', true, 'tags'),
       ('c4a41406-5c80-4670-a635-8c058f88bd65', 'SETTINGS_ACCOUNT', 'Acces to Account Settings',
        'User can change account related settings', true, 'settings'),
       ('b8aec65d-e492-48f2-9606-fbc52ea383f0', 'SETTINGS_TAGS', 'Acces to Tags Settings',
        'User can change Tags related settings', true, 'settings'),
       ('4f137185-730f-4f20-bb0c-51788654f2a5', 'SETTINGS_PERMISSION', 'Acces to Permissions Settings',
        'User can change Permission related settings', true, 'settings');

INSERT INTO fake_tenant_company_for_test_00000000000000000000000000000000.roles ("uuid", is_custom, is_visible,
                                                                                 is_system, role_name, role_title,
                                                                                 role_description, created_at,
                                                                                 updated_at, deleted_at)
VALUES ('a8cd3ea8-6a52-482d-9ca8-097d59429ea5', false, true, true, 'ADMIN_MASTER', 'Main admin', 'Main admin role',
        NULL, NULL, NULL),
       ('758fb334-fe25-40b6-9ac4-98417522afd7', false, true, false, 'ADMIN', 'Admin', 'Admin role', NULL, NULL, NULL),
       ('4b3be063-7cdd-434a-96c5-7de2a32d19d3', true, true, false, 'Serwisant', 'Serwisant', NULL, NULL, NULL, NULL);

INSERT INTO fake_tenant_company_for_test_00000000000000000000000000000000.roles_permissions_link (role_id, permission_id)
VALUES (1, 1),
       (1, 2),
       (1, 3),
       (1, 4),
       (1, 5),
       (1, 6),
       (1, 7),
       (1, 8),
       (1, 9),
       (1, 10),
       (1, 11),
       (1, 12),
       (1, 13),
       (1, 14),
       (1, 15),
       (1, 16),
       (1, 17),
       (1, 18),
       (1, 19),
       (1, 20),
       (1, 21),
       (1, 22),
       (1, 23),
       (1, 24),
       (1, 25),
       (1, 26),
       (1, 27),
       (1, 28),
       (1, 29),
       (1, 30),
       (1, 31),
       (1, 32),
       (1, 33),
       (2, 2),
       (2, 3),
       (2, 4),
       (2, 5),
       (2, 6),
       (2, 7),
       (2, 8),
       (2, 9),
       (2, 10),
       (2, 11),
       (2, 12),
       (2, 13),
       (2, 14),
       (2, 15),
       (2, 16),
       (2, 17),
       (2, 18),
       (2, 19),
       (2, 20),
       (2, 21),
       (2, 22),
       (2, 23),
       (2, 24),
       (2, 25),
       (2, 26),
       (2, 27),
       (2, 28),
       (2, 29),
       (2, 30),
       (2, 31),
       (2, 32),
       (2, 33),
       (3, 33);


INSERT INTO fake_tenant_company_for_test_00000000000000000000000000000000.users ("uuid", email, phone, "password", tos,
                                                                                 first_name, last_name, user_role_id,
                                                                                 auth_token, auth_token_valid_to,
                                                                                 is_active, is_verified, is_visible,
                                                                                 service_token, service_token_valid_to,
                                                                                 tz, lang, tenant_id, created_at,
                                                                                 updated_at, deleted_at)
VALUES ('868d7244-3ac4-44f3-8704-bc5863117066', 'anonymous@example.com', NULL, NULL, true, 'Anonymous', 'User', NULL,
        '5b4eb5c141211f36e22ca41e04a96ebdad581cfa07ae201109e03846bcdd78d9', '2023-07-15 13:34:43.280869+02', true, true,
        false, NULL, NULL, 'Europe/Warsaw', 'pl', 'fake_tenant_company_for_test_00000000000000000000000000000000',
        '2023-07-14 13:34:43.280876+02', NULL, NULL),
       ('59e49dd8-efb0-4201-b767-607257fd13de', 'user@example.com', '',
        '$argon2id$v=19$m=65536,t=3,p=4$PAegdO69976X8t77n/PeGw$gqyBNnZ1NCtLSa2sLTS2r7TttboBEafbGZchM1hlVNA', true,
        'Jan', 'Kowalski', 1,
        '7a1fc9e64e63c3c879b6cdab82277acc3ce2dd7adf2d3d9f13735b48a553ae978e502eff3cbc55206a8b2baddae447ecea0e9e62f06e652b2c9fafbae31d456c',
        '2024-05-03 15:18:52.244047+02', true, true, true, NULL, NULL, 'Europe/Warsaw', 'pl',
        'fake_tenant_company_for_test_00000000000000000000000000000000', '2023-07-14 13:34:43.280832+02',
        '2024-05-02 15:18:52.244111+02',
        NULL),
       ('94ca4f7e-e4ae-4921-8758-94e672fe201d', 'maciej.xxx@gmail.com', '',
        '$argon2id$v=19$m=65536,t=3,p=4$zDknJKTUGsN4zxljzBkjBA$GiL1slIklzjo/iS22EiAOlbZL7qcKSVm80jq165VnbY', true,
        'Maciej', 'Nowak', 3,
        'a9b4d21ae98b3d86853e897af669739f9859d095c23bdbd2b0b3e94e7cd9d6eca3c9c55ee99bacd91fdd7349f909cb35b39285a1b3a201750d65792c418859b3',
        '2024-02-07 14:27:32.622697+01', true, true, true, NULL, NULL, 'Europe/Warsaw', 'pl',
        'fake_tenant_company_for_test_00000000000000000000000000000000', '2023-11-14 18:37:56.824461+01',
        '2024-02-06 14:27:32.622729+01',
        NULL);