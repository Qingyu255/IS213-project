using System.Net;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using user_management_service.Constants;
using user_management_service.DTOs;
using user_management_service.Models;
using user_management_service.Repositories;
using user_management_service.Services;

namespace user_management_service.Controllers;

[ApiController]
[Route("api/users")]
public class UserController : ControllerBase // Inherit controller base
{
    private readonly IUserRepository _userRepository;
    private readonly CognitoService _cognitoService;
    private readonly ILogger<UserController> _logger;

    public UserController(IUserRepository userRepository, CognitoService cognitoService, ILogger<UserController> logger, IConfiguration configuration)
    {
        _userRepository = userRepository;
        _cognitoService = cognitoService;
        _logger = logger;
    }

    // [HttpGet("getall")]
    // [Authorize(Policy = Policies.AdminsOnly)]
    // public async Task<IActionResult> GetAllUsers()
    // {
    //     var users = await _userRepository.GetAllUsersAsync();
    //
    //     if (!User.IsInRole("rootadmin")) // only rootadmin can see all users; other roles cannot see rootadmin
    //     {
    //         users = users.Where(u => u.Role != "rootadmin").ToList();
    //     }
    //
    //     return Ok(users);
    // }

    [HttpGet("{userId}")]
    [Authorize]
    public async Task<IActionResult> GetUserById([FromRoute] string userId)
    {
        // TODO: If not an admin, ensure that the user is only querying their own data.
        // if (!isAdmin)
        // {
        //     var currentUserId = User.FindFirst("sub")?.Value;
        //     if (currentUserId != userId)
        //     {
        //         return Forbid();
        //     }
        // }

        var user = await _userRepository.GetUserByIdAsync(userId); // use .ToList() due to deferred execution
        if (user != null)
        {
            return Ok(user);
        };

        return NotFound(new
        {
            message = $"User with ID {userId} not found."
        });
    }

    [HttpPost("create")]
    [AllowAnonymous] // This is a public endpoint and will be excluded from the JWT token validation
    public async Task<IActionResult> CreateUser([FromBody] CreateUserDto createUserDto)
    {
        // Check if user with username already exists
        var user = await _userRepository.GetUserByUsernameAsync(createUserDto.Username);
        _logger.LogInformation(user?.ToString());
        if (user != null)
        {
            return BadRequest(new
                {
                    error = string.Format(ErrorMessages.UserExists, createUserDto.Username)
                }
            );
        }

        // And check if user with email already exists
        if (user == null)
        {
            user = await _userRepository.GetUserByEmailAsync(createUserDto.Email);
            if (user != null)
            {
                return BadRequest(new
                    {
                        error = string.Format(ErrorMessages.UserEmailExists, createUserDto.Email)
                    }
                );
            }
        }

        var newUser = new User
        {
            Id = Guid.NewGuid().ToString(),
            Username = createUserDto.Username,
            Email = createUserDto.Email,
        };

        // Step 1: Create user in Cognito
        try
        {
            await _cognitoService.CreateUserAsync(createUserDto);
            _logger.LogInformation($"Successfully created user of username={newUser.Username} in cognito service");
        }
        catch (Exception e)
        {
            var errorStr = $"Error creating user of username={newUser.Username} in cognito service: {e}";
            _logger.LogError(errorStr);
            return StatusCode((int)HttpStatusCode.InternalServerError, errorStr);
        }

        // Step 2: Persist to db
        try
        {
            await _userRepository.CreateUserAsync(newUser);
            _logger.LogInformation($"Successfully created user record in postgres db for user of username={newUser.Username}");
        }
        catch (Exception dbEx)
        {
            // Delete the user from Cognito since DB persistence failed
            try
            {
                _logger.LogInformation("Attempting to delete the user from Cognito since postgres DB persistence failed");
                await _cognitoService.DeleteUserAsync(newUser.Username);
            }
            catch (Exception e)
            {
                var errorStr = $"Error deleting Cognito user of username={newUser.Username}";
                _logger.LogCritical(e, errorStr);
                return StatusCode((int)HttpStatusCode.InternalServerError, errorStr);
            }

            return StatusCode((int)HttpStatusCode.InternalServerError,
                $"Error creating user of username={newUser.Username} in database: {dbEx}.");
        }

        return CreatedAtAction(nameof(GetUserById), new { userId = newUser.Id }, newUser);
    }

