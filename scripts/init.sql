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
    CREATE TABLE $(SQL_TABLE) (
        Id INT PRIMARY KEY IDENTITY (1, 1),
        col1 NVARCHAR(MAX),
        col2 NVARCHAR(MAX),
        col3 NVARCHAR(MAX),
        col4 NVARCHAR(MAX),
        col5 NVARCHAR(MAX),
        col6 NVARCHAR(MAX),
        col7 NVARCHAR(MAX),
        col8 NVARCHAR(MAX),
        col9 NVARCHAR(MAX),
        col10 NVARCHAR(MAX),
        col11 NVARCHAR(MAX),
    )
END