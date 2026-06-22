-- ============================================================
-- Construction AI — Demo Seed Data
-- Al Barsha Mixed-Use Tower — PROJ-001
-- 7 days of realistic site activity
-- Run this AFTER schema.sql in the Supabase SQL editor
-- ============================================================

-- ── Extra projects ────────────────────────────────────────────
insert into projects (id, name, location, pm_name, pm_phone, pm_email)
values
  ('PROJ-001', 'Al Barsha Mixed-Use Tower',  'Al Barsha, Dubai, UAE',      'Ahmed Al-Rashid',   '+971501234567', 'ahmed@construction-demo.com'),
  ('PROJ-002', 'JVC Residential Complex',    'Jumeirah Village Circle, Dubai', 'Sara Khalil',    '+971507654321', 'sara@construction-demo.com'),
  ('PROJ-003', 'DIFC Office Fit-Out',        'DIFC, Dubai, UAE',            'James Thornton',   '+971509876543', 'james@construction-demo.com')
on conflict (id) do nothing;


-- ============================================================
-- SITE UPDATES — raw messages as they arrived
-- ============================================================

with su as (
  insert into site_updates (id, project_id, source, raw_content, sender, received_at) values

  -- ── DAY 1 — Monday (normal progress) ──────────────────────
  ('a1000001-0000-0000-0000-000000000001', 'PROJ-001', 'whatsapp',
   'Morning all. Concrete pour on Level 4 columns started at 7am. 18 columns targeted today. Weather clear, no issues so far. Crew of 22 on site.',
   '+971501111001', now() - interval '6 days' + interval '7 hours'),

  ('a1000001-0000-0000-0000-000000000002', 'PROJ-001', 'email',
   'Structural steel delivery for Level 5 arrived this morning. All 48 beams accounted for and match spec (HEB240). Stored in laydown area B. Ready for erection tomorrow.',
   'logistics@steelsupply-uae.com', now() - interval '6 days' + interval '9 hours'),

  ('a1000001-0000-0000-0000-000000000003', 'PROJ-001', 'form',
   'Level 4 concrete pour complete. All 18 columns done by 2pm. QC inspection passed. Formwork removal scheduled for Wednesday after curing check.',
   'Khalid Mansoor', now() - interval '6 days' + interval '14 hours'),

  ('a1000001-0000-0000-0000-000000000004', 'PROJ-001', 'whatsapp',
   'MEP rough-in floors 1 and 2 signed off by inspector this afternoon. Electrical and plumbing both cleared. Moving crew to floor 3 tomorrow.',
   '+971501111002', now() - interval '6 days' + interval '16 hours'),

  -- ── DAY 2 — Tuesday (medium issue) ────────────────────────
  ('a1000001-0000-0000-0000-000000000005', 'PROJ-001', 'whatsapp',
   'Steel erection Level 5 started. First 12 beams up by noon. One beam had a minor surface rust patch — tagged and reported to engineer. Waiting on decision whether to treat or replace.',
   '+971501111001', now() - interval '5 days' + interval '12 hours'),

  ('a1000001-0000-0000-0000-000000000006', 'PROJ-001', 'email',
   'Scaffolding inspection carried out on north and west faces. North face passed. West face has two bays flagged as non-compliant — tie spacing exceeds maximum. Work on west face suspended until rectified. Contractor notified.',
   'safety@siteinspect.ae', now() - interval '5 days' + interval '13 hours'),

  ('a1000001-0000-0000-0000-000000000007', 'PROJ-001', 'form',
   'Scaffolding west face issue resolved. Contractor re-tied all flagged bays, re-inspection done and passed at 4pm. West face work resumed.',
   'Omar Al-Farsi', now() - interval '5 days' + interval '16 hours'),

  -- ── DAY 3 — Wednesday (critical safety incident) ──────────
  ('a1000001-0000-0000-0000-000000000008', 'PROJ-001', 'whatsapp',
   'URGENT — Worker fall on Level 3 at 9:15am. Worker slipped near formwork edge. Wearing harness, caught by anchor. No injury but site protocol requires full stop. All work halted. HSE notified. Incident report being filed now.',
   '+971501111003', now() - interval '4 days' + interval '9 hours 15 minutes'),

  ('a1000001-0000-0000-0000-000000000009', 'PROJ-001', 'email',
   'Following this morning incident: HSE inspection completed at 1pm. Root cause identified as loose plywood board near formwork edge. Board secured, area re-barriered. HSE cleared site to resume work at 2:30pm with additional edge protection installed on all open levels.',
   'hse@constructionuae.ae', now() - interval '4 days' + interval '14 hours'),

  ('a1000001-0000-0000-0000-000000000010', 'PROJ-001', 'form',
   'Work resumed Level 3 and above at 2:30pm following HSE clearance. Toolbox talk conducted with all 37 workers re edge protection. Signed attendance record filed. No further incidents.',
   'Ahmed Al-Rashid', now() - interval '4 days' + interval '15 hours'),

  -- ── DAY 4 — Thursday (materials delay) ────────────────────
  ('a1000001-0000-0000-0000-000000000011', 'PROJ-001', 'whatsapp',
   'Concrete pump broke down at 8am. Level 5 slab pour scheduled for today cannot proceed. Maintenance team on site. Pump supplier says earliest replacement pump available is tomorrow morning.',
   '+971501111001', now() - interval '3 days' + interval '8 hours'),

  ('a1000001-0000-0000-0000-000000000012', 'PROJ-001', 'email',
   'Pump breakdown update: arranged hire pump from Al Fara Machinery. Arrives site 6am tomorrow. Pour rescheduled to Friday. Overall programme impact: 1 day delay on Level 5 slab. Mitigation: Saturday working approved to recover.',
   'logistics@construction-demo.com', now() - interval '3 days' + interval '11 hours'),

  ('a1000001-0000-0000-0000-000000000013', 'PROJ-001', 'form',
   'While waiting for pump, crew redirected to Level 2 fit-out preparation — block walls, door frames, MEP second fix prep. Good progress made. 3 rooms fully prepped.',
   'Khalid Mansoor', now() - interval '3 days' + interval '14 hours'),

  -- ── DAY 5 — Friday (recovery day) ─────────────────────────
  ('a1000001-0000-0000-0000-000000000014', 'PROJ-001', 'whatsapp',
   'Hire pump arrived 5:50am. Level 5 slab pour started at 7am. 280 cubic metres. All going smoothly. Expected completion 3pm.',
   '+971501111001', now() - interval '2 days' + interval '8 hours'),

  ('a1000001-0000-0000-0000-000000000015', 'PROJ-001', 'form',
   'Level 5 slab pour complete at 2:45pm. QC samples taken. Cube test results in 7 days. Curing membrane applied. Good recovery from yesterday delay.',
   'Omar Al-Farsi', now() - interval '2 days' + interval '15 hours'),

  ('a1000001-0000-0000-0000-000000000016', 'PROJ-001', 'whatsapp',
   'Saturday working confirmed. Full crew approved. Plan: Level 5 steelwork erection and Level 2 block walls completion.',
   '+971501111002', now() - interval '2 days' + interval '17 hours'),

  -- ── DAY 6 — Saturday (good progress) ──────────────────────
  ('a1000001-0000-0000-0000-000000000017', 'PROJ-001', 'whatsapp',
   'Saturday crew 28 workers. Level 5 steel erection: 30 of 48 beams up by midday. Level 2 block walls: 4 rooms complete. Programme recovery on track.',
   '+971501111001', now() - interval '1 day' + interval '12 hours'),

  ('a1000001-0000-0000-0000-000000000018', 'PROJ-001', 'form',
   'End of Saturday: Level 5 steel 44/48 beams erected. Remaining 4 beams Monday. Level 2 block walls 100% complete. Overall 1-day delay recovered to half day. Project back near programme.',
   'Ahmed Al-Rashid', now() - interval '1 day' + interval '17 hours'),

  -- ── DAY 7 — Today (current status) ────────────────────────
  ('a1000001-0000-0000-0000-000000000019', 'PROJ-001', 'whatsapp',
   'Monday morning. Final 4 Level 5 steel beams going up now. Should complete by 10am. Level 6 formwork planning meeting at 11am with engineer.',
   '+971501111001', now() - interval '2 hours'),

  ('a1000001-0000-0000-0000-000000000020', 'PROJ-001', 'email',
   'Subcontractor invoice dispute: Al Noor Electrical submitted invoice AED 285,000 for floors 1-3 MEP. Our QS assessment is AED 241,000. Difference of AED 44,000 relates to variation claims not approved. Meeting scheduled Wednesday to resolve.',
   'finance@construction-demo.com', now() - interval '1 hour'),

  ('a1000001-0000-0000-0000-000000000021', 'PROJ-001', 'form',
   'Level 5 steel complete at 9:50am. All 48 beams in place. Engineer sign-off received. Ready for Level 6 formwork planning to start this afternoon.',
   'Khalid Mansoor', now() - interval '30 minutes')

  returning id, project_id, source, sender, received_at
)

