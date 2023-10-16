/* put database initialization script here */

-- for example
CREATE ROLE examuser WITH ENCRYPTED PASSWORD 'pass' LOGIN;
COMMENT ON ROLE examuser IS 'helpdesk django application';

CREATE DATABASE helpdeskdb OWNER docker;
COMMENT ON DATABASE helpdeskdb IS 'helpdesk project db';
