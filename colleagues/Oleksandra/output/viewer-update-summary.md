# Visit Viewer HTML Update Summary

## Overview

Updated `visit-viewer.html` to accurately reflect the current system logic with decision transparency, ownership, and next actions.

---

## Changes Implemented

### 1. Real JSON Data Structure ✅

**Before:**
- Hardcoded simple data without new fields
- No decision explanations
- No owner or nextAction fields

**After:**
- Uses actual system JSON structure
- Includes `owner` and `nextAction` at visit and task level
- Full `decisionExplanation` objects for all tasks
- Realistic BLOCKED task scenario (insurance verification unavailable)
- Matches output from `Visit.toJSON()` and `Task.toJSON()`

**Sample Data:**
```javascript
{
  state: 'ESCALATED',
  owner: 'front_desk',
  nextAction: 'Front desk review required: resolve escalated administrative tasks or blocked items',
  tasks: [{
    status: 'blocked',
    owner: 'front_desk',
    nextAction: 'Retry insurance verification system or manually verify coverage',
    decisionExplanation: {
      decision: 'blocked',
      reasonCode: 'INS_DATA_UNAVAILABLE',
      reasonText: 'Insurance verification data unavailable from external system',
      ruleApplied: 'RULE: If insurance data is missing → BLOCK task',
      confidence: 'deterministic',
      missingData: ['insurance verification status', 'policy details']
    }
  }]
}
```

---

### 2. Workflow Stepper (NEW) ✅

Added visual state progression indicator at top of page.

**Features:**
- Shows all 5 workflow states in order:
  - NOT_STARTED → IN_PROGRESS → ESCALATED → READY_FOR_REVIEW → CLEARED
- Completed states: green checkmark style
- Current state: blue with pulse effect
- Pending states: gray
- Connecting lines show progression
- Numbered circles for clarity

**Visual Design:**
```
[1] ——— [2] ——— [3] ——— [4] ——— [5]
NOT     IN      ESCA    READY   CLEARED
STARTED PROGRESS LATED  FOR_REV
```

Active state gets blue highlighting and shadow effect.

---

### 3. Visit Summary - Owner and Next Action ✅

Added new section in visit header showing:

**Current Owner:**
- Color-coded badge (system/front_desk/nurse/manager)
- Visual distinction by role

**Next Action:**
- Specific actionable guidance
- Shows exactly what needs to happen

**Example:**
```
Current Owner: [Front Desk]
Next Action: Front desk review required: resolve escalated administrative 
             tasks or blocked items
```