-- ============================================================
-- PROCESSED UPDATES — AI extraction results
-- ============================================================
insert into processed_updates
  (update_id, project_id, summary, issues, severity, delay_risk, action_required, processed_at)
select
  id,
  project_id,
  case id
    when 'a1000001-0000-0000-0000-000000000001' then 'Concrete pour on Level 4 columns started at 7am. 22-person crew on site, clear weather, targeting 18 columns today. No issues reported.'
    when 'a1000001-0000-0000-0000-000000000002' then 'Full structural steel delivery for Level 5 has arrived and been verified against spec. All 48 HEB240 beams accounted for and stored. Erection scheduled for tomorrow.'
    when 'a1000001-0000-0000-0000-000000000003' then 'Level 4 concrete pour completed successfully. All 18 columns poured and passed QC inspection by 2pm. Formwork removal planned for Wednesday pending curing check.'
    when 'a1000001-0000-0000-0000-000000000004' then 'MEP rough-in on floors 1 and 2 has received full inspector sign-off for both electrical and plumbing. Crew relocating to floor 3 tomorrow.'
    when 'a1000001-0000-0000-0000-000000000005' then 'Steel erection on Level 5 progressing — 12 of 48 beams installed by noon. One beam flagged for surface rust and referred to structural engineer for assessment.'
    when 'a1000001-0000-0000-0000-000000000006' then 'Scaffolding inspection found two non-compliant bays on the west face due to excessive tie spacing. West face work has been suspended pending contractor rectification.'
    when 'a1000001-0000-0000-0000-000000000007' then 'West face scaffolding issue fully resolved. Contractor re-tied all flagged bays, passed re-inspection at 4pm, and work has resumed.'
    when 'a1000001-0000-0000-0000-000000000008' then 'Worker fall incident on Level 3 at 9:15am. Worker was caught by harness with no injury, but all site work halted per HSE protocol. HSE notified and incident report filed.'
    when 'a1000001-0000-0000-0000-000000000009' then 'HSE inspection identified loose plywood near formwork edge as root cause. Edge secured and additional protection installed across all open levels. Site cleared to resume at 2:30pm.'
    when 'a1000001-0000-0000-0000-000000000010' then 'Work fully resumed after HSE clearance. Toolbox talk on edge protection conducted with all 37 workers. Signed attendance records filed.'
    when 'a1000001-0000-0000-0000-000000000011' then 'Concrete pump failure at 8am has halted the planned Level 5 slab pour. Replacement pump sourced but not available until tomorrow morning, causing a 1-day delay.'
    when 'a1000001-0000-0000-0000-000000000012' then 'Hire pump confirmed for 6am tomorrow. Level 5 pour rescheduled to Friday. 1-day programme delay anticipated, with Saturday working approved to recover.'
    when 'a1000001-0000-0000-0000-000000000013' then 'Crew redirected to Level 2 fit-out prep during pump downtime. Three rooms fully prepped — door frames, block walls, MEP second fix preparation complete.'
    when 'a1000001-0000-0000-0000-000000000014' then 'Hire pump arrived on time and Level 5 slab pour commenced at 7am. 280 cubic metres being poured, expected to complete by 3pm.'
    when 'a1000001-0000-0000-0000-000000000015' then 'Level 5 slab pour completed successfully at 2:45pm. QC cube samples taken. Curing membrane applied. Delay from Thursday effectively recovered.'
    when 'a1000001-0000-0000-0000-000000000016' then 'Saturday working approved with full crew. Plan targets Level 5 steelwork erection and Level 2 block wall completion to recover programme.'
    when 'a1000001-0000-0000-0000-000000000017' then 'Saturday progress strong — 30 of 48 Level 5 steel beams erected by midday. Level 2 block walls: 4 rooms complete. Programme recovery on track.'
    when 'a1000001-0000-0000-0000-000000000018' then 'Saturday wrap-up: Level 5 steel 44/48 beams done, Level 2 block walls 100% complete. Overall delay reduced to half a day. Project near programme.'
    when 'a1000001-0000-0000-0000-000000000019' then 'Final 4 Level 5 steel beams being installed this morning. Level 6 formwork planning meeting with engineer at 11am.'
    when 'a1000001-0000-0000-0000-000000000020' then 'Invoice dispute with Al Noor Electrical: AED 44,000 difference between submitted (AED 285k) and approved (AED 241k) amounts. Meeting scheduled Wednesday to resolve variation claims.'
    when 'a1000001-0000-0000-0000-000000000021' then 'Level 5 structural steel 100% complete at 9:50am with engineer sign-off received. Level 6 formwork planning underway this afternoon.'
  end as summary,

  case id
    when 'a1000001-0000-0000-0000-000000000001' then '[]'::jsonb
    when 'a1000001-0000-0000-0000-000000000002' then '[]'::jsonb
    when 'a1000001-0000-0000-0000-000000000003' then '[]'::jsonb
    when 'a1000001-0000-0000-0000-000000000004' then '[]'::jsonb
    when 'a1000001-0000-0000-0000-000000000005' then '["Surface rust on one beam — engineer assessment pending", "12 of 48 beams remaining"]'::jsonb
    when 'a1000001-0000-0000-0000-000000000006' then '["West face scaffolding non-compliant — tie spacing exceeded", "West face work suspended"]'::jsonb
    when 'a1000001-0000-0000-0000-000000000007' then '[]'::jsonb
    when 'a1000001-0000-0000-0000-000000000008' then '["Worker fall incident — Level 3", "All site work halted", "HSE notified", "Incident report filed"]'::jsonb
    when 'a1000001-0000-0000-0000-000000000009' then '["Loose plywood identified as root cause", "Additional edge protection required on all open levels"]'::jsonb
    when 'a1000001-0000-0000-0000-000000000010' then '[]'::jsonb
    when 'a1000001-0000-0000-0000-000000000011' then '["Concrete pump failure", "Level 5 slab pour halted", "1-day programme delay"]'::jsonb
    when 'a1000001-0000-0000-0000-000000000012' then '["1-day delay on Level 5 slab", "Saturday working required to recover"]'::jsonb
    when 'a1000001-0000-0000-0000-000000000013' then '[]'::jsonb
    when 'a1000001-0000-0000-0000-000000000014' then '[]'::jsonb
    when 'a1000001-0000-0000-0000-000000000015' then '[]'::jsonb
    when 'a1000001-0000-0000-0000-000000000016' then '[]'::jsonb
    when 'a1000001-0000-0000-0000-000000000017' then '[]'::jsonb
    when 'a1000001-0000-0000-0000-000000000018' then '[]'::jsonb
    when 'a1000001-0000-0000-0000-000000000019' then '[]'::jsonb
    when 'a1000001-0000-0000-0000-000000000020' then '["Invoice dispute AED 44,000 with Al Noor Electrical", "Variation claims not approved"]'::jsonb
    when 'a1000001-0000-0000-0000-000000000021' then '[]'::jsonb
  end as issues,

  case id
    when 'a1000001-0000-0000-0000-000000000008' then 'critical'
    when 'a1000001-0000-0000-0000-000000000011' then 'critical'
    when 'a1000001-0000-0000-0000-000000000006' then 'medium'
    when 'a1000001-0000-0000-0000-000000000005' then 'medium'
    when 'a1000001-0000-0000-0000-000000000012' then 'medium'
    when 'a1000001-0000-0000-0000-000000000020' then 'medium'
    else 'low'
  end as severity,

  case id
    when 'a1000001-0000-0000-0000-000000000008' then true
    when 'a1000001-0000-0000-0000-000000000011' then true
    when 'a1000001-0000-0000-0000-000000000012' then true
    else false
  end as delay_risk,

  case id
    when 'a1000001-0000-0000-0000-000000000008' then 'Stop all work. Ensure HSE is on site. File incident report immediately. Notify client.'
    when 'a1000001-0000-0000-0000-000000000011' then 'Confirm hire pump booking for tomorrow 6am. Approve Saturday working to recover 1-day delay.'
    when 'a1000001-0000-0000-0000-000000000006' then 'Confirm scaffolding contractor attends site today to rectify west face bays before end of shift.'
    when 'a1000001-0000-0000-0000-000000000005' then 'Get structural engineer written decision on rusted beam by end of day — treat or replace.'
    when 'a1000001-0000-0000-0000-000000000012' then 'Confirm Saturday crew and approve overtime budget. Notify client of 1-day delay in writing.'
    when 'a1000001-0000-0000-0000-000000000020' then 'Attend Wednesday meeting with QS. Bring approved variation log. Target settlement at AED 255k.'
    else null
  end as action_required,

  received_at + interval '45 seconds' as processed_at
