def createTables(self):
	"""
	Tries to automatically create the db tables that are required
		to set up the dashboard structure expected by this project.
		
	Args:
		self: Instance object containing session properties and
			  properties from the view from which this was called.
		
	Returns:
		This function does not have a return value.
	"""
	
	from com.inductiveautomation.ignition.gateway import IgnitionGateway
	
	# Try to get the default db connection for this project, and then try
	# to determine the db type for this connection.
	try:
		context = IgnitionGateway.get()
		projectName = system.project.getProjectName()
		dbName = context.getProjectManager().getProjectProps(projectName).getDefaultDatasourceName()
		ds = system.dataset.toPyDataSet(system.db.getConnectionInfo(dbName))
		dbType = ds[0]["DBType"]
	except:
		dbType = "MYSQL"
	
	if dbType == None:
		dashboard.showError("Unable to determine your project's default database. Please create tables manually.")
	else:
		try:
			# Run the update queries that are associated with the db type.
			queries = eval("db.%s.getQueries()" % dbType)
			for query in queries:
				system.db.runUpdateQuery(query)
				
			# Refresh the session objects (which hold info regarding the dashboards).
			dashboard.refresh(self)
		except:
			dashboard.showError("Database type '%s' is not currently supported" % dbType)
	
def getDashboards(ds, parentId=None, parentPath=None, defaultDashboard=None):
	"""
	Utilizes the info from the 'ds' dataset arg to create a list
		of dashboard objects. The 'ds' arg contains info regarding
		the dashboards.
			
	Args:
		ds: Dataset that holds info regarding the dashboards.
		parentId: ID of the parent of a set of dashboards.
		parentPath: Path to the dashboard parent (tree structure).
		defaultDashboard: Dashboard displayed by default. 
			
	Returns:
		A list of dictionary objects that represent dashboards.
	"""
		
	# Create dashboards and gps lists.
	dashboards = []
	gps = []
	
	# Iterate through dataset, reading dashboard info and
	# storing the info in variables.
	for row in ds:
		id = row["id"]
		dashboardParentId = row["parent_id"]
		name = row["name"]
		icon = row["icon"]
		dashboardUrl = row["url"]
		gps_enabled = row["gps_enabled"]
		gps_lat = row["gps_lat"]
		gps_lon = row["gps_lon"]
		gps_radius = row["gps_radius"]
		showDefault = row["show_default"]
		showPublic = row["show_public"]
		username = row["username"]
		grid = row["grid"]
		cellSize = row["cell_size"]
		gridRows = row["grid_rows"]
		gridRowGutterSize = row["row_gutter_size"]
		gridCols = row["grid_cols"]
		gridColGutterSize = row["col_gutter_size"]	  
		dashboardOrder = row["dashboard_order"]
		
		if parentId == None:
			if gps_enabled:
				gps.append({"url":dashboardUrl, "lat":gps_lat, "lon":gps_lon, "radius":gps_radius})
		
		# Create the dictionary object representing the dashboard.
		d = {"id":id, "name":name, "url":dashboardUrl, "icon":icon, "parent_id":dashboardParentId, "parent_path":parentPath, "allow_edit": True, "default":showDefault, "public":showPublic, "gps":{"enabled":gps_enabled, "lat":gps_lat, "lon":gps_lon, "radius":gps_radius}, "grid":grid, "cellSize":cellSize, "gridRows":gridRows, "gridRowGutterSize":gridRowGutterSize, "gridCols":gridCols, "gridColGutterSize":gridColGutterSize, "order":dashboardOrder, "action":{"action":"edit"}}		
		if dashboardParentId == parentId:
			# Get the widgets for this dashboard.
			res = system.db.runNamedQuery(path="Dashboard/Widget/Get", parameters={"dashboard":id})
			res = system.dataset.toPyDataSet(res)
			
			widgets = {}
			idx = 0
			
			# Iterate through the widgets dataset, decode the
			# widget params, create the widget object, and add
			# it to the widgets dictionary.
			for w in res:
				if w["id"] not in widgets:
					viewParams = system.util.jsonDecode(w["parameters"])
					widgets[w["id"]] = {"id":w["id"], "widget_id":w["widget_id"], "idx":idx, "name":w["name"], "widget":w["widget"], "position":w["position"], "path":w["path"], "params":viewParams, "action":{"action":"", "params":[]}}
					idx += 1

			if parentPath == None:
				pp = name
			else:
				pp = "%s/%s" % (parentPath, name)
			
			# Add the widgets to the dashboard dictionary (along
			# with any children of this dashboard, and the
			# dashboard's author's username).	
			d["widgets"] = [w[1] for w in widgets.items()]
			d["children"] = dashboard.getDashboards(ds, id, pp, defaultDashboard)
			d["username"] = username
			
			# Append the dashboard object to the dashboards list.
			dashboards.append(d)
			
			if defaultDashboard == None and showDefault:
				defaultDashboard = d
			
	if parentId == None:
		return {"default":defaultDashboard, "dashboards":dashboards, "valid":True, "gps":gps, "numDashboards":len(ds)}
		
	return dashboards

