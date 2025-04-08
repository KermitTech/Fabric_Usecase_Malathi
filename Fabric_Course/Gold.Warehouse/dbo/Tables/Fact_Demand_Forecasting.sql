CREATE TABLE [dbo].[Fact_Demand_Forecasting] (

	[date_key] date NULL, 
	[month_key] int NULL, 
	[year_key] int NULL, 
	[product_key] varchar(100) NULL, 
	[store_key] varchar(100) NULL, 
	[total_quantity_sold] int NULL, 
	[total_quantity_shipped] int NULL, 
	[quantity_in_stock] int NULL, 
	[stock_level] int NULL, 
	[predicted_sales] decimal(10,2) NULL
);