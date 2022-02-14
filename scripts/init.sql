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
    )
END