def getWidgetsRows(ds, gridRows):
	"""
	The widgets of a dashboard are displayed in a single column
		on a mobile device. In this case, the dashboard needs
		to know the total number of rows required to display
		the widgets. This utilizes the position info in the 'ds'
		dataset arg to count the total number of rows for the
		widgets of the dashboard.
		
	Args:
		ds: Dataset containing info about a dashboard's widgets. 
		gridRows: Configured number of rows in the dashboard's grid. 
		
	Returns:
		The total number of rows of a dashboard's widgets.
	"""
	
	rowIndex = 1	
	for row in ds:
		if row["action"]["action"] != "delete":
			position = row["position"].split(",")
			numRows = int(position[1]) - int(position[0])
			# To keep a 'consistent ratio' regarding widget height
			# on mobile for dashboards that have varying amounts
			# of rows in the grid (and also for the calculated font
			# and icon size in the status widgets), the num rows
			# are divided by the num rows in the grid, and the res
			# is multiplied by 50.
			numRows = (float(numRows)/float(gridRows))*50.0
			rowIndex += (numRows + 1)

	return round(rowIndex)
	
def getWidgets(ds, mobile=False, configurable=False, rowCount=0, columnCount=0, theme='hvac-dark', editing=False):
	"""
	Utilizes the info in the 'ds' dataset arg to create a list
		of dictionary objects that represent the widgets of a
		dashboard.
		
	Args:
		ds: Dataset containing info about a dashboard's widgets. 
		mobile: Bool denoting whether user is on mobile device.
		configurable: Bool denoting if widgets can be edited.
		rowCount: Number of rows in the grid of the dashboard.
		columnCount: Number of cols in the grid of the dashboard.
		theme: The current theme being used in the session.
		editing: Bool denoting whether the user is editing the
				 dashboard.
		
	Returns:
		A list of dictionary objects that represents the widgets
		of a dashboard.
	"""

	widgets = []
	rowIndex = 1
	
	# Iterate through the dataset, reading the info about each
	# widget and creating a widget dictionary object.
	for row in ds:
		if row["action"]["action"] != "delete":
			position = row["position"].split(",")
			numRows = int(position[1]) - int(position[0])
			numRowsMobile = round((float(numRows)/float(rowCount))*50.0)

			widget = {
			  "name": row["name"],
			  "viewPath": "Building Automation Demo/Page/Systems Overview/Framework/Dashboard/Configuration/Edit Widget Wrapper" if configurable else row["path"],
			  "viewParams": {"id":row["id"], "configuring":False, "name":row["name"], "widgetId":row["widget_id"], "widgetName":row["widget"], "viewPath":row["path"], "viewParams":dict(row["params"]), "editParams":row["action"]["params"]} if configurable else row["params"],
			  "isConfigurable": configurable,
			  "header": {
				"enabled": False,
				"title": row["name"],
				"style": {
				  "classes": ""
				}
			  },
			  "body": {
				"style": {
				  "classes": ""
				}
			  },
			  "minSize": {
				"columnSpan": 1,
				"rowSpan": 1
			  },
			  "position": {
				"rowStart": rowIndex if mobile else int(position[0]),
				"rowEnd": (rowIndex + numRowsMobile) if mobile else int(position[1]),
				"columnStart": 1 if mobile else int(position[2]),
				"columnEnd": 2 if mobile else int(position[3])
			  },
			  "style": {
				"classes": "",
				"marginLeft": '10px' if mobile else '0px',
				"marginRight": '10px' if mobile else '0px'
			  }
			}
			
			# Apply slightly different style when theme is light.
			#if theme in ['hvac','hvac-warm']:
			widget["style"]["borderStyle"] = 'solid'
			widget["style"]["borderWidth"] = '1px'
			widget["style"]["borderColor"] = '--neutral-30' if theme in ['hvac','hvac-warm'] else '--neutral-60'
				
			# Make background transparent if title widget.
			if row["name"] == 'Title':
				widget["style"]["borderStyle"] = "none"
				if editing == False:
					widget["body"]["style"]["backgroundColor"] = "#00000000"
				else:
					widget["body"]["style"]["backgroundColor"] = "#00000059"
			
			# Tell the widget that the dashboard that it is housed in is currently
			# being edited. This will enable the tooltips for the nonTitle widgets,
			# so that when setting associated widgets for title widgets, if there
			# are any widgets with the same name (in which the case the user needs
			# to know the widgetID), then the user can hover the mouse over the
			# widgets that have the same name in order to reveal the widgetID.
			if widget['name'] != 'Title':
				if editing:
					widget['viewParams']['viewParams']['beingEdited'] = True
					widget['viewParams']['viewParams']['widgetID'] = widget['viewParams']['id']
				
			# Tell Single Status and Alarm Count widgets the number of rows and columns 
			# in the dashboard (utilized to calculate font size in these widgets) and the
			# number of rows and columns that they span.
			if widget['name'] in ['Single Status', 'Alarm Count']:
				widget['viewParams']['viewParams']['rowCount'] = rowCount
				widget['viewParams']['viewParams']['columnCount'] = columnCount

				widget['viewParams']['viewParams']['rowSpan'] = widget['position']['rowEnd'] - widget['position']['rowStart']
				widget['viewParams']['viewParams']['columnSpan'] = widget['position']['columnEnd'] - widget['position']['columnStart']
			
			# Tell widgets that they are being viewed in mobile environment.
			if mobile:
				widget['viewParams']['viewParams']['mobile'] = True
				rowIndex += (numRowsMobile + 1)
			else:
				rowIndex += (numRows + 1)
			
			widgets.append(widget)
			
	# If the dashboard has any Title widgets and mobile=True, then re-order 
	# the widgets in the 'widgets' list such that the Title widgets are 
	# positioned correctly (the widgets that are displayed after a Title 
	# widget should correspond to that title widget). This can be done by
	# modifying the position properties of the widgets.
	if mobile:
		titleWidgets = [titleWidget for titleWidget in widgets if titleWidget['name'] == 'Title']
		nonTitleWidgets = [nonTitleWidget for nonTitleWidget in widgets if nonTitleWidget['name'] != 'Title']
		if len(titleWidgets) > 0:
			rowStart = 1
			rowEnd = 2
			widgetsToReturn = []
			for titleWidget in titleWidgets:
				associatedWidgets = titleWidget['viewParams']['viewParams']['associatedWidgets']
				if len(associatedWidgets) > 0:
					# Only displaying the title widgets that have at least one
					# associated widget.
					
					if rowEnd - 1 != rowStart:
						rowEnd = rowStart + 1
					
					titleWidget['position']['rowStart'] = rowStart
					titleWidget['position']['rowEnd'] = rowEnd
					
					widgetsToReturn.append(titleWidget)
					nonTitleWidgetsToRemove = []
					for nonTitleWidget in nonTitleWidgets:
						associatedID = nonTitleWidget['viewParams']['viewParams']['widgetTitle'] + ' (' + str(nonTitleWidget['viewParams']['id']) + ')'
						if associatedID in associatedWidgets:
							nonTitleWidgetRowStart = nonTitleWidget['position']['rowStart']
							nonTitleWidgetRowEnd = nonTitleWidget['position']['rowEnd']
							
							nonTitleWidgetRowSpan = nonTitleWidgetRowEnd - nonTitleWidgetRowStart
							
							rowStart = rowEnd + 1
							rowEnd = rowStart + nonTitleWidgetRowSpan
							
							nonTitleWidget['position']['rowStart'] = rowStart
							nonTitleWidget['position']['rowEnd'] = rowEnd
							
							widgetsToReturn.append(nonTitleWidget)
							
							# Making an assumption that a non-title widget can
							# be associated with only one title widget. So, once
							# a nonTitleWidget has been added to widgetsToReturn,
							# it can be removed from nonTitleWidgets.
							nonTitleWidgetsToRemove.append(nonTitleWidget)
							
							rowStart = rowEnd + 1
					
					for nonTitleWidgetToRemove in nonTitleWidgetsToRemove:
						nonTitleWidgets.remove(nonTitleWidgetToRemove)
							
			
			# The only widgets that remain in nonTitleWidgets are the widgets
			# that are not associated with any Title widgets. Append the
			# remaining widgets to widgetsToReturn.
			
			if rowEnd - 1 != rowStart:
				rowEnd = rowStart + 1 
			
			for nonTitleWidget in nonTitleWidgets:
				nonTitleWidgetRowStart = nonTitleWidget['position']['rowStart']
				nonTitleWidgetRowEnd = nonTitleWidget['position']['rowEnd']
				
				nonTitleWidgetRowSpan = nonTitleWidgetRowEnd - nonTitleWidgetRowStart
				
				rowStart = rowStart + 1
				rowEnd = rowStart + nonTitleWidgetRowSpan
				
				nonTitleWidget['position']['rowStart'] = rowStart
				nonTitleWidget['position']['rowEnd'] = rowEnd
				
				widgetsToReturn.append(nonTitleWidget)
				
				rowStart = rowEnd + 1
			
			widgets = widgetsToReturn
	
	return widgets
	
