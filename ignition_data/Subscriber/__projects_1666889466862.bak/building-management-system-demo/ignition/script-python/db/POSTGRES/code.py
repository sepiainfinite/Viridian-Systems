def getQueries():
	"""
	Returns a list of update queries that can be executed to generate
		the dashboard structure in the db.
		
	Args:
		This function does not have any args.
		
	Returns:
		A list of update queries to create the dashboard structure
		in the db.
	"""

	queries = []
	
	queries.append("""
	CREATE TABLE widgets
	(
		id serial NOT NULL,
		name character varying(50) NOT NULL,
		path text NOT NULL,
		icon character varying(50),
		alias character varying(50) NOT NULL,
		position character varying(50) NOT NULL,
		PRIMARY KEY (id)
	)
	""")
	
	queries.append("""
	CREATE TABLE dashboards
	(
		id serial NOT NULL,
		parent_id integer,
		name character varying(50) NOT NULL,
		icon character varying(50),
		url character varying(200) NOT NULL,
		enabled integer NOT NULL DEFAULT 1,
		show_public integer NOT NULL DEFAULT 0,
		show_default integer NOT NULL DEFAULT 0,
		username character varying(50),
		gps_enabled integer NOT NULL DEFAULT 0,
		gps_lat real,
		gps_lon real,
		gps_radius real,
		grid character varying(50) NOT NULL DEFAULT 'fixed',
		cell_size integer NOT NULL DEFAULT 100,
		grid_rows integer NOT NULL DEFAULT 10,
		row_gutter_size integer NOT NULL DEFAULT 6,
		grid_cols integer NOT NULL DEFAULT 10,
		col_gutter_size integer NOT NULL DEFAULT 6,
		dashboard_order integer NOT NULL DEFAULT 1,
		last_modified timestamp with time zone NOT NULL,
		PRIMARY KEY (id),
		CONSTRAINT fk_dashboards_1 FOREIGN KEY (parent_id)
			REFERENCES dashboards (id) MATCH SIMPLE
			ON UPDATE NO ACTION
			ON DELETE NO ACTION
			NOT VALID
	)
	""")
	
	queries.append("""CREATE INDEX idx_dashboards_1 on dashboards using btree (enabled)""")
	queries.append("""CREATE INDEX idx_dashboards_2 on dashboards using btree (show_public)""")
	queries.append("""CREATE INDEX idx_dashboards_3 on dashboards using btree (username)""")
	
	queries.append("""
	CREATE TABLE dashboard_widgets
	(
		id serial NOT NULL,
		dashboard_id integer NOT NULL,
		widget_id integer NOT NULL,
		name character varying(50) NOT NULL,
		parameters text NOT NULL,
		position character varying(50) NOT NULL,
		PRIMARY KEY (id),
		CONSTRAINT fk_dashboard_widgets_1 FOREIGN KEY (dashboard_id)
			REFERENCES dashboards (id) MATCH SIMPLE
			ON UPDATE NO ACTION
			ON DELETE CASCADE
			NOT VALID,
		CONSTRAINT fk_dashboard_widgets_2 FOREIGN KEY (widget_id)
			REFERENCES widgets (id) MATCH SIMPLE
			ON UPDATE NO ACTION
			ON DELETE NO ACTION
			NOT VALID
	)
	""")
	
	return queries
