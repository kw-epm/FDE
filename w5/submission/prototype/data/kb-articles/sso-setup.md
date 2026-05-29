# SSO configuration

CloudServe supports SSO for Business and Enterprise plans via SAML 2.0 (Okta, Azure AD, Google Workspace, OneLogin) and OIDC.

## When to escalate

SSO setup is a configuration task. The agent can answer general questions and link to the setup guide, but **escalate to Theo Marek (Technical Escalation)** if:

- The IdP isn't in our supported list.
- The customer's metadata XML doesn't validate.
- They need a custom assertion attribute mapping.

## Self-service path

1. Admin → Security → SSO → Add provider.
2. Choose IdP from the dropdown.
3. Paste IdP metadata URL or upload the XML.
4. Configure attribute mapping (default mappings work for most setups).
5. Test with a single account before enforcing org-wide.
