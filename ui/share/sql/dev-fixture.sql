\echo ---------------------------------
\echo --
\echo -- Adding some users and groups
\echo --
\echo ---------------------------------
\echo

INSERT INTO application.roles (role_name, role_password, role_email, is_active, is_admin)
-- alice // alice
VALUES ('alice', 'Xm4iJH8aQmXRvrsLy/fNbQU23K6/FlEVRhhPZKO2aHvYVGzCft+u7RXQ9Z48IyVtnS+n47UM3QUM4is0BVTPOA==', 'alice@temboard.local', true, false),
-- bob // bob
       ('bob', 'f9Yol14q9N89EyYSCUR9izXfXugNiXN/HiKsa8CFnIzq/MADFgL7UnjMnxBVypSP6vzPbusotyEAF5H6tP2Mlw==', 'bob@temboard.local', true, false);

INSERT INTO application.role_groups (role_name, group_name, group_kind)
VALUES ('alice', 'default', 'role'),
       ('bob', 'default', 'role');

-- Pre-register agents

INSERT INTO application.instances
(agent_address, agent_port, agent_key, hostname, pg_port, comment, notify)
VALUES
('0.0.0.0', 2345, NULL, 'postgres0.dev', 5432, '', FALSE),
('0.0.0.0', 2346, NULL, 'postgres1.dev', 5432, '', FALSE),
('0.0.0.0', 2347, 'key_for_agent', 'postgres-stable.dev', 5432, '', FALSE);

INSERT INTO application.instance_groups
(agent_address, agent_port, group_name, group_kind)
VALUES
('0.0.0.0', 2345, 'default', 'instance'),
('0.0.0.0', 2346, 'default', 'instance'),
('0.0.0.0', 2347, 'default', 'instance');

INSERT INTO application.plugins
(agent_address, agent_port, plugin_name)
VALUES
('0.0.0.0', 2345, 'dashboard'),
('0.0.0.0', 2345, 'pgconf'),
('0.0.0.0', 2345, 'activity'),
('0.0.0.0', 2345, 'monitoring'),
('0.0.0.0', 2345, 'maintenance'),
('0.0.0.0', 2345, 'statements'),
('0.0.0.0', 2346, 'dashboard'),
('0.0.0.0', 2346, 'pgconf'),
('0.0.0.0', 2346, 'activity'),
('0.0.0.0', 2346, 'monitoring'),
('0.0.0.0', 2346, 'maintenance'),
('0.0.0.0', 2346, 'statements'),
('0.0.0.0', 2347, 'dashboard'),
('0.0.0.0', 2347, 'pgconf'),
('0.0.0.0', 2347, 'activity'),
('0.0.0.0', 2347, 'monitoring'),
('0.0.0.0', 2347, 'maintenance'),
('0.0.0.0', 2347, 'statements');