def getInstalledWidgets(ds):
	"""
	Utilizes the info in the 'ds' dataset arg to create a list
		of dictionary objects that represents widgets that are
		available to be added to a dashboard.
		
	Args:
		ds: Dataset containing info about widgets that are
			available to install. 
		
	Returns:
		A list of dictionary objects that represents widgets
		that are available to install.
	"""

	widgets = {}
	
	# Iterate through the dataset, reading the widget info and
	# creating an 'avaialable widget' dictionary object for
	# each row.
	for row in ds:
		if row["id"] not in widgets:
			viewParams = system.util.jsonDecode(row["parameters"])
			widgets[row["id"]] = {
								  "name": row["widget"],
								  "viewPath": "Building Automation Demo/Page/Systems Overview/Framework/Dashboard/Configuration/Edit Widget Wrapper",
								  "viewParams": {"id":None, "configuring":False, "name":row["widget"], "widgetId":row["id"], "widgetName":row["widget"], "viewPath":row["path"], "viewParams":viewParams, "editParams":[]},
								  "isConfigurable": True,
								  "header": {
									"enabled": True,
									"title": row["widget"],
									"style": {
									  "classes": ""
									}
								  },
								  "body": {
									"style": {
									  "classes": ""
									}
								  },
								  "defaultSize": {
									"columnSpan": 1,
									"rowSpan": 1
								  },
								  "minSize": {
									"columnSpan": 1,
									"rowSpan": 1
								  },
								  "category":"Widgets",
								  "style": {
									"classes": ""
								  }
								}
	return [w[1] for w in widgets.items()]
	