from su;


-- ============================================================
-- DAILY REPORTS — 6 days of generated reports
-- ============================================================
insert into daily_reports (project_id, report_date, content, rag_status, created_at) values

('PROJ-001', current_date - 6,
'## Overall Status
🟢 Green — Productive first day. All planned works completed on programme.

## Progress Today
- Level 4 concrete pour completed — all 18 columns poured and QC passed
- Structural steel delivery for Level 5 received and verified (all 48 HEB240 beams)
- MEP rough-in floors 1 and 2 signed off by inspector
- 22-person crew on site, full attendance

## Issues & Blockers
- No issues today

## Actions Required Tomorrow
1. Begin Level 5 steel erection — 48 beams to be erected
2. Mobilise Level 3 MEP crew following floors 1-2 sign-off
3. Confirm formwork removal timing for Level 4 (Wednesday after curing check)

## Risk Watch
- No current risks to programme or budget',
'Green', now() - interval '6 days' + interval '17 hours'),

('PROJ-001', current_date - 5,
'## Overall Status
🟡 Amber — Scaffolding non-compliance on west face caused temporary work suspension. Resolved same day but requires monitoring.

## Progress Today
- Level 5 steel erection commenced — 12 of 48 beams erected
- Scaffolding issue on west face identified and fully resolved by 4pm
- Steel delivery beam with surface rust flagged — engineer assessment pending

## Issues & Blockers
- ⚠️ West face scaffolding: two bays had non-compliant tie spacing. Work suspended 13:00–16:00. Resolved.
- Beam surface rust: one HEB240 beam has surface rust patch. Engineer decision pending (treat or replace)

## Actions Required Tomorrow
1. Obtain structural engineer written decision on rusted beam — treat or replace
2. Continue Level 5 steel erection — target 30+ beams by end of day
3. Monitor west face scaffolding — inspector re-visit recommended

## Risk Watch
- Rusted beam could cause minor delay if replacement ordered (2–3 day lead time)
- Scaffolding compliance: one non-conformance in first week is a yellow flag — reinforce contractor briefing',
'Amber', now() - interval '5 days' + interval '17 hours'),

