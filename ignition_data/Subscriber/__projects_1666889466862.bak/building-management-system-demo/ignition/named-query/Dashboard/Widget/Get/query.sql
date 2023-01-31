SELECT 
	dw.id,
	dw.name,
	w.id widget_id,
	w.name widget,
	w.path,
	w.icon,
	dw.parameters,
	dw.position
FROM 
	dashboard_widgets dw 
		JOIN widgets w ON w.id = dw.widget_id 
WHERE 
	dw.dashboard_id = :dashboard
ORDER BY 
	dw.id ASC, dw.name