def getCurrentDashboard(dashboards, url, sub=False):
	"""
	Utilizes the 'url' arg to find the dashboard in the 'dashboards'
		list arg that should be currently displayed on the Systems
		Overview page (in the current session).
		
	Args:
		dashboards: List of the available dashboards. 
		url: String representing the dashboard that should be displayed
			 in the current session.
		sub: Boolean denoting whether the dashboards list is a sub-member  
			 of the 'dashboards' arg.
			 
	Returns:
		A dictionary object representing the current dashboard.
	"""
	
	d = None

	if not sub:
		dbObj = dashboards.dashboards
	else:
		dbObj = dashboards

	for row in dbObj:
		if '/dashboard/' + row["url"] == url or row["url"] == url:
			# Found the current dashboard.
			d = dashboard.getDashboardObject(row)
		else:
			# Search the children of the dashboard to see if one
			# of them is the current dashboard.
			d = dashboard.getCurrentDashboard(row["children"], url, True)
			
		if d != None:
			break
	
	# If the dashboard was not found, then either try to return
	# the default dashboard if the 'default dashboard' property
	# is not null, or return an empty dashboard.
	if d == None and not sub:
		if dashboards.default != None:
			d = dashboard.getDashboardObject(dashboards.default)
		else:
			d = dashboard.getDashboardObject(False)
			
	return d

def getDashboard(id, dashboards):
	"""
	Utilizes the 'id' arg to find a specific dashboard in the
		'dashboards' list arg.
		
	Args:
		id: Number representing the dashboard that this function
			is trying to find.
		dashboards: List of configured dashboards.
		
	Returns:
		The dashboard that corresponds with the id.
	"""

	for dashboard in dashboards:
		if dashboard.id == id:
			return dashboard
	return {}

