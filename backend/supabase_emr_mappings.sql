-- Run this in Supabase SQL editor to create the table for EMR mapping storage.
-- Columns: push_fhir (JSONB), get_fhir (JSONB) as requested.

create table if not exists emr_mappings (
  id uuid primary key default gen_random_uuid(),
  emr_id text not null unique,
  api_doc_url text,
  push_fhir jsonb not null default '[]',
  get_fhir jsonb not null default '[]',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index if not exists emr_mappings_emr_id on emr_mappings (emr_id);
