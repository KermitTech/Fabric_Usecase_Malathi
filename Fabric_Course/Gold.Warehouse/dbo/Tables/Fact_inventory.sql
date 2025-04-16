CREATE TABLE [dbo].[Fact_inventory] (

	[inventory_id] int NULL, 
	[product_id] int NULL, 
	[store_id] varchar(8000) NULL, 
	[quantity_in_stock] int NULL, 
	[inventory_date] date NULL
);