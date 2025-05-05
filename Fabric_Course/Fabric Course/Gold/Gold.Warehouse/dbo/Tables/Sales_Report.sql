CREATE TABLE [dbo].[Sales_Report] (

	[month_key] int NULL, 
	[year_key] int NULL, 
	[date_key] date NULL, 
	[category] varchar(100) NULL, 
	[product_name] varchar(255) NULL, 
	[store_id] varchar(100) NULL, 
	[city] varchar(100) NULL, 
	[revenue] decimal(38,2) NULL
);