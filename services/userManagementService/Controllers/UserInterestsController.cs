using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using user_management_service.Repositories;

namespace user_management_service.Controllers;

[ApiController]
[Route("api/userinterests")]
public class UserInterestsController : ControllerBase
{
    private readonly IUserInterestRepository _userInterestRepository;
    private readonly IUserRepository _userRepository;

    public UserInterestsController(IUserInterestRepository userInterestRepository, IUserRepository userRepository)
    {
        _userInterestRepository = userInterestRepository;
        _userRepository = userRepository;
    }

    [Authorize]
    [HttpGet("user/{userId}")]
    public async Task<ActionResult<List<string>>> GetUserInterests([FromRoute] string userId)
    {
        var user = await _userRepository.GetUserByIdAsync(userId);
        if (user == null)
        {
            return NotFound(new
            {
                message = $"User with ID {userId} not found."
            });
        };

        var interests = await _userInterestRepository.GetUserInterestsAsync(userId);
        return Ok(interests);
    }

    [Authorize]
    [HttpPost("user/{userId}")]
    public async Task<IActionResult> UpsertUserInterests(
        [FromRoute] string userId,
        [FromBody] List<string> interestList)
    {
        try
        {
            var user = await _userRepository.GetUserByIdAsync(userId);
            if (user == null)
            {
                return NotFound(new
                {
                    message = $"User with ID {userId} not found."
                });
            };

            await _userInterestRepository.UpsertUserInterestsAsync(userId, interestList);
            return Ok("Interests updated successfully.");
        }
        catch (Exception ex)
        {
            return BadRequest(new { error = ex.Message });
        }
    }

    [HttpGet("getusers/{interest}")] // TODO: Authorisation here must check if its from the composite servivce role
    [AllowAnonymous] // For testing; TODO: enforce authorisation when create events composite has auth up
    public async Task<IActionResult> GetUsersByInterest([FromRoute] string interest)
    {
        var users = await _userInterestRepository.GetUsersByInterestAsync(interest);
        return Ok(users);
    }
}