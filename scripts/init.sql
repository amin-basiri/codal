IF NOT EXISTS(SELECT * FROM sys.databases WHERE name = '$(SQL_DATABASE)')
  BEGIN
    CREATE DATABASE $(SQL_DATABASE)

    END
    GO
       USE $(SQL_DATABASE)
    GO


-- Check Table Existence
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='$(SQL_TABLE)' and xtype='U')
BEGIN

    -- Financial Statements Table
    CREATE TABLE $(SQL_TABLE) (
        Id INT PRIMARY KEY IDENTITY (1, 1),
        col1 NVARCHAR(500),
        col2 NVARCHAR(500),
        col3 NVARCHAR(500),
        col4 NVARCHAR(500),
        col5 NVARCHAR(500),
        col6 NVARCHAR(500),
        col7 NVARCHAR(500),
        col8 NVARCHAR(500),
        col9 NVARCHAR(500),
        col10 NVARCHAR(500),
        col11 NVARCHAR(500),
        col12 NVARCHAR(500),
        col13 NVARCHAR(500),
        col14 NVARCHAR(500),
        col15 NVARCHAR(500),
        col16 NVARCHAR(500),
        col17 NVARCHAR(500),
        col18 NVARCHAR(500),
        col19 NVARCHAR(500),
        col20 NVARCHAR(500),
        col21 NVARCHAR(500),
        col22 NVARCHAR(500),
        col23 NVARCHAR(500),
        col24 NVARCHAR(500),
        col25 NVARCHAR(500),
        col26 NVARCHAR(500),
        col27 NVARCHAR(500),
        col28 NVARCHAR(500),
        col29 NVARCHAR(500),
        col30 NVARCHAR(500),
        col31 NVARCHAR(500),
        col32 NVARCHAR(500),
        col33 NVARCHAR(500),
        col34 NVARCHAR(500),
        col35 NVARCHAR(500)
    )
END