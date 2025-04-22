CREATE TABLE [dbo].[Dim_Customer] (

	[customer_id] varchar(100) NULL, 
	[customer_name] varchar(255) NULL, 
	[email] varchar(255) NULL, 
	[phone] varchar(50) NULL, 
	[address] varchar(255) NULL, 
	[social_security_number] varchar(50) NULL, 
	[date_of_birth] date NULL, 
	[age] int NULL, 
	[gender] varchar(10) NULL
);