    [HttpPut("update/{userId}")]
    [Authorize(Policy = Policies.AdminsOnly)]
    public async Task<IActionResult> UpdateUser(string userId, [FromBody] UpdateUserDto updateUserDto)
    {
        var user = await _userRepository.GetUserByIdAsync(userId);
        // Check if user exists and prevent update if the user to be updated is a rootadmin
        if (user != null)
        {
            // Step 1: Update user details in Cognito
            try
            {
                await _cognitoService.UpdateUserAsync(user.Username, updateUserDto);
                _logger.LogInformation($"Successfully updated details of user of username={user.Username} in cognito service");
            }
            catch (Exception e)
            {
                var errorStr = $"Error updating details of user of username={user.Username} in cognito service: {e}";
                _logger.LogError(errorStr);
                return StatusCode((int)HttpStatusCode.InternalServerError, errorStr);
            }

            // Step 2: Update user record in db
            // Update existing user properties
            user.Email = updateUserDto.Email;
            try
            {
                await _userRepository.UpdateUserAsync(user);
                _logger.LogInformation($"Successfully updated user record in postgres db for user of username={user.Username}");
            }
            catch (Exception dbEx)
            {
                _logger.LogCritical(dbEx, $"Error updating Cognito user of username={user.Username}");
                return StatusCode((int)HttpStatusCode.InternalServerError,
                    $"Error deleting user of username={user.Username} in database: {dbEx}.");
            }

            return Ok(new
            {
                message = $"User with ID: {userId} and username: {user.Username} updated successfully."
            });
        }

        return NotFound(new
        {
            message = $"User with ID {userId} not found."
        });
    }

    [HttpDelete("delete/{userId}")]
    // [Authorize(Policy = Policies.AdminsOnly)]
    public async Task<IActionResult> DeleteUser([FromRoute] string userId)
    {
        var user = await _userRepository.GetUserByIdAsync(userId);
        // First check if user exists
        if (user != null)
        {
            // // Forbid deletion if the user to be deleted is a rootadmin
            // if (user.Role.ToLower() == Roles.RootAdmin)
            // {
            //     return Forbid(ErrorMessages.RootAdminDeletion);
            // }

            _logger.LogInformation("User making request has 'AdminsOnly' access and is authorised to delete users."); // should make this such that only user themselves can delete their own acc
            // Deletion authorised, delete user record in db
            // Step 1: Delete user in Cognito
            try
            {
                await _cognitoService.DeleteUserAsync(user.Username);
                _logger.LogInformation($"Successfully deleted user of username={user.Username} in cognito service");
            }
            catch (Exception e)
            {
                var errorStr = $"Error deleting user of username={user.Username} from postgres db but deleted from cognito: {e}"; // This is a highly unlikely case
                _logger.LogError(errorStr);
                return StatusCode((int)HttpStatusCode.InternalServerError, errorStr);
            }

            // Step 2: Delete user record from db
            try
            {
                await _userRepository.DeleteUserAsync(user.Id);
                _logger.LogInformation($"Successfully deleted user record in postgres db for user of username={user.Username}");
            }
            catch (Exception dbEx)
            {
                _logger.LogCritical(dbEx, $"Error deleting Cognito user of username={user.Username}");
                return StatusCode((int)HttpStatusCode.InternalServerError,
                    $"Error deleting user of username={user.Username} in database: {dbEx}.");
            }
            return Ok(new
            {
                message = $"User with ID: {userId} and username: {user.Username} deleted successfully."
            });
        }
        return NotFound(new
        {
            message = $"User with ID {userId} not found."
        });
    }
}

public static class ErrorMessages
{
    public const string UserExists = "User with username {0} already exists!";
    public const string UserEmailExists = "User with email {0} already exists!";
}