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
	CREATE TABLE [dbo].[widgets](
		[id] [int] IDENTITY(1,1) NOT NULL,
		[name] [nvarchar](50) NOT NULL,
		[path] [nvarchar](max) NOT NULL,
		[icon] [nvarchar](50) NOT NULL,
		[alias] [nvarchar](50) NOT NULL,
		[parameters] [nvarchar](max) NOT NULL,
	 CONSTRAINT [PK_widgets] PRIMARY KEY CLUSTERED 
	(
		[id] ASC
	)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
	) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
	""")
	
	queries.append("""
	CREATE TABLE [dbo].[dashboards](
		[id] [int] IDENTITY(1,1) NOT NULL,
		[parent_id] [int] NULL,
		[name] [nvarchar](50) NOT NULL,
		[icon] [nvarchar](50) NULL,
		[url] [nvarchar](200) NOT NULL,
		[enabled] [bit] NOT NULL,
		[show_public] [bit] NOT NULL,
		[show_default] [bit] NOT NULL,
		[username] [nvarchar](50) NULL,
		[gps_enabled] [bit] NOT NULL,
		[gps_lat] [decimal](11, 8) NULL,
		[gps_lon] [decimal](11, 8) NULL,
		[gps_radius] [decimal](11, 8) NULL,
		[grid] [nvarchar](50) NOT NULL,
	    [cell_size] [int] NOT NULL,
	    [grid_rows] [int] NOT NULL,
	    [row_gutter_size] [int] NOT NULL,
	    [grid_cols] [int] NOT NULL,
	    [col_gutter_size] [int] NOT NULL,
		[dashboard_order] [int] NOT NULL,
		[last_modified] [datetime] NOT NULL,
	 CONSTRAINT [PK_dashboards] PRIMARY KEY CLUSTERED 
	(
		[id] ASC
	)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
	) ON [PRIMARY]
	""")
	
	queries.append("""
	ALTER TABLE [dbo].[dashboards] ADD  CONSTRAINT [DF_dashboards_enabled]  DEFAULT ((1)) FOR [enabled]
	""")
	
	queries.append("""
	ALTER TABLE [dbo].[dashboards] ADD  CONSTRAINT [DF_dashboards_show_public]  DEFAULT ((1)) FOR [show_public]
	""")
	
	queries.append("""
	ALTER TABLE [dbo].[dashboards] ADD  CONSTRAINT [DF_dashboards_show_default]  DEFAULT ((0)) FOR [show_default]
	""")
	
	queries.append("""
	ALTER TABLE [dbo].[dashboards] ADD  CONSTRAINT [DF_dashboards_gps_enabled]  DEFAULT ((0)) FOR [gps_enabled]
	""")

	queries.append("""
	ALTER TABLE [dbo].[dashboards] ADD  CONSTRAINT [DF_dashboards_grid]  DEFAULT (('fixed')) FOR [grid]
	""")
	
	queries.append("""
	ALTER TABLE [dbo].[dashboards] ADD  CONSTRAINT [DF_dashboards_cell_size]  DEFAULT ((100)) FOR [cell_size]
	""")
	
	queries.append("""
	ALTER TABLE [dbo].[dashboards] ADD  CONSTRAINT [DF_dashboards_grid_rows]  DEFAULT ((10)) FOR [grid_rows]
	""")
	
	queries.append("""
	ALTER TABLE [dbo].[dashboards] ADD  CONSTRAINT [DF_dashboards_row_gutter_size]  DEFAULT ((6)) FOR [row_gutter_size]
	""")
	
	queries.append("""
	ALTER TABLE [dbo].[dashboards] ADD  CONSTRAINT [DF_dashboards_grid_cols]  DEFAULT ((10)) FOR [grid_cols]
	""")
	
	queries.append("""
	ALTER TABLE [dbo].[dashboards] ADD  CONSTRAINT [DF_dashboards_col_gutter_size]  DEFAULT ((6)) FOR [col_gutter_size]
	""")

	queries.append("""
	ALTER TABLE [dbo].[dashboards] ADD  CONSTRAINT [DF_dashboards_dashboard_order]  DEFAULT ((1)) FOR [dashboard_order]
	""")
	
	queries.append("""
	ALTER TABLE [dbo].[dashboards]  WITH CHECK ADD  CONSTRAINT [FK_dashboards_dashboards] FOREIGN KEY([parent_id])
	REFERENCES [dbo].[dashboards] ([id])
	""")
	
	queries.append("""
	ALTER TABLE [dbo].[dashboards] CHECK CONSTRAINT [FK_dashboards_dashboards]
	""")
	
	queries.append("""
	CREATE NONCLUSTERED INDEX [IX_dashboards] ON [dbo].[dashboards]
	(
		[enabled] ASC
	)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON)
	""")
	
	queries.append("""
	CREATE NONCLUSTERED INDEX [IX_dashboards_1] ON [dbo].[dashboards]
	(
		[show_public] ASC
	)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON)
	""")
		
	queries.append("""
	CREATE NONCLUSTERED INDEX [IX_dashboards_2] ON [dbo].[dashboards]
	(
		[username] ASC
	)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON)
	""")
	
	queries.append("""
	CREATE TABLE [dbo].[dashboard_widgets](
		[id] [int] IDENTITY(1,1) NOT NULL,
		[dashboard_id] [int] NOT NULL,
		[widget_id] [int] NOT NULL,
		[name] [nvarchar](50) NOT NULL,
		[parameters] [nvarchar](max) NOT NULL,
		[position] [nvarchar](50) NOT NULL,
	 CONSTRAINT [PK_dashboard_widgets] PRIMARY KEY CLUSTERED 
	(
		[id] ASC
	)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
	) ON [PRIMARY]
	""")
	
	queries.append("""
	ALTER TABLE [dbo].[dashboard_widgets]  WITH CHECK ADD  CONSTRAINT [FK_dashboard_widgets_dashboards] FOREIGN KEY([dashboard_id])
	REFERENCES [dbo].[dashboards] ([id])
	ON DELETE CASCADE
	""")
	
	queries.append("""
	ALTER TABLE [dbo].[dashboard_widgets] CHECK CONSTRAINT [FK_dashboard_widgets_dashboards]
	""")
	
	queries.append("""
	ALTER TABLE [dbo].[dashboard_widgets]  WITH CHECK ADD  CONSTRAINT [FK_dashboard_widgets_widgets] FOREIGN KEY([widget_id])
	REFERENCES [dbo].[widgets] ([id])
	""")
	
	queries.append("""
	ALTER TABLE [dbo].[dashboard_widgets] CHECK CONSTRAINT [FK_dashboard_widgets_widgets]
	""")
	
	return queries
