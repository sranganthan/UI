# Configuration Setup Guide

## Quick Setup Steps

### 1. Create Configuration File
```bash
# Copy the template
copy config_template.json config.json
```

### 2. Edit config.json

Open `config.json` in a text editor and update the following sections:

#### A. Email Configuration
```json
"email": {
  "smtp_server": "smtp.gmail.com",          ← Your SMTP server
  "smtp_port": 587,                          ← SMTP port (587 for TLS, 465 for SSL)
  "sender_email": "billing@yourcompany.com", ← Your email address
  "sender_password": "your-app-password",    ← Gmail: Use App Password, not regular password
  "use_tls": true                            ← Use TLS encryption
}
```

**For Gmail:**
- Go to Google Account → Security → 2-Step Verification → App Passwords
- Generate an app password and use it here

**For Outlook/Office365:**
- Use `smtp.office365.com` as server
- Use your regular password

#### B. Environment Configuration

For each environment (IT, ST, SystemTest, UAT), update:

```json
"IT": {
  "name": "IT Environment",                              ← Display name
  "host": "10.26.224.31",                                ← Server IP or hostname
  "port": 22,                                            ← SSH port
  "username": "billadmin",                               ← SSH username
  "password": "YourPassword123",                         ← SSH password (OR use key_file)
  "key_file": "",                                        ← SSH key path (OR use password)
  "script_paths": {
    "Proforma": "/appl_sw/custbill/scripts/Proforma.sh", ← Path to Proforma script
    "Definitive": "/appl_sw/custbill/scripts/Definitive.sh" ← Path to Definitive script
  },
  "output_path": "/LOG/CIF/STAMPE",                     ← Where invoice files are generated
  "log_path": "/appl_sw/custbill/log"                   ← Server-side log directory
}
```

**Repeat for all 4 environments:** IT, ST, SystemTest, UAT

### 3. SSH Authentication Options

#### Option A: Password Authentication (Simpler)
```json
"username": "billadmin",
"password": "YourPassword123",
"key_file": ""
```

#### Option B: SSH Key Authentication (More Secure)
```json
"username": "billadmin",
"password": "",
"key_file": "C:\\Users\\yourname\\.ssh\\id_rsa"
```

**Note:** On Windows, use double backslashes (`\\`) in paths

### 4. Verify Configuration

Start the application:
```bash
python app.py
```

Look for these messages:
```
Configuration loaded successfully from config.json
Starting Flask application...
Access the UI at: http://localhost:5000
```

### 5. Test Invoice Generation

1. Open http://localhost:5000
2. Select an environment
3. Choose invoice type
4. Enter customer ID
5. Enter recipient email
6. Click "Generate Invoice"

## Troubleshooting

### "WARNING: config.json not found"
- Run: `copy config_template.json config.json`
- Edit the new `config.json` file

### "ERROR loading config: ..."
- Check JSON syntax (commas, quotes, brackets)
- Use a JSON validator online
- Compare with `config_template.json`

### SSH Connection Fails
- Verify server IP/hostname is correct
- Check username and password
- Ensure SSH port is correct (usually 22)
- Test SSH manually: `ssh username@server-ip`

### Email Not Sending
- For Gmail: Use App Password, not regular password
- Check SMTP server and port
- Verify `use_tls` is `true` for port 587

## Example config.json

```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "billing@company.com",
    "sender_password": "abcd efgh ijkl mnop",
    "use_tls": true
  },
  "environments": {
    "IT": {
      "name": "IT Environment",
      "host": "10.26.224.31",
      "port": 22,
      "username": "billadmin",
      "password": "SecurePass123",
      "key_file": "",
      "script_paths": {
        "Proforma": "/appl_sw/custbill/scripts/Proforma.sh",
        "Definitive": "/appl_sw/custbill/scripts/Definitive.sh"
      },
      "output_path": "/LOG/CIF/STAMPE",
      "log_path": "/appl_sw/custbill/log"
    }
  }
}
```

## Security Tips

1. **Never commit config.json to Git** - Add it to `.gitignore`
2. **Use SSH keys** instead of passwords when possible
3. **Restrict file permissions** on config.json (Windows: right-click → Properties → Security)
4. **Use strong passwords** for SSH and email
5. **Keep config_template.json** as reference (without real credentials)
