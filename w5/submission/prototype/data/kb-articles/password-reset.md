# Reset your CloudServe password

If you've forgotten your password, follow these steps to reset it. This is a
self-service flow — no agent intervention required.

## Steps

1. Go to https://app.cloudserve.example/login
2. Click **Forgot password?**
3. Enter the email address on your account.
4. Check your inbox for a message from `noreply@cloudserve.example`. The link expires in 60 minutes.
5. Click the link and choose a new password (12+ characters, mix of cases and digits).
6. Sign in with the new password.

## If the email never arrives

- Check spam / junk folder.
- Confirm the email matches the one on your account (the **Profile** page shows it once you're signed in on another device).
- If your account uses SSO (Google / Okta / Azure AD), the reset link is suppressed because passwords are managed by your identity provider — sign in via the SSO option instead.

## If your account is locked

After 5 failed attempts the account is auto-locked for 30 minutes. The lock clears automatically; no agent action required.

For 2FA-related access issues see [2FA troubleshooting](2fa-troubleshooting.md).
