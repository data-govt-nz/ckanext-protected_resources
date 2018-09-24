-- add the resource_protected table to support https://github.com/data-govt-nz/ckanext-protected_resources

\connect "{db_name}"


CREATE TABLE  IF NOT EXISTS "resource_protected"(
  id text NOT NULL,
  resource_id text NOT NULL
);

ALTER TABLE public.resource_protected OWNER TO "{db_user}";