def getDashboardObject(dbObj):
	"""
	Returns a dictionary object that represents a dashboard. Either
		returns an empty dashboard if the 'dbObj' param is a bool,
		or returns a non-empty dashboard that represents the dashboard
		in the 'dbObj' arg.
		
	Args:
		dbObj: Either a boolean, which means that an empty dashboard
			   should be returned, or an object that contains the
			   properties and widgets of a dashboard. 
		
	Returns:
		A dictionary object representing a dashboard.
	"""

	if isinstance(dbObj, bool):
		if dbObj:
			return {"id":None, "name":"", "url":"", "icon":"dashboard", "parent_id":None, "parent_path":"", "allow_edit":True, "default":False, "public":False, "gps":{"enabled":False, "lat":None, "lon":None, "radius":None}, "order":None, "widgets":[], "grid":"stretch", "cellSize":100, "gridRows":10, "gridCols":10, "gridRowGutterSize":6, "gridColGutterSize":6, "action":{"action":"add"}}
		else:
			return {"id":None, "name":None, "url":None, "icon":None, "parent_id":None, "parent_path":None, "allow_edit":False, "default":False, "public":False, "gps":{"enabled":False, "lat":None, "lon":None, "radius":None}, "order":None, "widgets":[], "grid":"stretch", "cellSize":100, "gridRows":10, "gridCols":10, "gridRowGutterSize":6, "gridColGutterSize":6, "action":{"action":""}}
	elif dbObj != None:
		return dashboard.copyDictionary(dbObj)

def copyArray(items):
	"""
	Copies the info in the 'items' arg and returns the copied list.
		
	Args:
		items: The list to be copied.
		
	Returns:
		A list that is a copy of the 'items' arg.
	"""
	
	ret = []
	for value in items:
		if str(type(value)) == "<type 'com.inductiveautomation.perspective.gateway.script.PropertyTreeScriptWrapper$MapWrapper'>" or type(value) == dict:
			ret.append(dashboard.copyDictionary(value))
		else:
			ret.append(value)
	return ret
		
def copyDictionary(items):
	"""
	Copies the info in the 'items' arg and returns the copied dictionary.
		
	Args:
		items: The dictionary to be copied.
		
	Returns:
		A dictionary that is a copy of the 'items' arg.
	"""

	ret = {}
	for key in items:
		value = items[key]
		
		if str(type(value)) == "<type 'com.inductiveautomation.perspective.gateway.script.PropertyTreeScriptWrapper$MapWrapper'>" or type(value) == dict:
			ret[key] = dashboard.copyDictionary(value)
		else:
			ret[key] = value
	return ret
	
def editDashboard(self, add=True):
	"""
	Initiates the process of adding, editing, or deleting a dashboard.
		
	Args:
		self: Instance object containing session properties and
			  properties from the view from which this was called.
		add: Boolean denoting whether a dashboard is being added.
		
	Returns:
		This function does not have a return value.
	"""
	
	if add:
		# Create a new empty dashboard object and set the 'edit dashboard'
		# object equal to it. Open the 'dashboard details' side panel.
		self.session.custom.dashboard.objects.edit = dashboard.getDashboardObject(True)
		maxId = system.db.runNamedQuery(path="Dashboard/Get URL", parameters={}) + 1
		self.session.custom.dashboard.objects.edit.name = "Dashboard %d" % (maxId)
		self.session.custom.dashboard.objects.edit.url = "dash%d" % (maxId)
		system.perspective.openDock('editDetails',params={'currEdit':self.session.custom.dashboard.objects.edit})
	else:
		# Set the 'edit dashboard' object equal to the current dashboard and
		# then open the 'add edit dashboard' page.
		if self.session.custom.dashboard.objects.current.id == None:
			return
		self.session.custom.dashboard.objects.edit = dashboard.getDashboardObject(self.session.custom.dashboard.objects.current)
		system.perspective.navigate(view="Building Automation Demo/Page/Systems Overview/Framework/Dashboard/Page/Edit/Add Edit Dashboard", params={})

