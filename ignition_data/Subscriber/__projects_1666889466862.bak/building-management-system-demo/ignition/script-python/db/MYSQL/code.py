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
	CREATE TABLE `widgets` (
	  `id` int(11) NOT NULL AUTO_INCREMENT,
	  `name` varchar(50) NOT NULL,
	  `path` text NOT NULL,
	  `icon` varchar(50) DEFAULT NULL,
	  `alias` varchar(50) NOT NULL,
	  `parameters` text NOT NULL,
	  PRIMARY KEY (`id`)
	) ENGINE=InnoDB
	""")
	
	queries.append("""
	CREATE TABLE `dashboards` (
	  `id` int(11) NOT NULL AUTO_INCREMENT,
	  `parent_id` int(11) DEFAULT NULL,
	  `name` varchar(50) NOT NULL,
	  `icon` varchar(50) DEFAULT NULL,
	  `url` varchar(200) NOT NULL,
	  `enabled` tinyint(1) NOT NULL DEFAULT '1',
	  `show_public` tinyint(1) NOT NULL DEFAULT '0',
	  `show_default` tinyint(1) NOT NULL DEFAULT '0',
	  `username` varchar(50) DEFAULT NULL,
	  `gps_enabled` tinyint(1) NOT NULL DEFAULT '0',
	  `gps_lat` decimal(11,8) DEFAULT NULL,
	  `gps_lon` decimal(11,8) DEFAULT NULL,
	  `gps_radius` decimal(11,8) DEFAULT NULL,
	  `grid` varchar(50) NOT NULL DEFAULT 'fixed',
	  `cell_size` int(11) NOT NULL DEFAULT 100,
	  `grid_rows` int(11) NOT NULL DEFAULT 10,
	  `row_gutter_size` int(11) NOT NULL DEFAULT 6,
	  `grid_cols` int(11) NOT NULL DEFAULT 10,
	  `col_gutter_size` int(11) NOT NULL DEFAULT 6,
	  `dashboard_order` int(11) NOT NULL DEFAULT '1',
	  `last_modified` DATETIME NOT NULL,
	  PRIMARY KEY (`id`),
	  KEY `fk_dashboards_1_idx` (`parent_id`),
	  KEY `idx_dashboards_1` (`enabled`),
	  KEY `idx_dashboards_2` (`show_public`),
	  KEY `idx_dashboards_3` (`username`),
	  CONSTRAINT `fk_dashboards_1` FOREIGN KEY (`parent_id`) REFERENCES `dashboards` (`id`) 
	) ENGINE=InnoDB
	""")
	
	queries.append("""
	CREATE TABLE `dashboard_widgets` (
	  `id` int(11) NOT NULL AUTO_INCREMENT,
	  `dashboard_id` int(11) NOT NULL,
	  `widget_id` int(11) NOT NULL,
	  `name` varchar(50) NOT NULL,
	  `parameters` text NOT NULL,
	  `position` varchar(50) NOT NULL,
	  PRIMARY KEY (`id`),
	  KEY `fk_dashboard_widgets_1_idx` (`dashboard_id`),
	  KEY `fk_dashboard_widgets_2_idx` (`widget_id`),
	  CONSTRAINT `fk_dashboard_widgets_1` FOREIGN KEY (`dashboard_id`) REFERENCES `dashboards` (`id`) ON DELETE CASCADE,
	  CONSTRAINT `fk_dashboard_widgets_2` FOREIGN KEY (`widget_id`) REFERENCES `widgets` (`id`)
	) ENGINE=InnoDB
	""")
	
	return queries
