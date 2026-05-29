# 2FA troubleshooting

Two-factor authentication (2FA) protects your account from unauthorised access. If you can't get a code, here's the fix order.

## I lost my authenticator device

1. Use a **backup code** if you saved them at setup.
2. If no backup codes: **request a recovery email** from the sign-in page. We send a one-time link valid for 60 minutes.
3. If recovery email isn't arriving, contact support — a human agent will verify identity (last 4 of payment card on file, last login city, account creation month) before disabling 2FA.

## My code isn't accepted

- Check the device's clock is set to **automatic / network time**. TOTP codes drift if local time is wrong.
- Try the **next** code (codes rotate every 30 seconds).
- If you re-installed the authenticator app, the secret is gone — use a backup code, then re-enrol.

## I want to disable 2FA

Disabling 2FA on an account is a security-sensitive operation. The agent can route you to the right place but **cannot disable 2FA on your behalf**. You must sign in with current credentials and toggle it off in **Profile → Security**.
