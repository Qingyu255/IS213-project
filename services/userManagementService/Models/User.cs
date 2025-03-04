using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using Microsoft.EntityFrameworkCore;

namespace user_management_service.Models;

[Table("users")]
[Index(nameof(Username), IsUnique = true)]
public class User
{
    [Key] // Declare that column of id is the primary key
    [Column("id")]
    public string Id { get; set; }

    [Column("username")]
    public string Username { get; set; } // This is an unique candidate key

    [Column("email")]
    public string Email { get; set; }
    
    [Column("created_at")]
    public DateTime CreatedAt { get; set; }

    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; }
}