namespace user_management_service.DTOs;

public class CreateUserDto
{
    public string Username { get; set; }
    public string Email { get; set; }
    public string Password { get; set; }
}