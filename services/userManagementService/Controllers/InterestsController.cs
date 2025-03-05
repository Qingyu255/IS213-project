using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using user_management_service.Models;
using user_management_service.Repository;

namespace user_management_service.Controllers;

[ApiController]
[Route("api/[controller]")]
public class UserInterestsController : ControllerBase
{
    private readonly ApplicationDbContext _dbContext;

    public UserInterestsController(ApplicationDbContext dbContext)
    {
        _dbContext = dbContext;
    }

    // Get all interests for a given user
    // e.g., GET /api/userinterests/user/123
    [HttpGet("user/{userId}")]
    public async Task<ActionResult<List<string>>> GetUserInterests([FromRoute] string userId)
    {
        var user = await _dbContext.Users
            .Include(u => u.UserInterests)
            .FirstOrDefaultAsync(u => u.Username == userId);

        if (user == null)
            return NotFound($"User with ID '{userId}' not found.");

        // Return just the list of interest strings
        var interests = user.UserInterests.Select(ui => ui.Interest).ToList();
        return Ok(interests);
    }

    // Upsert user interests (as list of strings)
    // e.g., POST /api/userinterests/user/123 with body ["Music", "Sports"]
    [HttpPost("user/{userId}")]
    public async Task<IActionResult> UpsertUserInterests(
        [FromRoute] string userId,
        [FromBody] List<string> interestList)
    {
        var user = await _dbContext.Users
            .Include(u => u.UserInterests)
            .FirstOrDefaultAsync(u => u.Id == userId);

        if (user == null)
            return NotFound($"User with ID '{userId}' not found.");

        // Remove existing associations that are NOT in the new list
        var existingInterests = user.UserInterests.Select(ui => ui.Interest).ToList();
        user.UserInterests = user.UserInterests.Where(i => existingInterests.Contains(i.Interest))
            .ToList();

        // Add new interests that don't exist yet
        var newInterests = interestList.Except(existingInterests).ToList();

        foreach (var interest in newInterests)
            user.UserInterests.Add(new UserInterest
            {
                UserId = userId,
                Interest = interest
            });

        await _dbContext.SaveChangesAsync();
        return Ok("Interests updated successfully.");
    }
}