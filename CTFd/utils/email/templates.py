def get_verification_email_html(name, otp, confirm_url, ctf_name="XPLOITX 2.0 BETA"):
    """
    Renders an HTML email matching the official XploitX 2.0 BETA verification format.
    """
    display_name = name or "Operative"
    formatted_otp = " ".join(list(str(otp))) if str(otp).isdigit() and len(str(otp)) == 6 else str(otp)

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Verification Code - {ctf_name}</title>
</head>
<body style="margin: 0; padding: 24px 12px; background-color: #030712; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; color: #e6edf3;">
  <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0">
    <tr>
      <td align="center">
        <table role="presentation" style="max-width: 620px; width: 100%; border: 1.5px solid #00ff66; border-radius: 12px; background: #050811; box-shadow: 0 0 25px rgba(0, 255, 102, 0.2);" border="0" cellspacing="0" cellpadding="0">
          <tr>
            <td style="padding: 28px 24px;">
              
              <!-- Header with Logos -->
              <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom: 24px;">
                <tr>
                  <td width="70" align="left" valign="middle" style="padding-right: 8px;">
                    <a href="https://www.xploitxctf.me" target="_blank" style="text-decoration: none; display: block;">
                      <img src="https://www.xploitxctf.me/PEC%20Logo.png" alt="PEC Logo" width="65" height="65" style="display: block; max-width: 65px; height: auto; border: 0;">
                    </a>
                  </td>
                  <td align="center" valign="middle">
                    <div style="color: #ffffff; font-size: 15px; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; line-height: 1.3;">
                      PRATHYUSHA ENGINEERING COLLEGE
                    </div>
                    <div style="color: #8b949e; font-size: 11px; font-weight: 600; letter-spacing: 1px; margin-top: 3px;">
                      (AN AUTONOMOUS INSTITUTION)
                    </div>
                    <div style="color: #c9d1d9; font-size: 12px; font-weight: 700; letter-spacing: 1.5px; margin-top: 4px; text-transform: uppercase;">
                      DEPARTMENT OF CYBER SECURITY
                    </div>
                    <div style="color: #00ff66; font-size: 19px; font-weight: 900; letter-spacing: 2px; margin-top: 6px; text-transform: uppercase; text-shadow: 0 0 10px rgba(0, 255, 102, 0.5);">
                      XPLOITX 2.0 BETA
                    </div>
                  </td>
                  <td width="70" align="right" valign="middle" style="padding-left: 8px;">
                    <a href="https://www.xploitxctf.me" target="_blank" style="text-decoration: none; display: block;">
                      <img src="https://www.xploitxctf.me/xploitx_logo.png" alt="XPLOITX 2.0 BETA" width="75" style="display: block; max-width: 75px; height: auto; border: 0;">
                    </a>
                  </td>
                </tr>
              </table>

              <!-- Main Card -->
              <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="background: #080d1a; border-left: 4px solid #00ff66; border-radius: 8px;">
                <tr>
                  <td style="padding: 28px 24px; text-align: left;">
                    
                    <h2 style="color: #ffffff; text-align: center; margin: 0 0 20px 0; font-size: 22px; font-weight: 700; letter-spacing: 0.5px;">
                      Verification Code
                    </h2>
                    
                    <p style="color: #e6edf3; font-size: 15px; margin: 0 0 12px 0;">
                      Dear <strong style="color: #ffffff;">{display_name}</strong>,
                    </p>
                    
                    <p style="color: #8b949e; font-size: 14px; line-height: 1.6; margin: 0 0 22px 0;">
                      Your one-time verification code for registering in <strong style="color: #ffffff;">XPLOITX 2.0 BETA</strong> is:
                    </p>

                    <!-- OTP Code Box -->
                    <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="margin: 22px 0;">
                      <tr>
                        <td align="center">
                          <div style="display: inline-block; padding: 14px 30px; border: 2px dashed #00ff66; border-radius: 8px; background-color: rgba(0, 255, 102, 0.04); color: #00ff66; font-family: 'Consolas', 'Courier New', Courier, monospace; font-size: 34px; font-weight: 800; letter-spacing: 10px; text-shadow: 0 0 12px rgba(0, 255, 102, 0.45);">
                            {formatted_otp}
                          </div>
                        </td>
                      </tr>
                    </table>

                    <p style="color: #8b949e; font-size: 13px; line-height: 1.5; text-align: center; margin: 18px 0 16px 0;">
                      This OTP is valid for 10 minutes. Please enter this code on the registration page to complete your email verification.
                    </p>

                    <!-- Direct Link Button -->
                    <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="margin: 16px 0 12px 0;">
                      <tr>
                        <td align="center">
                          <a href="{confirm_url}" target="_blank" style="display: inline-block; background-color: #00ff66; color: #000000; font-weight: 800; font-size: 12px; letter-spacing: 1px; padding: 11px 26px; border-radius: 6px; text-decoration: none; text-transform: uppercase;">
                            Or Click Here to Verify Directly
                          </a>
                        </td>
                      </tr>
                    </table>

                    <p style="color: #6e7681; font-size: 12px; line-height: 1.4; text-align: center; margin: 16px 0 0 0;">
                      If you did not request this email, please ignore this message.
                    </p>
                    
                  </td>
                </tr>
              </table>

              <!-- Footer -->
              <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-top: 28px; padding-top: 10px;">
                <tr>
                  <td align="center">
                    <div style="color: #8b949e; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; margin-bottom: 12px; text-transform: uppercase;">
                      CONNECT WITH US &amp; FIND VENUE LOCATION
                    </div>
                    <table role="presentation" border="0" cellspacing="0" cellpadding="0">
                      <tr>
                        <td style="padding: 0 10px;">
                          <a href="https://www.instagram.com/xploitx_pec/" target="_blank" style="display: inline-block; text-decoration: none;">
                            <img src="https://cdn-icons-png.flaticon.com/512/174/174855.png" alt="Instagram" width="28" height="28" style="display: block; border-radius: 6px; border: 0;">
                          </a>
                        </td>
                        <td style="padding: 0 10px;">
                          <a href="https://maps.google.com/?q=Prathyusha+Engineering+College" target="_blank" style="display: inline-block; text-decoration: none;">
                            <img src="https://cdn-icons-png.flaticon.com/512/2991/2991231.png" alt="Google Maps" width="28" height="28" style="display: block; border-radius: 6px; border: 0;">
                          </a>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>

            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
    return html


