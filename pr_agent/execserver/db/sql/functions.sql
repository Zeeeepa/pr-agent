-- SQL functions for database operations

-- Function to execute arbitrary SQL
CREATE OR REPLACE FUNCTION public.exec_sql(sql text)
RETURNS SETOF json AS $$
BEGIN
    RETURN QUERY EXECUTE sql;
EXCEPTION WHEN OTHERS THEN
    RAISE EXCEPTION '%', SQLERRM;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to create a table if it doesn't exist
CREATE OR REPLACE FUNCTION public.create_table_if_not_exists(table_name text, columns text)
RETURNS void AS $$
BEGIN
    EXECUTE format('CREATE TABLE IF NOT EXISTS %I (%s)', table_name, columns);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to drop a table if it exists
CREATE OR REPLACE FUNCTION public.drop_table_if_exists(table_name text)
RETURNS void AS $$
BEGIN
    EXECUTE format('DROP TABLE IF EXISTS %I CASCADE', table_name);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
