UPDATE dashboards 
SET 
	dashboard_order = :dashboard_order, 
	enabled = :enabled, 
	gps_enabled = :gps_enabled, 
	gps_lat = :gps_lat,
	gps_lon = :gps_lon,
	gps_radius = :gps_radius, 
	grid = :grid,
	cell_size = :cell_size,
	grid_rows = :grid_rows,
	grid_cols = :grid_cols,
	row_gutter_size = :grid_row_gutter_size,
	col_gutter_size = :grid_col_gutter_size,
	icon = :icon, 
	name = :name, 
	parent_id = :parent_id, 
	show_default = :show_default, 
	show_public = :show_public, 
	url = :url, 
	username = :username, 
	last_modified = CURRENT_TIMESTAMP 
WHERE 
	id = :id