# Database Migrations with Flyway

We use [Flyway](https://flywaydb.org/documentation) to manage database schema changes across our microservices. Flyway helps ensure that every environment (development, staging, and production) maintains a consistent database state through version-controlled migrations.

>**Note:** All database changes have to go through a Flyway migration script. This centralized approach ensures consistency and traceability across all microservices and environments.

## Folder Structure

Each microservice that owns its database should include a dedicated migrations directory. A common pattern is:

```
/
├── database/
│   └── migration/
│       ├── V202503031230__init_schema.sql
│       ├── V202503041015__another_migration_1.sql
│       └── V202503051200__another_migration_2.sql
```

## Version Naming Convention

We use a timestamp-based naming scheme with a `V` prefix in the format `Vyyyymmddhhmm` to indicate when each migration was created. For example, `V202503031230__initial_setup.sql` indicates a migration created on March 3, 2025, at 12:30.

**Guidelines:**
- **Prefix and Timestamp:** Use a `V` prefix followed by the timestamp (`yyyymmddhhmm`) to ensure that migrations are naturally ordered by creation time.
- **Unique Ordering:** Timestamps help avoid conflicts when multiple developers create migrations simultaneously.
- **Double Underscore Separator:** Use `__` (two underscores) to separate the timestamp from the description.
- **Clear Descriptions:** Include a brief, descriptive name (e.g., `initial_setup`, `add_customer_table`) to clarify the purpose of the migration.

## How to Add a New Migration

1. **Define the Change:**
   - Clearly identify the required schema modification (e.g., creating a new table, modifying columns, adding indexes).

2. **Create a Migration File:**
   - Navigate to your microservice’s migration folder (e.g., `src/main/resources/db/migration`).
   - Create a new SQL file using the naming convention. For instance:
     ```
     V202503061045__Add_Product_Table.sql
     ```

3. **Write the Migration SQL:**
   - Add the necessary SQL commands for the migration. For example:
     ```sql
     CREATE TABLE product (
         id INT PRIMARY KEY,
         name VARCHAR(255) NOT NULL,
         price DECIMAL(10, 2) NOT NULL,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
     );
     ```
   - Ensure that the migration script runs only once. When possible, write idempotent SQL or include checks for pre-existing objects.

4. **Test the Migration Locally:**
   - Execute the migration in your development environment:
     ```bash
     flyway migrate
     ```
   - Confirm that the migration is applied correctly and that the database schema updates as expected.

5. **Version Control and Collaboration:**
   - Commit the new migration file along with any related code changes.
   - Notify your team so that everyone applies the latest migrations before deployment.

## Purpose of Using Flyway

- **Consistency:** Ensures all environments use the same database schema version.
- **Version Control:** Tracks every schema change alongside application code, facilitating audits and reviews.
- **Automation:** Integrates with CI/CD pipelines to automatically apply database changes during deployments.
- **Reliability:** Reduces human error by automating schema updates and enforcing best practices in schema evolution.


