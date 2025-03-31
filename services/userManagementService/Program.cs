using System.IdentityModel.Tokens.Jwt;
using Amazon.CognitoIdentityProvider;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using user_management_service.Constants;
using user_management_service.Repositories;
using user_management_service.Repository;
using user_management_service.Services;
using Prometheus; 

var builder = WebApplication.CreateBuilder(args);

// Add CORS services
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowSpecificOrigins", policy =>
    {
        policy.WithOrigins("http://localhost:3000", "https://itsag3t2.com")
            .AllowAnyHeader()
            .AllowAnyMethod();
    });
});

// Add services to the container.
// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle

// Database setup
var connectionString = builder.Configuration.GetConnectionString("PostgresDbConnectionString");
// Register ApplicationDbContext with DI using the PostgreSQL provider
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseNpgsql(connectionString));

// Authentication
var awsCognitoRegion = builder.Configuration["AWS_COGNITO_REGION"];
var awsCognitoUserPoolId = builder.Configuration["AWS_COGNITO_USER_POOL_ID"];
var awsCognitoAppClientId = builder.Configuration["AWS_COGNITO_APP_CLIENT_ID"];

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer("Bearer", options =>
        {
            options.Authority = $"https://cognito-idp.{awsCognitoRegion}.amazonaws.com/{awsCognitoUserPoolId}";

            options.TokenValidationParameters = new TokenValidationParameters()
            {
                // Validate that the issuer (who created the token) is your Cognito User Pool.
                ValidateIssuer = true,
                ValidIssuer = $"https://cognito-idp.{awsCognitoRegion}.amazonaws.com/{awsCognitoUserPoolId}",

                // Disable built-in audience validation since "aud" is empty.
                ValidateAudience = false,

                // Ensure the token hasn't expired.
                ValidateLifetime = true,

                // Optionally validate the signing key (usually handled automatically with metadata).
                ValidateIssuerSigningKey = true
            };
            // Verify Cognito ClientId
            options.Events = new JwtBearerEvents
            {
                OnTokenValidated = async context =>
                {
                    if (context.SecurityToken is JwtSecurityToken jwt)
                    {
                        // Manually check the "client_id" claim.
                        var clientId = jwt.Claims.FirstOrDefault(c => c.Type == "client_id")?.Value;
                        if (clientId != awsCognitoAppClientId)
                        {
                            context.Fail("Invalid Cognito ClientId: client_id mismatch");
                        }
                    }
                    await Task.CompletedTask;
                }
            };
        }
    );

// Authorisation
builder.Services.AddAuthorization(options =>
{
    // Policy for endpoints that should be accessible only by admins and rootadmins
    options.AddPolicy(Policies.AdminsOnly, policy =>
    {
        // Require that the token has a "cognito:groups" claim with one of these values
        policy.RequireClaim("cognito:groups", "rootadmin", "admin");
    });
});

// AWS Cognito
// Register AWS Cognito Identity Provider uing AWS Extensions
builder.Services.AddSingleton<IAmazonCognitoIdentityProvider, AmazonCognitoIdentityProviderClient>();

// Register CognitoService
builder.Services.AddScoped<CognitoService>(sp =>
{
    var cognitoClient = sp.GetRequiredService<IAmazonCognitoIdentityProvider>();
    var configuration = sp.GetRequiredService<IConfiguration>();
    var userPoolId = configuration["AWS_COGNITO_USER_POOL_ID"];
    var clientId = configuration["AWS_COGNITO_APP_CLIENT_ID"];
    return new CognitoService(cognitoClient, userPoolId, clientId);
});

// Repositories
builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddScoped<IUserInterestRepository, UserInterestRepository>();

builder.Logging.AddConsole();
builder.Logging.AddDebug();

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Log all incoming requests
app.Use(async (context, next) =>
{
    var logger = context.RequestServices.GetRequiredService<ILogger<Program>>();
    logger.LogInformation("Incoming Request: {Method} {Path}", context.Request.Method, context.Request.Path);
    
    var stopwatch = System.Diagnostics.Stopwatch.StartNew();
    await next.Invoke();
    stopwatch.Stop();

});

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseCors("AllowSpecificOrigins");

// Use Prometheus metrics collection
app.UseMetricServer();
app.UseHttpMetrics();

app.MapControllers();

app.Run();