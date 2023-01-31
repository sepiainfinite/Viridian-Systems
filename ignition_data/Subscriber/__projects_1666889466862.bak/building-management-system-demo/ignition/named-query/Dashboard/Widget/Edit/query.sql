UPDATE dashboard_widgets
SET
	dashboard_id = :dashboard_id, 
	widget_id = :widget_id, 
	name = :name,
	parameters = :parameters,
	position = :position
WHERE 
	id = :id