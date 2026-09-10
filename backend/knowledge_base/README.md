# NotRealOrg Knowledge Base

This is the fictional knowledge base for the AI Knowledge-Base Support Agent.

## Documents
- company_overview.md
- hr_policies.md
- leave_and_attendance.md
- it_support.md
- security_policy.md
- expense_policy.md
- remote_work.md
- benefits_and_payroll.md
- customer_support.md

The knowledge base contains 100+ documented FAQ-style facts across HR, leave, IT, security, expenses, remote work, payroll/benefits, company information, and customer support.

## Important testing rule
The agent must answer only from these documents. If a question is not supported by the documents, it must explicitly say that the information is unavailable and recommend escalation/clarification rather than inventing an answer.

Good unknown-question tests include:
- Does NotRealOrg provide housing allowance?
- Can employees request a salary advance?
- What is the promotion criteria for Senior Engineer?
- Does NotRealOrg pay for gym memberships?
- What is the exact bonus percentage for each role?

The documents intentionally contain enough related information to test follow-up questions and cross-document retrieval.
