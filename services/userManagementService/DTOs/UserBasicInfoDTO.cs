namespace user_management_service.DTOs;

public class UserBasicInfoDTO
{
    public string Id { get; set; } = default!;
    public string Username { get; set; } = default!;
    public string Email { get; set; } = default!;
}