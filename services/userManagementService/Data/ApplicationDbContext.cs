using Microsoft.EntityFrameworkCore;
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

    public DbSet<User> Users { get; set; } = default!;
    public DbSet<UserInterest> UserInterests { get; set; } = default!;

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);
        
        // Composite key: user_id + interest
        modelBuilder.Entity<UserInterest>()
            .HasKey(ui => new { ui.UserId, ui.Interest });

        // Relationship: one User has many UserInterests
        modelBuilder.Entity<UserInterest>()
            .HasOne(ui => ui.User)
            .WithMany(u => u.UserInterests)
            .HasForeignKey(ui => ui.UserId);
    }
}