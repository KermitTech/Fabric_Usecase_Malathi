CREATE TABLE [dbo].[Fact_Demand_Predictions] (

	[product_id] varchar(8000) NULL, 
	[store_id] varchar(8000) NULL, 
	[Date] datetime2(6) NULL, 
	[year] int NULL, 
	[DayOfWeek] int NULL, 
	[month] int NULL, 
	[prediction] float NULL
);