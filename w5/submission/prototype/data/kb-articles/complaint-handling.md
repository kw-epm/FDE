# Complaint handling — agent playbook

A complaint is any ticket where the customer signals dissatisfaction beyond the resolution itself. Common signals: "unacceptable", "I'm furious", "this is unprofessional", explicit threats to cancel, mentions of regulator / lawyer / Better Business Bureau / state attorney general.

## What the AI does

- Acknowledges the issue without rushing to fix or deflect.
- Pulls up the customer's history and recent tickets to show context.
- **Does not** make any compensation offer.
- **Does not** cancel, refund, or modify the account based on emotional pressure.
- **Always escalates to a human** if the complaint mentions regulator / legal / lawyer language.

## Escalation paths

- Default complaint → CSR queue (any of the agents in CSR_AGENTS pool).
- Mentions of legal / regulator / chargeback / BBB → **Uma Bardwaj (Compliance)**.
- Enterprise customer → Victoria Lim (Account Management) on top of compliance.
