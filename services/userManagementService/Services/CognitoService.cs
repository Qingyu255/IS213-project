using Amazon.CognitoIdentityProvider;
using Amazon.CognitoIdentityProvider.Model;
using user_management_service.DTOs;

namespace user_management_service.Services;

public class CognitoService
{
    private readonly IAmazonCognitoIdentityProvider _cognitoClient;
    private readonly string _userPoolId;

    public CognitoService(IAmazonCognitoIdentityProvider cognitoClient, string userPoolId)
    {
        _cognitoClient = cognitoClient;
        _userPoolId = userPoolId;
    }

    /// <summary>
    /// Creates user with attributes: email, firstname, lastname, role
    /// </summary>
    /// <param name="createUserDto"></param>
    /// <returns></returns>
    public async Task<AdminCreateUserResponse> CreateUserAsync(CreateUserDto createUserDto)
    {
        // // Check if role is specified; throw an error if not.
        // if (string.IsNullOrEmpty(createUserDto.Role))
        // {
        //     throw new Exception("Role must be specified in the CreateUserDto");
        // }

        // Create the user in Cognito
        var request = new AdminCreateUserRequest
        {
            UserPoolId = _userPoolId,
            Username = createUserDto.Username,
            UserAttributes = new List<AttributeType>
            {
                new AttributeType { Name = "email", Value = createUserDto.Email},
            },
            
            DesiredDeliveryMediums = new List<string>{"EMAIL"},
        };

        return await _cognitoClient.AdminCreateUserAsync(request);

        // // Add the user to the specified group in cognito
        // var addGroupRequest = new AdminAddUserToGroupRequest
        // {
        //     UserPoolId = _userPoolId,
        //     Username = createUserDto.Username,
        //     GroupName = createUserDto.Role
        // };
        //
        // return await _cognitoClient.AdminAddUserToGroupAsync(addGroupRequest);
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
    /// This method updates a user's email, firstname, lastname
    /// </summary>
    /// <param name="updateUserDto"></param>
    /// <returns></returns>
    public async Task<AdminUpdateUserAttributesResponse> UpdateUserAsync(string username, UpdateUserDto updateUserDto)
    {
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