def get_password_reset_email_html(name, reset_url, ctf_name="XPLOITX 2.0 BETA"):
    """
    Renders an HTML email for password reset in the same XploitX 2.0 BETA format.
    """
    display_name = name or "Operative"

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Password Reset - {ctf_name}</title>
</head>
<body style="margin: 0; padding: 24px 12px; background-color: #030712; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; color: #e6edf3;">
  <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0">
    <tr>
      <td align="center">
        <table role="presentation" style="max-width: 620px; width: 100%; border: 1.5px solid #00ff66; border-radius: 12px; background: #050811; box-shadow: 0 0 25px rgba(0, 255, 102, 0.2);" border="0" cellspacing="0" cellpadding="0">
          <tr>
            <td style="padding: 28px 24px;">
              
              <!-- Header with Logos -->
              <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom: 24px;">
                <tr>
                  <td width="70" align="left" valign="middle" style="padding-right: 8px;">
                    <a href="https://www.xploitxctf.me" target="_blank" style="text-decoration: none; display: block;">
                      <img src="https://www.xploitxctf.me/PEC%20Logo.png" alt="PEC Logo" width="65" height="65" style="display: block; max-width: 65px; height: auto; border: 0;">
                    </a>
                  </td>
                  <td align="center" valign="middle">
                    <div style="color: #ffffff; font-size: 15px; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; line-height: 1.3;">
                      PRATHYUSHA ENGINEERING COLLEGE
                    </div>
                    <div style="color: #8b949e; font-size: 11px; font-weight: 600; letter-spacing: 1px; margin-top: 3px;">
                      (AN AUTONOMOUS INSTITUTION)
                    </div>
                    <div style="color: #c9d1d9; font-size: 12px; font-weight: 700; letter-spacing: 1.5px; margin-top: 4px; text-transform: uppercase;">
                      DEPARTMENT OF CYBER SECURITY
                    </div>
                    <div style="color: #00ff66; font-size: 19px; font-weight: 900; letter-spacing: 2px; margin-top: 6px; text-transform: uppercase; text-shadow: 0 0 10px rgba(0, 255, 102, 0.5);">
                      XPLOITX 2.0 BETA
                    </div>
                  </td>
                  <td width="70" align="right" valign="middle" style="padding-left: 8px;">
                    <a href="https://www.xploitxctf.me" target="_blank" style="text-decoration: none; display: block;">
                      <img src="https://www.xploitxctf.me/xploitx_logo.png" alt="XPLOITX 2.0 BETA" width="75" style="display: block; max-width: 75px; height: auto; border: 0;">
                    </a>
                  </td>
                </tr>
              </table>

              <!-- Main Card -->
              <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="background: #080d1a; border-left: 4px solid #00ff66; border-radius: 8px;">
                <tr>
                  <td style="padding: 28px 24px; text-align: left;">
                    
                    <h2 style="color: #ffffff; text-align: center; margin: 0 0 20px 0; font-size: 22px; font-weight: 700; letter-spacing: 0.5px;">
                      Password Reset Request
                    </h2>
                    
                    <p style="color: #e6edf3; font-size: 15px; margin: 0 0 12px 0;">
                      Dear <strong style="color: #ffffff;">{display_name}</strong>,
                    </p>
                    
                    <p style="color: #8b949e; font-size: 14px; line-height: 1.6; margin: 0 0 22px 0;">
                      We received a request to reset your password for <strong style="color: #ffffff;">XPLOITX 2.0 BETA</strong>. Click the button below to choose a new password:
                    </p>

                    <!-- Reset Button -->
                    <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="margin: 22px 0;">
                      <tr>
                        <td align="center">
                          <a href="{reset_url}" target="_blank" style="display: inline-block; background-color: #00ff66; color: #000000; font-weight: 800; font-size: 13px; letter-spacing: 1px; padding: 12px 28px; border-radius: 6px; text-decoration: none; text-transform: uppercase;">
                            Reset Password Now
                          </a>
                        </td>
                      </tr>
                    </table>

                    <p style="color: #8b949e; font-size: 13px; line-height: 1.5; text-align: center; margin: 18px 0 10px 0;">
                      This link is valid for 30 minutes. If you did not request a password reset, you can safely ignore this email.
                    </p>
                    
                  </td>
                </tr>
              </table>

              <!-- Footer -->
              <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-top: 28px; padding-top: 10px;">
                <tr>
                  <td align="center">
                    <div style="color: #8b949e; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; margin-bottom: 12px; text-transform: uppercase;">
                      CONNECT WITH US &amp; FIND VENUE LOCATION
                    </div>
                    <table role="presentation" border="0" cellspacing="0" cellpadding="0">
                      <tr>
                        <td style="padding: 0 10px;">
                          <a href="https://www.instagram.com/xploitx_pec/" target="_blank" style="display: inline-block; text-decoration: none;">
                            <img src="https://cdn-icons-png.flaticon.com/512/174/174855.png" alt="Instagram" width="28" height="28" style="display: block; border-radius: 6px; border: 0;">
                          </a>
                        </td>
                        <td style="padding: 0 10px;">
                          <a href="https://maps.google.com/?q=Prathyusha+Engineering+College" target="_blank" style="display: inline-block; text-decoration: none;">
                            <img src="https://cdn-icons-png.flaticon.com/512/2991/2991231.png" alt="Google Maps" width="28" height="28" style="display: block; border-radius: 6px; border: 0;">
                          </a>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>

            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
    return html
