-- ============================================================
-- Construction AI — Supabase Schema
-- Run this in your Supabase SQL editor to set up all tables
-- ============================================================

-- Site updates (raw incoming messages)
create table if not exists site_updates (
  id            uuid primary key default gen_random_uuid(),
  project_id    text not null,
  source        text not null,        -- 'whatsapp' | 'email' | 'form'
  raw_content   text not null,
  sender        text,
  received_at   timestamptz default now()
);

-- AI-processed results
create table if not exists processed_updates (
  id               uuid primary key default gen_random_uuid(),
  update_id        uuid references site_updates(id),
  project_id       text not null,
  summary          text,
  issues           jsonb default '[]',
  severity         text default 'low',   -- 'low' | 'medium' | 'critical'
  delay_risk       boolean default false,
  action_required  text,
  processed_at     timestamptz default now()
);

-- Daily reports
create table if not exists daily_reports (
  id           uuid primary key default gen_random_uuid(),
  project_id   text not null,
  report_date  date not null,
  content      text,
  rag_status   text default 'Green',    -- 'Red' | 'Amber' | 'Green'
  created_at   timestamptz default now()
);

-- Projects reference table
create table if not exists projects (
  id          text primary key,         -- e.g. 'PROJ-001'
  name        text not null,
  location    text,
  pm_name     text,
  pm_phone    text,
  pm_email    text,
  created_at  timestamptz default now()
);

-- Seed a demo project
insert into projects (id, name, location, pm_name, pm_phone, pm_email)
values (
  'PROJ-001',
  'Al Barsha Mixed-Use Tower',
  'Al Barsha, Dubai, UAE',
  'Ahmed Al-Rashid',
  '+971501234567',
  'ahmed@construction-demo.com'
) on conflict (id) do nothing;

-- Indexes for fast time-based queries
create index if not exists idx_site_updates_project_date
  on site_updates (project_id, received_at desc);

create index if not exists idx_processed_project_date
  on processed_updates (project_id, processed_at desc);

create index if not exists idx_reports_project_date
  on daily_reports (project_id, report_date desc);
