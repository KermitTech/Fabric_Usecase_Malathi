CREATE TABLE [dbo].[Fact_Sales] (

	[transaction_id] int NULL, 
	[customer_id] int NULL, 
	[date_key] date NULL, 
	[month_key] int NULL, 
	[year_key] int NULL, 
	[product_key] varchar(100) NULL, 
	[store_key] varchar(100) NULL, 
	[quantity] int NULL, 
	[unit_price] decimal(18,2) NULL, 
	[discount] decimal(18,2) NULL, 
	[total_amount] decimal(18,2) NULL
);