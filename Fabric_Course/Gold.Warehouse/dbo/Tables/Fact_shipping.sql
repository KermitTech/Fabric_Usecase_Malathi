CREATE TABLE [dbo].[Fact_shipping] (

	[product_id] bigint NULL, 
	[shipping_id] bigint NULL, 
	[quantity_shipped] bigint NULL, 
	[store_id] varchar(8000) NULL, 
	[shipping_date] datetime2(6) NULL
);