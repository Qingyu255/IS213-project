using Amazon.CognitoIdentityProvider;
using Amazon.CognitoIdentityProvider.Model;
using user_management_service.DTOs;

namespace user_management_service.Services;

public class CognitoService
{
    private readonly IAmazonCognitoIdentityProvider _cognitoClient;
    private readonly string _userPoolId;
    private readonly string _clientId;

    public CognitoService(IAmazonCognitoIdentityProvider cognitoClient, string userPoolId, string clientId)
    {
        _cognitoClient = cognitoClient;
        _userPoolId = userPoolId;
        _clientId = clientId;
    }

    /// <summary>
    /// Creates user with attributes: username and password (password only stored in aws cognito not our service)
    /// </summary>
    /// <param name="createUserDto"></param>
    /// <returns></returns>
    public async Task<SignUpResponse> CreateUserAsync(string userUuid, CreateUserDto createUserDto)
    {
        // Create the user in Cognito with a temporary password
        var request = new SignUpRequest
        {
            ClientId = _clientId,
            Username = createUserDto.Username,
            Password = createUserDto.Password, 
            UserAttributes = new List<AttributeType>
            {
                new AttributeType { Name = "email", Value = createUserDto.Email},
                new AttributeType { Name = "custom:id", Value = userUuid},
            },
        };

        return await _cognitoClient.SignUpAsync(request);
    }

    public async Task<AdminDeleteUserResponse> DeleteUserAsync(string username)
    {
        var request = new AdminDeleteUserRequest()
        {
            UserPoolId = _userPoolId,
            Username = username,
        };

        return await _cognitoClient.AdminDeleteUserAsync(request);
    }

    /// <summary>
    /// This method updates a user's email
    /// </summary>
    /// <param name="updateUserDto"></param>
    /// <returns></returns>
    public async Task<AdminUpdateUserAttributesResponse> UpdateUserAsync(string username, UpdateUserDto updateUserDto)
    {
        // TODO: allow update username?
        var request = new AdminUpdateUserAttributesRequest()
        {
            UserPoolId = _userPoolId,
            Username = username,
            UserAttributes = new List<AttributeType>
            {
                new AttributeType { Name = "email", Value = updateUserDto.Email},
            }
            
        };
        return await _cognitoClient.AdminUpdateUserAttributesAsync(request);
    }
}