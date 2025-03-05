using System.ComponentModel.DataAnnotations.Schema;
using System.ComponentModel.DataAnnotations;

namespace user_management_service.Models;

[Table("user_interests")]
public class UserInterest
{
    [Key, Column("user_id", Order = 0)]
    public string UserId { get; set; } = default!;

    [Key, Column("interest", Order = 1)]
    public string Interest { get; set; } = default!;

    // Navigation property to the User entity
    // Note: Not strictly required if you only need the table
    // but it's useful if you want to Include(...) in queries
    public User User { get; set; } = default!;
}