def addUpdateWidget(self):
	"""
	Either updates the position of an existing widget, or creates a
		new widget and appends it to the widgets of the dashboard
		that is currently being edited.
		
	Args:
		self: Instance object containing session properties and
			  properties from the view from which this was called.
		
	Returns:
		This function does not have a return value.
	"""
	
	from java.util import UUID
	sessionWidgets = self.session.custom.dashboard.objects.edit.widgets
	
	foundIds = []
	for row in self.props.widgets:
		positionStr = "%s,%s,%s,%s" % (row.position.rowStart, row.position.rowEnd, row.position.columnStart, row.position.columnEnd)
		
		foundId = False
		for i in range(len(sessionWidgets)):
			if sessionWidgets[i]["id"] == row.viewParams.id:
				# Updating the widget's position string.
				sessionWidgets[i]["position"] = positionStr
				foundIds.append(sessionWidgets[i]["id"])
				foundId = True
				break
		
		if not foundId:
			# Creating a new widget object and appending it to the
			# sessionWidgets list.
			id = UUID.randomUUID()
			sessionWidgets.append({"id":id, 
					"widget_id":row.viewParams.widgetId, 
					"name":row.viewParams.name, 
					"widget":row.viewParams.widgetName, 
					"path":row.viewParams.viewPath, 
					"params": dashboard.copyDictionary(row.viewParams.viewParams), 
					"position":positionStr, 
					"action":{"action":"add", 
							"params":dashboard.copyArray(row.viewParams.editParams)
							}
					})
			foundIds.append(id)

	# Mark the widgets to be removed (when 'save' button is pressed
	# we know which widgets need to be deleted).
	for i in range(len(sessionWidgets)):
		id = sessionWidgets[i]["id"]
		if id not in foundIds:
			sessionWidgets[i]["action"]["action"] = "delete"
			
def sanitizeTree(element):
	"""
	A custom deep copy functon for dicts/lists that converts
		the Perspective property object wrappers to the
		Python equivalent.
		
	Args:
		element: The Perspective property object wrapper.
	
	Returns:
		A deep copy (Python equivalent) of the Perspective
		property object wrapper passed in (element).
	"""
	if hasattr(element, '__iter__'):
		if hasattr(element, 'keys'):
			return dict((k, sanitizeTree(element[k])) for k in element.keys())
		else:
			return list(sanitizeTree(x) for x in element)
	return element


