using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Storage.ValueConversion;
using user_management_service.Models;

namespace user_management_service.Repository;

public class ApplicationDbContext : DbContext
{
    // If you still want to use IConfiguration and ILogger, you can inject them as needed,
    // but the DbContextOptions are the key for DI configuration.
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options)
    {
    }

    public DbSet<User> Users { get; set; }
}