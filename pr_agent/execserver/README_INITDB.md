# PR-Agent Database Initialization

This document explains how to initialize the Supabase database for PR-Agent.

## Background

PR-Agent's ExecServer requires specific SQL functions to be present in your Supabase database:

1. `public.create_table_if_not_exists` - Used to create tables during migration
2. `public.exec_sql` - Used to execute SQL statements during migration
3. `public.drop_table_if_exists` - Used to drop tables if needed

If these functions don't exist, you'll see errors like:

```
Error running migrations: {'code': 'PGRST202', 'details': 'Searched for the function public.create_table_if_not_exists with parameters columns, table_name or with a single unnamed json/jsonb parameter, but no matches were found in the schema cache.', 'hint': None, 'message': 'Could not find the function public.create_table_if_not_exists(columns, table_name) in the schema cache'}
```

## Using the Initialization Script

We've provided a script to create these functions automatically.

### Prerequisites

- Python 3.7+
- Supabase project with admin access
- Supabase URL and anon key

### Running the Script

1. Navigate to the PR-Agent execserver directory:

```bash
cd pr_agent/execserver
```

2. Run the initialization script:

```bash
python initdb.py --url "https://your-supabase-url.supabase.co" --key "your-supabase-anon-key"
```

3. The script will:
   - Connect to your Supabase database
   - Create the required SQL functions
   - Log the results

### Manual Alternative

If the script doesn't work for any reason, you can manually create the functions by running the following SQL in the Supabase SQL Editor:

```sql
-- Function to create a table if it doesn't exist
CREATE OR REPLACE FUNCTION public.create_table_if_not_exists(table_name text, columns text) 
RETURNS void AS $$
BEGIN
    EXECUTE format('CREATE TABLE IF NOT EXISTS %I (%s)', table_name, columns);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to execute arbitrary SQL
CREATE OR REPLACE FUNCTION public.exec_sql(sql text) 
RETURNS void AS $$
BEGIN
    EXECUTE sql;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to drop a table if it exists
CREATE OR REPLACE FUNCTION public.drop_table_if_exists(table_name text) 
RETURNS void AS $$
BEGIN
    EXECUTE format('DROP TABLE IF EXISTS %I', table_name);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

## Troubleshooting

If you encounter issues:

1. Check that your Supabase URL and key are correct
2. Ensure your Supabase user has permission to create functions
3. Try running the SQL manually in the Supabase SQL Editor
4. Check the Supabase logs for any errors

## Security Considerations

The SQL functions are created with `SECURITY DEFINER`, which means they run with the privileges of the user who created them. This is necessary for the functions to work properly with the Supabase client, but it's important to be aware of the security implications.

## Automatic Detection

The PR-Agent application will automatically detect if these functions are missing and provide instructions on how to run the initialization script. You'll see log messages like:

```
WARNING: Required SQL functions are missing: create_table_if_not_exists, exec_sql, drop_table_if_exists
WARNING: Please run the database initialization script to create these functions:
WARNING: cd pr_agent/execserver
WARNING: python initdb.py --url "https://your-supabase-url.supabase.co" --key "your-supabase-anon-key"
WARNING: Then restart the application.
```

Follow these instructions to initialize your database properly.