('PROJ-001', current_date - 4,
'## Overall Status
🔴 Red — Safety incident on Level 3 halted all site work for 5 hours. Site cleared by HSE and resumed with enhanced controls.

## Progress Today
- Worker fall incident Level 3 at 09:15 — harness functioned correctly, no injury
- All site work halted 09:15–14:30 per HSE protocol
- HSE inspection identified loose plywood as root cause — rectified
- Additional edge protection installed on all open levels
- Toolbox talk completed with all 37 workers
- Work resumed 14:30 — 5 productive hours lost

## Issues & Blockers
- ⚠️ SAFETY: Worker fall incident — full investigation underway
- ⚠️ 5-hour work stoppage — some programme impact

## Actions Required Tomorrow
1. File completed HSE incident report with client and authority
2. Engineer to confirm all edge protection installations are permanent fixtures
3. PM to assess programme impact and advise if weekend working needed
4. Confirm insurance notification sent

## Risk Watch
- Repeated safety incident would trigger authority site suspension — zero tolerance from here
- Check if 5-hour loss impacts Level 5 pour schedule (currently planned this week)',
'Red', now() - interval '4 days' + interval '17 hours'),

('PROJ-001', current_date - 3,
'## Overall Status
🔴 Red — Concrete pump failure halted Level 5 slab pour. 1-day programme delay confirmed. Recovery plan approved.

## Progress Today
- Concrete pump failed at 08:00 — Level 5 slab pour cancelled for today
- Hire pump sourced and confirmed for 06:00 tomorrow
- Saturday working approved to recover 1-day delay
- Crew redirected to Level 2 fit-out prep — 3 rooms fully prepared

## Issues & Blockers
- ⚠️ CRITICAL: Concrete pump breakdown — Level 5 pour delayed 1 day
- Saturday working required — overtime budget impact approx AED 18,000

## Actions Required Tomorrow
1. Confirm hire pump on site by 06:00 — call supplier at 05:30 to verify
2. Full crew briefing at 06:30 for Level 5 slab pour
3. Ensure QC team on site for sampling
4. Saturday crew confirmation — target 28 workers

## Risk Watch
- Two critical incidents in one week (HSE + pump) — review plant maintenance schedule
- Saturday working adds fatigue risk — ensure adequate supervision',
'Red', now() - interval '3 days' + interval '17 hours'),

