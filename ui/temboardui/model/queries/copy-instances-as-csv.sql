COPY (
  WITH
		inventory AS (SELECT DISTINCT
			i.hostname AS "Hostname",
			i.pg_port AS "Port",
			i.pg_data AS "PGDATA",
			i.pg_version_summary AS "Version",
			string_agg(DISTINCT group_name, ',') AS "Groups",
			i.agent_address AS "Agent Address",
			i.agent_port AS "Agent Port",
			string_agg(DISTINCT plugin_name, ',') AS "Plugins"
		FROM application.instances AS i
		LEFT OUTER JOIN application.instance_groups AS groups
				ON groups.agent_port = i.agent_port
				AND groups.agent_address = i.agent_address
		LEFT OUTER JOIN application.plugins
				ON plugins.agent_address = i.agent_address
				AND plugins.agent_port = i.agent_port
		GROUP BY 1, 2, 3, 4, 6, 7
		ORDER BY 1, 2
	)
  SELECT * FROM inventory
	WHERE concat_ws(
		' ',
		"Hostname", "Port", "PGDATA", "Version", "Groups",
		"Agent Address", "Agent Port"
	) LIKE %s
) TO STDOUT WITH (
	DELIMITER ';',
	ENCODING 'UTF-8',
	FORCE_QUOTE *,
	FORMAT CSV,
	HEADER
) ;
