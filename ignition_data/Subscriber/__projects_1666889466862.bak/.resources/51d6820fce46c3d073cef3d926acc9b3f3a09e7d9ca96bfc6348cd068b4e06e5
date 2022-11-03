SELECT 
	d.id,
	d.parent_id,
	d.name,
	d.url,
	COALESCE(d.icon, '') icon,
	d.gps_enabled,
	d.gps_lat,
	d.gps_lon,
	d.gps_radius,
	d.show_default,
	d.show_public,
	d.username,
	d.grid,
	d.cell_size,
	d.grid_rows,
	d.row_gutter_size,
	d.grid_cols,
	d.col_gutter_size,	
	d.dashboard_order
FROM 
	dashboards d
WHERE 
	d.enabled = 1 AND 
	(d.show_public = 1 OR d.username = :username)
ORDER BY 
	d.parent_id ASC, d.dashboard_order ASC, d.id ASC