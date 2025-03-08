using Microsoft.EntityFrameworkCore;
using user_management_service.DTOs;
using user_management_service.Models;
using user_management_service.Repository;

namespace user_management_service.Repositories;

public interface IUserInterestRepository
{
    Task<List<string>> GetUserInterestsAsync(string userId);
    Task UpsertUserInterestsAsync(string userId, List<string> interests);
    Task<List<UserBasicInfoDTO>> GetUsersByInterestAsync(string interest);
}

public class UserInterestRepository : IUserInterestRepository
{
    private readonly ApplicationDbContext _context;

    public UserInterestRepository(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<List<string>> GetUserInterestsAsync(string userId)
    {
        var user = await _context.Users
            .Include(u => u.UserInterests)
            .FirstOrDefaultAsync(u => u.Id == userId);

        return user.UserInterests.Select(ui => ui.Interest).ToList();
    }

    public async Task UpsertUserInterestsAsync(string userId, List<string> interests)
    {
        var user = await _context.Users
            .Include(u => u.UserInterests)
            .FirstOrDefaultAsync(u => u.Id == userId);

        // Remove interests that are not in the new list
        var toRemove = user.UserInterests.Where(ui => !interests.Contains(ui.Interest)).ToList();
        foreach (var interest in toRemove)
        {
            user.UserInterests.Remove(interest);
        }

        // Add new interests that aren't already associated with the user
        var existingInterests = user.UserInterests.Select(ui => ui.Interest).ToList();
        var newInterests = interests.Except(existingInterests).ToList();

        foreach (var interest in newInterests)
        {
            user.UserInterests.Add(new UserInterest
            {
                UserId = userId,
                Interest = interest
            });
        }

        await _context.SaveChangesAsync();
    }

    public async Task<List<UserBasicInfoDTO>> GetUsersByInterestAsync(string interest)
    {
        // Eagerly load UserInterests so we can filter by interest.
        return await _context.Users
            .Where(u => u.UserInterests.Any(ui => ui.Interest == interest))
            .Select(u => new UserBasicInfoDTO
            {
                Id = u.Id,
                Username = u.Username,
                Email = u.Email
            })
            .ToListAsync();
    }
}