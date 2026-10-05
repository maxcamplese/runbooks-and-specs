# Spec: Account Region Field

A required Region field on Salesforce Accounts, with Slack alerts for new accounts.

> **Sample document.** This is a practice spec for a realistic but fictional change at a fictional company. It shows how I structure a spec, RACI, UAT plan, and rollout. It is not a record of a change I made in a production org.

| | |
|---|---|
| **Status** | Draft for review |
| **Author** | Max Camplese |
| **Requested by** | VP of Sales (fictional) |
| **Systems** | Salesforce (Sales Cloud), Slack |
| **Target release** | Not scheduled (sample spec). Would ship during a weekly change window. |
| **Change type** | Normal change: configuration only, no code |

---

## 1. Summary

Sales managers cannot tell which region a new account belongs to without opening it, and nobody is notified when an account is created in their region. This change adds a required **Region** field to the Account object, fills it in for existing accounts, posts a Slack message to the regional sales channel when a new account is created, and adds a report and dashboard of new accounts by region.

## 2. Background and Problem

- Region is tracked today in a free-text "Notes" field, spelled inconsistently ("West", "west coast", "W").
- Regional managers find out about new accounts in a weekly spreadsheet export, up to 7 days late.
- Leadership wants a dashboard of new accounts by region, which is impossible with free text.

## 3. Scope

**In scope**

- New picklist field `Region__c` on Account.
- Validation rule that makes Region required on create and edit.
- One-time backfill of Region on existing Accounts.
- Record-triggered flow that sends a Slack message to the right regional channel when an Account is created.
- Field-level security and page layout updates.
- One report and one dashboard component.

**Out of scope**

- Changing account ownership or assignment rules.
- Region on Leads, Contacts, or Opportunities (possible follow-up).
- Any change to the ERP or billing integration.

## 4. Requirements

| ID | Requirement | Priority |
|---|---|---|
| R1 | Every Account has exactly one Region from a fixed list: West, Central, East, International. | Must |
| R2 | Users cannot save a new or edited Account without a Region. | Must |
| R3 | The nightly ERP integration user can still save Accounts without a Region, so the sync does not fail. | Must |
| R4 | When an Account is created, a message is posted to that region's Slack channel within 5 minutes. | Must |
| R5 | Sales Ops can edit Region. Sales Reps can set it on create but only Sales Ops can change it afterward. | Should |
| R6 | A dashboard shows new Accounts by Region for the current and previous quarter. | Should |

## 5. Design

### 5.1 Field

| Property | Value |
|---|---|
| Object | Account |
| Label / API name | Region / `Region__c` |
| Type | Picklist, **restricted** (users cannot add values) |
| Values | West, Central, East, International |
| Default | None (forces a choice) |
| Help text | "Sales region this account belongs to. Ask Sales Ops if unsure." |

### 5.2 Validation Rule

- **Name:** `Region_Required`
- **Condition (error when true):**
  `AND( ISBLANK(TEXT(Region__c)), NOT($Permission.Bypass_Region_Validation) )`
- **Error message:** "Choose a Region before saving. Ask Sales Ops if you are not sure which region applies."
- **Bypass:** custom permission `Bypass_Region_Validation`, granted through a permission set assigned only to the ERP integration user (R3).

### 5.3 Rule for R5 (Reps Cannot Change Region After Create)

- Second validation rule `Region_Locked_After_Create`:
  `AND( NOT(ISNEW()), ISCHANGED(Region__c), NOT(ISBLANK(TEXT(PRIORVALUE(Region__c)))), NOT($Permission.Edit_Region) )`
- The `PRIORVALUE` check lets anyone fill in a Region that was blank. Without it, a rep editing an Account the integration created with no Region could not save at all: rule 5.2 would require a Region and this rule would block setting one.
- Custom permission `Edit_Region` is granted to the Sales Ops permission set.

### 5.4 Flow

- **Type:** record-triggered flow on Account, runs **after save**, **only when a record is created**.
- **Logic:** a Get Records element looks up the Slack channel for the Account's Region in the custom metadata type `Region_Slack_Channel__mdt`. The flow then posts the Account name, owner, and a link to the record to that channel.
- **Asynchronous path:** the Slack post runs on the flow's **Run Asynchronously** path, because a call out to Slack can't run inside the save itself. A Slack failure therefore cannot roll back the save.
- **Why custom metadata:** an admin can change a channel without editing or redeploying the flow.
- **Channel mapping** (the records in `Region_Slack_Channel__mdt`):

| Region | Slack channel |
|---|---|
| West | `#sales-west` |
| Central | `#sales-central` |
| East | `#sales-east` |
| International | `#sales-intl` |

- **Accounts with no Region** (only possible from the integration user) find no mapping record, so a Decision element sends them to `#sales-ops` for cleanup.
- **Failure handling:** a fault path emails the Salesforce admin group. A failed Slack post must never block the Account from saving.

### 5.5 Security and Layout

| Profile or permission set | Region field access |
|---|---|
| Sales Rep | Read and edit (edit blocked after create by rule 5.3) |
| Sales Ops | Read and edit |
| Support | Read only |
| ERP integration user | Read and edit, plus validation bypass |

Add Region to the Account page layout in the top section, and to the "New Account" quick action.

### 5.6 Report and Dashboard

