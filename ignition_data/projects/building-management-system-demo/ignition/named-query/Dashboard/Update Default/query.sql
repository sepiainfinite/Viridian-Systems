UPDATE dashboards SET show_default = 0 WHERE show_public = 0 AND username = :username AND id != :id