"""The public demo company that recruiters and visitors can open in one click.

Visitors are logged in as a MEMBER, so they can explore and open or update
incidents but can't delete services or invite people. A scheduled job (every 3 days)
(scripts/seed.py --demo) wipes and regenerates the demo company, so anything
visitors change is cleaned up and the dates always look current.
"""
DEMO_ORG = "Acme Corp (Demo)"
DEMO_EMAIL = "demo@relay.io"
DEMO_OWNER_EMAIL = "owner@acme-demo.example"