- **Report:** "New Accounts by Region". Report type Accounts, filter Created Date, Range **Current and Previous CQ**, grouped by Region and Created Date (by month).
- **Dashboard component:** stacked bar chart on the existing Sales Leadership dashboard.

## 6. Data Migration (Backfill)

1. Export all Accounts with `Id`, `BillingState`, `BillingCountry`, and the old free-text notes.
2. Map each Account to a Region by billing state and country, using a mapping table Sales Ops approves before the load.
3. Sales Ops reviews any rows that did not map (expected: under 5 percent).
4. Load the `Region__c` values with Data Loader in the full sandbox first, then in production.
5. **Verify:** a report of Accounts where Region is blank returns 0 rows, except records created by the integration user.

The backfill runs **before** the validation rule is turned on, so existing records that are edited do not error out.

## 7. RACI

**R** = Responsible (does the work), **A** = Accountable (signs off, one person only), **C** = Consulted, **I** = Informed.

| Task | Salesforce admin | Sales Ops lead | VP of Sales | Integration owner | Slack admin | Sales reps |
|---|---|---|---|---|---|---|
| Approve requirements | C | R | **A** | C | I | I |
| Build field, rules, flow in sandbox | **A/R** | C | | C | C | |
| Connect Slack channels | R | | | | **A** | |
| Approve region mapping table | C | **A/R** | I | | | |
| Run backfill | **A/R** | C | | I | | |
| UAT | C | **A/R** | I | R (test case 6) | | R (2 volunteers) |
| Go/no-go decision | R | C | **A** | C | C | |
| Deploy to production | **A/R** | I | I | I | I | |
| Announce change and train | C | **A/R** | I | | | I |

## 8. UAT Test Plan

**Environment:** full sandbox refreshed within 30 days.
**Testers:** Sales Ops lead, 2 sales reps, integration owner.
**Exit criteria:** every "Must" test passes, and no open defect is rated High.

| # | Requirement | Test | Steps | Expected result | Pass / Fail |
|---|---|---|---|---|---|
| 1 | R2 | Create without Region | As a Sales Rep, create an Account and leave Region blank. Save. | Save is blocked. Error text matches 5.2. | |
| 2 | R1, R4 | Create with Region | As a Sales Rep, create an Account with Region = West. | Saves. Message appears in `#sales-west` within 5 minutes with the correct name and link. | |
| 3 | R4 | Each channel | Repeat test 2 for Central, East, International. | Each message lands in the matching channel only. | |
| 4 | R5 | Rep edits Region | As the Sales Rep, change Region on the Account from test 2. | Blocked with the lock error from 5.3. | |
| 5 | R5 | Sales Ops edits Region | As Sales Ops, change Region from West to Central. | Saves. No new Slack message (flow only runs on create). | |
| 6 | R3 | Integration user | Run the ERP sync job against the sandbox with one Account that has no Region. | Sync succeeds. Account saves. Message posts to `#sales-ops`. | |
| 7 | R1 | Restricted values | Try to set Region to "Northwest" through Data Loader. | Rejected: value not in the restricted picklist. | |
| 8 | R4 | Slack failure | Temporarily point West to a channel the integration cannot post to. Create a West Account. | Account still saves. Admin group gets the fault email. | |
| 9 | R6 | Report | Open "New Accounts by Region". | Accounts from tests 2 to 6 appear under the right regions. | |
| 10 | Backfill | Blank check | Run the "Region is blank" report after the sandbox backfill. | 0 rows except records created by the integration user. | |
| 11 | R2, R5 | Rep fills in a blank Region | As a Sales Rep, open the Account from test 6 (no Region), set Region = East, save. | Saves. No Slack message (not a new record). | |

Testers record defects with the test number, the steps, a screenshot, and the user they tested as.

## 9. Rollout Plan

| Step | When | Owner |
|---|---|---|
| Announce the change to Sales, with a 1-paragraph "what changes for you" | 5 business days before | Sales Ops lead |
| Deploy field, layouts, permission sets (rules and flow **inactive**) | Change window, step 1 | Salesforce admin |
| Run production backfill and verify the blank-check report | Change window, step 2 | Salesforce admin |
| Activate validation rules | Change window, step 3 | Salesforce admin |
| Activate flow, then create one test Account per region and delete them | Change window, step 4 | Salesforce admin |
| Post "it's live" message with a 2-minute screen recording | Same day | Sales Ops lead |
| Watch `#sales-ops` and the fault email for 1 week | Week 1 | Salesforce admin |

## 10. Rollback Plan

Each step can be undone on its own, in reverse order:

1. **Deactivate the flow.** Slack messages stop. No data changes.
2. **Deactivate both validation rules.** Users can save without Region again.
3. **Leave the field and backfilled data in place.** Removing them would lose the backfill. Hide the field from layouts instead if needed.

**Rollback trigger:** the go/no-go owner (VP of Sales) decides, on advice from the admin, if Account saves fail for users who should be able to save, or the ERP sync fails.

## 11. Open Questions

1. Is the Salesforce-to-Slack connection already set up in this org, and which Slack workspace admin approves it? (Owner: Slack admin)
2. Do any other integrations create Accounts besides ERP? Each one needs the bypass or must send a Region. (Owner: Integration owner)
3. Should Region also drive account ownership later? If so, that is a separate spec. (Owner: VP of Sales)