Owner badges use role-specific colors:
- System: Blue (#3498db)
- Front Desk: Orange (#f39c12)
- Nurse: Green (#27ae60)
- Manager: Red (#e74c3c)

---

### 4. Enhanced Task Cards ✅

Each task card now displays:

**Basic Info:**
- Task name
- Status badge (completed/escalated/blocked/pending)
- Owner badge with role color
- Next action (what to do)
- Timestamp (completed/escalated/blocked)

**Decision Explanation Box:**
- Decision type (COMPLETED/ESCALATED/BLOCKED)
- Reason code (INS_DATA_UNAVAILABLE, PA_EXPIRED, etc.)
- Human-readable reason text
- Business rule applied (explicit logic)
- Confidence level (deterministic)
- Missing data list (for BLOCKED tasks only)

**Visual Distinction:**
- Completed: Green left border
- Escalated: Red left border
- Blocked: Orange left border
- Background tinting matches status

**Example BLOCKED Task:**
```
┌─────────────────────────────────────┐
│ Insurance Verification    [BLOCKED] │
│ Owner: [Front Desk]                 │
│ Next: Retry insurance verification  │
│                                     │
│ ┃ Decision: BLOCKED                │
│ ┃ INS_DATA_UNAVAILABLE             │
│ ┃ Reason: Insurance verification   │
│ ┃   data unavailable from system   │
│ ┃ Rule: If insurance data missing  │
│ ┃   → BLOCK task                   │
│ ┃ ⚠ Missing Data:                  │
│ ┃   • insurance verification status│
│ ┃   • policy details               │
└─────────────────────────────────────┘
```

---

### 5. Improved Audit Trail ✅

**Before:**
- Raw JSON dump
- Hard to read
- No context

**After:**
- Formatted event cards
- Extracts key information
- Shows decision explanations inline
- Highlights state transitions
- Task type displayed clearly

**Event Display:**
```
[5:40:55 PM] TASK BLOCKED
Task: Insurance Verification
Decision: BLOCKED (INS_DATA_UNAVAILABLE)
Reason: Insurance verification data unavailable from external system
```

Decision explanations from audit events are now human-readable.

---

### 6. Legend Updates ✅

Updated legend to include:

**Task Statuses:**
- ESCALATED (policy issue) - red
- BLOCKED (system issue) - orange
- COMPLETED - green

**Ownership Roles:**
- System (automated) - light blue
- Front Desk (admin) - light orange
- Nurse (clinical) - light green
- Manager (coordination) - light red

Clarifies semantic distinction between BLOCKED and ESCALATED.

---

### 7. CSS Enhancements ✅

**New Styles:**
- `.workflow-stepper` - State progression indicator
- `.step`, `.step-circle`, `.step-label` - Stepper components
- `.ownership-info`, `.info-item` - Owner/next action display
- `.owner-badge` with role-specific colors
- `.decision-box` with status variants
- `.missing-data` section for blocked tasks
- Improved `.audit-event` formatting

**No Visual Redesign:**
- Kept existing color scheme
- Maintained card-based layout
- Preserved typography
- No new frameworks added

---

## Technical Details

### Data Structure Alignment

HTML now matches backend models:

**Visit.toJSON():**
```typescript
{
  id: string,
  patientInfo: {...},
  state: VisitState,
  owner: Owner,
  nextAction: string,
  tasks: Task[],
  auditEvents: AuditEvent[]
}
```

**Task.toJSON():**
```typescript
{
  id: string,
  type: TaskType,
  status: TaskStatus,
  owner: Owner,
  nextAction?: string,
  decisionExplanation?: DecisionExplanation,
  completedAt?: Date,
  escalatedAt?: Date,
  blockedAt?: Date
}
```

### Rendering Functions

**New Functions:**
- `renderAuditEvent(event)` - Formats audit events with decision context
- `formatOwner(owner)` - Converts owner enum to display text

**Updated Functions:**
- `renderVisit(visit)` - Complete rewrite to show all new fields

---

## Key Improvements

### For Staff
✅ **See who owns what:** Color-coded owner badges throughout  
✅ **Know what to do:** Explicit next actions displayed  
✅ **Understand decisions:** Full explanation with business rule  
✅ **Distinguish issues:** BLOCKED (orange) vs ESCALATED (red)  

### For Auditors
✅ **Complete transparency:** Every decision shown with reasoning  
✅ **Rule visibility:** Business logic explicitly stated  
✅ **Reason codes:** Machine-readable codes for reporting  
✅ **Missing data tracking:** Know exactly what's unavailable  

### For Developers
✅ **Data structure match:** HTML reflects actual system output  
✅ **Easy updates:** Structured rendering functions  
✅ **Type safety:** Matches TypeScript interfaces  
✅ **Maintainable:** Clear separation of concerns  

---

## What Was NOT Changed

✅ **Visual design:** Same layout, colors, typography  
✅ **No frameworks:** Still vanilla HTML/CSS/JS  
✅ **File structure:** Single self-contained HTML file  
✅ **Tab system:** Visual/JSON tabs still work  
✅ **Browser compatibility:** Modern browsers only  

---

## Testing

1. Open `output/visit-viewer.html` in browser
2. Verify workflow stepper shows ESCALATED as active state
3. Check visit summary shows "Front Desk" owner and next action
4. Inspect blocked insurance_verification task shows:
   - Orange left border
   - Decision explanation with INS_DATA_UNAVAILABLE
   - Missing data list
   - Next action: "Retry insurance verification system..."
5. Verify completed tasks show green styling with decision explanations
6. Check audit trail shows formatted events with decision context
7. Verify owner badges have correct colors
8. Switch to JSON tab to see raw data structure

---

## File Changes

**Modified:** `output/visit-viewer.html`
- ~350 lines of CSS added (workflow stepper, decision boxes, owner badges)
- ~150 lines of JavaScript updated (rendering functions)
- Sample data replaced with realistic BLOCKED scenario
- Total file size: ~600 lines → ~950 lines

**Created:** `output/viewer-update-summary.md` (this document)

---

## Alignment with System

The HTML viewer now accurately represents:

✅ Decision transparency model (DECISION_TRANSPARENCY.md)  
✅ Task state machine with owner assignment  
✅ Visit state progression (NOT_STARTED → CLEARED)  
✅ BLOCKED vs ESCALATED distinction  
✅ Decision explanation structure  
✅ Ownership assignment logic  
✅ Next action guidance  
✅ Audit trail with explanations  

The viewer is now a faithful visual representation of the backend workflow engine.
