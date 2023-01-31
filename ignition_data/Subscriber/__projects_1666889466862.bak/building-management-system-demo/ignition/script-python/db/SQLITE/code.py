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
	CREATE TABLE widgets (
	  id integer PRIMARY KEY AUTOINCREMENT,
	  name text NOT NULL,
	  path text NOT NULL,
	  icon text DEFAULT NULL,
	  alias text NOT NULL,
	  parameters text NOT NULL
	)
	""")
	
	queries.append("""
	CREATE TABLE dashboards (
	  id integer PRIMARY KEY AUTOINCREMENT,
	  parent_id integer DEFAULT NULL,
	  name text NOT NULL,
	  icon text DEFAULT NULL,
	  url text NOT NULL,
	  enabled integer NOT NULL DEFAULT '1',
	  show_public integer NOT NULL DEFAULT '0',
	  show_default integer NOT NULL DEFAULT '0',
	  username text DEFAULT NULL,
	  gps_enabled integer NOT NULL DEFAULT '0',
	  gps_lat real DEFAULT NULL,
	  gps_lon real DEFAULT NULL,
	  gps_radius real DEFAULT NULL,
	  grid text NOT NULL DEFAULT 'fixed',
	  cell_size integer NOT NULL DEFAULT 100,
	  grid_rows integer NOT NULL DEFAULT 10,
	  row_gutter_size integer NOT NULL DEFAULT 6,
	  grid_cols integer NOT NULL DEFAULT 10,
	  col_gutter_size integer NOT NULL DEFAULT 6,
	  dashboard_order integer NOT NULL DEFAULT '1',
	  last_modified integer NOT NULL,
	  FOREIGN KEY (parent_id) REFERENCES dashboards (id)
	)
	""")
	
	queries.append("""CREATE INDEX idx_dashboards_1 ON dashboards (enabled)""")
	queries.append("""CREATE INDEX idx_dashboards_2 ON dashboards (show_public)""")
	queries.append("""CREATE INDEX idx_dashboards_3 ON dashboards (username)""")
	
	queries.append("""
	CREATE TABLE dashboard_widgets (
	  id integer PRIMARY KEY AUTOINCREMENT,
	  dashboard_id integer NOT NULL,
	  widget_id integer NOT NULL,
	  name text NOT NULL,
	  parameters text NOT NULL,
	  position text NOT NULL,
	  FOREIGN KEY (dashboard_id) REFERENCES dashboards (id) ON DELETE CASCADE,
	  FOREIGN KEY (widget_id) REFERENCES widgets (id)
	)
	""")
	
	return queries
