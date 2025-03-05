# run when there are new schema changes
dotnet ef migrations add add-username-column-to-users-table
dotnet ef database update
