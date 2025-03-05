namespace user_management_service.Constants;

public static class Roles
{
    public const string RootAdmin = "rootadmin";
    public const string Admin = "admin";
    public const string Agent = "agent";

    public static readonly HashSet<string> AllowedRoles = new(StringComparer.OrdinalIgnoreCase)
    {
        Admin,
        Agent
    };
}