def syncDashboardDB(self):
	"""
	After the user has finished making modifications to a dashboard,
		this handles saving all of the changes to the db (editing
		dashboard details, adding widgets, etc).
		
	Args:
		self: Instance object containing session properties and
			  properties from the view from which this was called.
		
	Returns:
		This function does not have a return value.
	"""

	self.print('Started Dashboard Sync')

	if not self.session.props.auth.authenticated:
		dashboard.showMessage("Please login to create or edit dashboards")
		return
	
	# Get the current 'edit dashboard' object.	
	d = self.session.custom.dashboard.objects.edit
	
	# Get the username of the author.
	username = self.session.custom.dashboard.options.username
	parentId = d.parent_id
	
	# Inform user that dashboard must have a name.
	if d.name == None or d.name == "":
		dashboard.showError("Please enter in a name")
		return
	
	# Inform user that dashboard must have a url.
	if d.url == None or d.url == "":
		dashboard.showError("Please enter in a URL")
		return 
	
	# Check if gps is enabled, and if so, inform
	# user that gps lat/lon/radius must be entered.	
	if not d.gps.enabled:
		d.gps.lat = None
		d.gps.lon = None
		d.gps.radius = None
	else:
		if d.gps.lat == None or d.gps.lon == None or d.gps.radius == None:
			dashboard.showError("Please enter in GPS lat/lon/radius")
			return
	
	# Inform user that grid data must be entered.		
	if d.cellSize == None or d.gridRows == None or d.gridCols == None or d.gridRowGutterSize == None or d.gridColGutterSize == None:
		dashboard.showError("Please enter in grid data (cell size, rows, cols, gutter size)")
		return
	
	# Ensure that url is unique.
	urlId = system.db.runNamedQuery(path="Dashboard/Check URL", parameters={"url":d.url})
	if urlId != None and (d.id == None or d.id != urlId):
		dashboard.showError("URL '%s' already exists. Please try another." % d.url)
		return 
	
	if d.public:
		d.default = False
	
	if d.action.action == "add":
		# Execute 'add' named query to add the new dashboard.
		dashboardOrder = system.db.runNamedQuery(path="Dashboard/Max Order", parameters={"parent_id":-1 if parentId is None else parentId, "show_public":d.public})
		id = system.db.runNamedQuery(path="Dashboard/Add", parameters={"dashboard_order":dashboardOrder, "enabled":True, "gps_enabled":d.gps.enabled, "gps_lat":d.gps.lat, "gps_lon":d.gps.lon, "gps_radius":d.gps.radius, "grid":d.grid, "cell_size":d.cellSize, "grid_rows":d.gridRows, "grid_cols":d.gridCols, "grid_row_gutter_size":d.gridRowGutterSize, "grid_col_gutter_size":d.gridColGutterSize, "icon":d.icon, "name":d.name, "parent_id":parentId, "show_default":d.default, "show_public":d.public, "url":d.url, "username":username}, getKey=True)
	else:
		# Execute the 'edit' named query to edit the dashboard.
		id = d.id
		system.db.runNamedQuery(path="Dashboard/Edit", parameters={"id":id, "dashboard_order":d.order, "enabled":True, "gps_enabled":d.gps.enabled, "gps_lat":d.gps.lat, "gps_lon":d.gps.lon, "gps_radius":d.gps.radius, "grid":d.grid, "cell_size":d.cellSize, "grid_rows":d.gridRows, "grid_cols":d.gridCols, "grid_row_gutter_size":d.gridRowGutterSize, "grid_col_gutter_size":d.gridColGutterSize, "icon":d.icon, "name":d.name, "parent_id":parentId, "show_default":d.default, "show_public":d.public, "url":d.url, "username":username})
				
	if d.default:
		# Update the default dashboard if this is set as default.
		system.db.runNamedQuery(path="Dashboard/Update Default", parameters={"id":id, "username":username})
	
	# Get a list of IDs and widget titles for the non-title widgets.
	nonTitleWidgets = [nonTitleWidget for nonTitleWidget in d.widgets if nonTitleWidget['name'] != 'Title' and nonTitleWidget.action.action != "delete"]
	nonTitleWidgetIDs = []
	nonTitleWidgetTitles = []
	
	for nonTitleWidget in nonTitleWidgets:
		if nonTitleWidget.action.action != "add":
			nonTitleWidgetId = nonTitleWidget.id
		else:
			nonTitleWidgetId = nonTitleWidget.widget_id
		
		nonTitleWidgetTitle = nonTitleWidget.params['widgetTitle']
		
		nonTitleWidgetIDs.append(str(nonTitleWidgetId))
		nonTitleWidgetTitles.append(nonTitleWidgetTitle)
	
	# Add, edit, and delete the widgets based on the changes
	# made by the user.
	for widget in d.widgets:
		widgetId = None
		
		widgetParams = sanitizeTree(widget.params)
		
		# Possibility: widgetA is added to a title widget's list
		# of associated widgets and the dashboard is saved. Then,
		# if widgetA is removed but the user does not manually
		# update the associated widgets list for this title widget,
		# then widgetA will still appear in the list of associated
		# widgets for this title widget. To prevent this from
		# happening, we can check to see if any title widgets contain
		# a deleted widget in their associated widgets list, and if
		# so, we can update the associated widgets list before saving
		# it in the db. Or, another possibility is that the title of
		# widgetA is modified. If this occurs, then we can update the
		# title of the associated widget in the associated widgets list
		# for the user.
		if widget['name'] == 'Title':
			associatedWidgets = widgetParams['associatedWidgets']
			for index,associatedWidget in enumerate(associatedWidgets):
				associatedWidgetInfo = associatedWidget.split(' ')
				widgetId = associatedWidgetInfo[len(associatedWidgetInfo)-1].replace('(','').replace(')','')
				widgetTitle = associatedWidget.split('(' + widgetId + ')')[0][:-1]
				
				# The associated widget was removed.
				if widgetId not in nonTitleWidgetIDs and widgetTitle not in nonTitleWidgetTitles:
					del associatedWidgets[index]
					
				# The title of the associated widget was changed.
				elif widgetId in nonTitleWidgetIDs and widgetTitle not in nonTitleWidgetTitles:
					idIndex = nonTitleWidgetIDs.index(widgetId)
					newAssociatedWidgetTitle = nonTitleWidgetTitles[idIndex]
					
					associatedWidgets[index] = newAssociatedWidgetTitle + ' (' + str(widgetId) + ')'
		
		if 'beingEdited' in widgetParams:	
			# Remove beingEdited and widgetID from params.
			del widgetParams['beingEdited']
			del widgetParams['widgetID']
		
		if widget.action.action == "delete":
			try:
				system.db.runNamedQuery(path="Dashboard/Widget/Delete", parameters={"id":widget.id})
			except:
				pass
		elif widget.action.action == "add":
			viewParamsJson = system.util.jsonEncode(widgetParams, 2)
			widgetId = system.db.runNamedQuery(path="Dashboard/Widget/Add", parameters={"dashboard_id":id, "widget_id":widget.widget_id, "name":widget.name, "parameters":viewParamsJson, "position":widget.position}, getKey=True)
		else:
			widgetId = widget.id
			viewParamsJson = system.util.jsonEncode(widgetParams, 2)
			system.db.runNamedQuery(path="Dashboard/Widget/Edit", parameters={"id":widgetId, "dashboard_id":id, "widget_id":widget.widget_id, "name":widget.name, "parameters":viewParamsJson, "position":widget.position})
	
	# Now that the info regarding this dashboard has been updated
	# in the db, tell the dashboard to refresh itself.
	dashboard.refresh(self)
	
	if d.action.action == "add":
		system.perspective.navigate(page="/dashboard/%s" % d.url)
	else:
		dashboard.back(self)

