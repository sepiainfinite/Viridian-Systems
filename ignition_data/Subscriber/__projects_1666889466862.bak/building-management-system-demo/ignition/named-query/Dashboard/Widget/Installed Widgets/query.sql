SELECT 
	w.id,
	w.name widget,
	w.path,
	w.icon,
	w.parameters
FROM 
	widgets w
ORDER BY 
	w.name ASC, w.id ASC