('PROJ-001', current_date - 2,
'## Overall Status
🟢 Green — Level 5 slab pour completed successfully. Programme delay fully recovered through Saturday working approval.

## Progress Today
- Hire pump arrived 05:50 — Level 5 slab pour started on schedule at 07:00
- 280 cubic metres poured, completed 14:45 — ahead of 15:00 target
- QC cube samples taken, curing membrane applied
- Saturday working confirmed — 28 workers approved

## Issues & Blockers
- No new issues today
- Previous 1-day delay effectively recovered

## Actions Required Tomorrow (Saturday)
1. Level 5 steelwork — target 30+ beams of 48
2. Level 2 block walls — complete all remaining rooms
3. Morning briefing 06:30 — remind crew this is recovery day, full focus

## Risk Watch
- QC cube test results in 7 days — flag if below target strength
- Monitor crew fatigue from extended week',
'Green', now() - interval '2 days' + interval '17 hours'),

('PROJ-001', current_date - 1,
'## Overall Status
🟢 Green — Strong Saturday recovery. Project back near programme. Good momentum heading into next week.

## Progress Today (Saturday)
- Level 5 steel erection: 44 of 48 beams complete
- Level 2 block walls: 100% complete
- Overall delay reduced from 1 day to approximately half a day
- 28-worker crew maintained full productivity throughout

## Issues & Blockers
- 4 beams remaining on Level 5 — minor, completing Monday morning
- No safety incidents

## Actions Required Monday
1. Complete final 4 Level 5 beams first thing — should finish by 10am
2. Level 6 formwork planning meeting with engineer at 11am
3. Invoice dispute with Al Noor Electrical — confirm Wednesday meeting attendance
4. Submit weekly programme update to client by end of day

## Risk Watch
- Invoice dispute (AED 44k difference) — needs resolution this week before it escalates
- Level 6 planning critical — any delay here has knock-on to programme milestone',
'Green', now() - interval '1 day' + interval '17 hours');


-- ============================================================
-- Verify counts
-- ============================================================
select
  (select count(*) from projects)          as projects,
  (select count(*) from site_updates)      as site_updates,
  (select count(*) from processed_updates) as processed_updates,
  (select count(*) from daily_reports)     as daily_reports;
