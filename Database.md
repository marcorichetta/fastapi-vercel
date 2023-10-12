## PlanetScale Branching Guide with `pscale`

Make sure to have the `pscale` CLI installed.

Our databases are `elmo-db` and `elmo-db-test`.

### 1. Create a New Branch

Initiate a new branch. This serves as a safe environment for changes without affecting the main branch.

```bash
pscale branch create {database} {branch_name}
```

### 2. Connect to Your Branch

Establish a connection to interact with the branch directly.

```bash
pscale connect {database} {branch_name}
```

### 3. Generate and Apply Database Migrations

Before applying changes, generate migration scripts using Alembic. Ensure you have Alembic set up and configured:

```bash
alembic revision --autogenerate -m "{description_of_changes}"
```

After generating the migration, apply it:

```bash
alembic upgrade head
```

Note: If you're using SQLAlchemy to manage your database schema, and you've made changes to your models, you'll need to execute the script. Use the `DB_LOCAL_URL` in your `.env` file:

```bash
python database.py
```

### 4. Review the Changes

Review the differences between the branch and the main branch.

```bash
pscale branch diff {database} {branch_name}
```

### 5. Merge Changes to the Main Branch

Promote or merge the changes to the main branch after ensuring they are satisfactory.

```bash
pscale deploy-request create {database} {branch_name}
```

### 6. Clean Up (Optional)

Consider deleting the branch after merging to maintain a clean environment.

```bash
pscale branch delete {database} {branch_name}
```