def deleteDashboard(self):
	"""
	Deletes a dashboard.
		
	Args:
		self: Instance object containing session properties and
			  properties from the view from which this was called.
		
	Returns:
		This function does not have a return value.
	"""
	
	# Only authenticated users can delete dashboards.
	if not self.session.props.auth.authenticated:
		dashboard.showMessage("Please login to remove dashboards")
		return
	
	# Get the id of the 'edit dashboard' and execute 'delete'
	# named query to delete this dashboard from the db.
	id = self.session.custom.dashboard.objects.edit.id
	system.db.runNamedQuery(path="Dashboard/Delete", parameters={"id":id})
	dashboard.refresh(self)
	system.perspective.navigate(page="/")
	
def back(self):
	"""
	Navigates back to the previous page.
		
	Args:
		self: Instance object containing session properties and
			  properties from the view from which this was called.
		
	Returns:
		This function does not have a return value.
	"""
	
	system.perspective.navigate(page=self.page.props.path)
	
def refresh(self, fromSession=False):
	"""
	Refreshes the binding on the dbValid and dashboard.dashboards
		session custom properties. Called when a dashboard has
		been modified.
		
	Args:
		self: Instance object containing session properties and
			  properties from the view from which this was called.
		fromSession: Bool denoting whether this was called from
					 a session.
		
	Returns:
		This function does not have a return value.
	"""
	
	if fromSession:
		obj = self
	else:
		obj = self.session
		
	obj.refreshBinding("custom.dbValid")
	obj.refreshBinding("custom.dashboard.dashboards")
	
def showError(message):
	"""
	Shows an error message in a popup.
		
	Args:
		message: The message to be displayed.
		
	Returns:
		This function does not have a return value.
	"""
	
	dashboard.popupMessage("error", message, "Error_Text")
	
def showMessage(message):
	"""
	Shows a general message in a popup.
		
	Args:
		message: The message to be displayed.
		
	Returns:
		This function does not have a return value.
	"""
	
	dashboard.popupMessage("info", message, "Text")
	
def popupMessage(icon, message, displayClass):
	"""
	Shows a message and icon in a popup.
		
	Args:
		icon: The icon to be displayed.
		message: The message to be displayed.
		displayClass: Style class to be used.
		
	Returns:
		This function does not have a return value.
	"""
	
	params = {"icon":icon, "display":message, "class":displayClass}
	system.perspective.openPopup(id="message", view="Building Automation Demo/Page/Systems Overview/Framework/Dashboard/Page/Popup/Message", params=params, showCloseIcon=True, draggable=False, resizable=True, modal=True, overlayDismiss=False)

def showConfirmation(message, function, params={}):
	"""
	Shows a confirmation message in a popup. Allows for a
		function to be called if the 'Yes' button is pressed.
		
	Args:
		message: The message to be displayed.
		function: The function to execute if the user
				  presses the 'Yes' button.
		params: The params to pass to the function if
				the user presses the 'Yes' button.
		
	Returns:
		This function does not have a return value.
	"""
	
	params = {"icon":"help", "display":message, "class":"Text", "function":{"script":function, "params":params}}
	system.perspective.openPopup(id="confirmation", view="Building Automation Demo/Page/Systems Overview/Framework/Dashboard/Page/Popup/Confirmation", params=params, showCloseIcon=True, draggable=False, resizable=True, modal=True, overlayDismiss=False)
