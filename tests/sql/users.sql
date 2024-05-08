-- fake_tenant_company_for_test_00000000000000000000000000000000.users definition

-- Drop table

-- DROP TABLE fake_tenant_company_for_test_00000000000000000000000000000000.users;
CREATE SCHEMA fake_tenant_company_for_test_00000000000000000000000000000000;
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
    CONSTRAINT users_service_token_key UNIQUE (service_token)
);
CREATE INDEX ix_users_uuid ON fake_tenant_company_for_test_00000000000000000000000000000000.users USING btree (uuid);

INSERT INTO fake_tenant_company_for_test_00000000000000000000000000000000.users ("uuid", email, phone, "password", tos,
                                                                                 first_name, last_name, user_role_id,
                                                                                 auth_token, auth_token_valid_to,
                                                                                 is_active, is_verified, is_visible,
                                                                                 service_token, service_token_valid_to,
                                                                                 tz, lang, tenant_id, created_at,
                                                                                 updated_at, deleted_at)
VALUES ('868d7244-3ac4-44f3-8704-bc5863117066', 'anonymous@example.com', NULL, NULL, true, 'Anonymous', 'User', NULL,
        '5b4eb5c141211f36e22ca41e04a96ebdad581cfa07ae201109e03846bcdd78d9', '2023-07-15 13:34:43.280869+02', true, true,
        false, NULL, NULL, 'Europe/Warsaw', 'pl', 'string_05eab8892bea4db18c3ff73222e073ee',
        '2023-07-14 13:34:43.280876+02', NULL, NULL),
       ('59e49dd8-efb0-4201-b767-607257fd13de', 'user@example.com', '',
        '$argon2id$v=19$m=65536,t=3,p=4$PAegdO69976X8t77n/PeGw$gqyBNnZ1NCtLSa2sLTS2r7TttboBEafbGZchM1hlVNA', true,
        'Jan', 'Kowalski', 1,
        '7a1fc9e64e63c3c879b6cdab82277acc3ce2dd7adf2d3d9f13735b48a553ae978e502eff3cbc55206a8b2baddae447ecea0e9e62f06e652b2c9fafbae31d456c',
        '2024-05-03 15:18:52.244047+02', true, true, true, NULL, NULL, 'Europe/Warsaw', 'pl',
        'string_05eab8892bea4db18c3ff73222e073ee', '2023-07-14 13:34:43.280832+02', '2024-05-02 15:18:52.244111+02',
        NULL),
       ('94ca4f7e-e4ae-4921-8758-94e672fe201d', 'maciej.xxx@gmail.com', '',
        '$argon2id$v=19$m=65536,t=3,p=4$zDknJKTUGsN4zxljzBkjBA$GiL1slIklzjo/iS22EiAOlbZL7qcKSVm80jq165VnbY', true,
        'Maciej', 'Nowak', 3,
        'a9b4d21ae98b3d86853e897af669739f9859d095c23bdbd2b0b3e94e7cd9d6eca3c9c55ee99bacd91fdd7349f909cb35b39285a1b3a201750d65792c418859b3',
        '2024-02-07 14:27:32.622697+01', true, true, true, NULL, NULL, 'Europe/Warsaw', 'pl',
        'string_05eab8892bea4db18c3ff73222e073ee', '2023-11-14 18:37:56.824461+01', '2024-02-06 14:27:32.622729+01',
        NULL);
000.users ADD CONSTRAINT role_fk FOREIGN KEY (user_role_id) REFERENCES fake_tenant_company_for_test_00000000000000000000000000000000.roles(id);
