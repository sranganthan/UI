# Multi-Environment Invoice Generation Web UI

A centralized web-based interface for generating Proforma and Definitive invoices across multiple non-production environments (IT, ST, System Test, UAT) with automated email delivery.

## Features

- 🎨 **Modern Web Interface** - Clean, responsive design
- 🖥️ **Multi-Environment Support** - IT, ST, System Test, UAT
- 📄 **Dual Invoice Types** - Proforma and Definitive
- 🔐 **SSH Remote Execution** - Securely connects to backend servers
- 📧 **Automated Email Delivery** - Sends invoices as email attachments
- ⚙️ **Configurable Settings** - Easy SMTP and SSH configuration
- 🔌 **Connection Testing** - Test SSH connectivity before use
- 💫 **Real-time Feedback** - Progress indicators and detailed error messages

## Architecture

```
[Your Windows PC]
     ↓ (Web Browser)
[Flask Web UI] ────SSH───→ [IT Server] ─→ Proforma.sh / Definitive.sh
               ├───SSH───→ [ST Server] ─→ Proforma.sh / Definitive.sh  
               ├───SSH───→ [System Test] ─→ Proforma.sh / Definitive.sh
               └───SSH───→ [UAT Server] ─→ Proforma.sh / Definitive.sh
```

## Quick Start

### 1. Configure Settings
Copy the template configuration file:
```bash
cd invoice_ui
copy config_template.json config.json
```

Edit `config.json` and update:
- **Email Settings:** SMTP server, sender email, password
- **Environment Settings:** For each environment (IT, ST, SystemTest, UAT):
  - Server host/IP and SSH port
  - SSH credentials (username + password OR key file path)
  - Script paths (Proforma.sh and Definitive.sh)
  - Output and log directories

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
**Windows:**
```
start.bat
```

**Linux/Mac:**
```bash
python app.py
```

### 4. Access the Web UI
Open your browser: **http://localhost:5000**

## Usage

1. **Select Environment** - Choose IT, ST, System Test, or UAT
2. **Select Invoice Type** - Proforma or Definitive
3. **Enter Customer ID** - Account number
4. **Enter Email** - Recipient email address
5. **Click Generate** - System connects via SSH, runs script, emails invoice

## Configuration Details

### SSH Authentication
File (config.json)

### Email Configuration
```json
"email": {
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "sender_email": "your-email@gmail.com",
  "sender_password": "your-app-password",
  "use_tls": true
}
```

**For Gmail:** Use App Password (not regular password)
**For Outlook:** Use regular password with smtp.office365.com

### Environment Configuration

Each environment requires:

```json
"IT": {
  "name": "IT Environment",
  "host": "10.26.224.31",
  "port": 22,
  "username": "your-username",
  "password": "your-password",
  "key_file": "",
  "script_paths": {
    "Proforma": "/appl_sw/custbill/scripts/Proforma.sh",
    "Defin_template.json        # Configuration template
├── config.json                 # Your configuration (create from template)
├── README.md                   # This file
├── logs/                       # Application logs (auto-created)
│   └── invoice_*.log          # Timestamped log files
├── temp/                       # Temporary invoice downloads
└── templates/                  # HTML templates
    ├── index.html             # Main invoice generation page
    └── logs.html              # Log viewer
### SSH Authentication Options

**Option 1: Password Authentication**
```json
"username": "your-username",
"password": "your-password",
"key_file": ""
```

**Option 2: SSH Key Authentication** (Recommended)
```json
"username": "your-username",
"password": "",
"key_file": "C:\\Users\\username\\.ssh\\id_rsa"
```

**Note:** On Windows, use double backslashes in paths
```
invoice_ui/
├── app.py                      # Flask application with SSH support
├── requirements.txt            # Python dependencies (Flask + Paramiko)
├── start.bat                   # Windows startup script
├── config.json                 # Auto-generated configuration
├── README.md                   # This file
├── temp/                       # Temporary invoice downloads
└── templates/                  # HTML templates
    ├── index.html             # Main invoice generation page
    ├── settings.html          # Email settings
    └── env_settings.html      # Server/SSH settings
```

## Troubleshooting

### SSH Connection Errors

**"Connection refused"**
- Verify server IP/hostname is correct
- Check SSH port (default 22)
- Ensure firewall allows SSH access

**"Authentication failed"**
- Verify username and password
- For key-based: Ensure private key file path is correct
- Check key file permissions (should be 600 on Linux)

**"Permission denied"**
- Verify user has execute permission on scripts
- Check script paths are correct on server

### Email Not Sending

- Use App Password for Gmail (`config.json`ssword)
- Check firewall settings for SMTP port
- Verify email credentials in Email Settings

### Script Execution Issues

- Verify server details in `config.json` are correct
- Check script exists at configured path on server
- Verify user has permission to execute scripts
- Check application logs in `logs/` folder
- Check server-side logs in configured log path

## Security Best Practices

1. **Use SSH Keys** instead of passwords when possible
2. **Restrict Access** - Run UI on internal network only
3. **HTTPS** - Use reverse proxy with SSL for production
4. **Strong Passwords** - If using password auth
5. **Limited Permissions** - SSH user should have minimal required permissions

## Advanced Configuration

### Custom Portsset `"port"` in environment config.

### Multiple Script Locations
Each environment can have different script paths in `config.json`
Each environment can have different script paths - configure separately.

### Timeout Settings
Script execution timeout is 600 seconds (10 minutes). Modify in `app.py`:
```python
channel.settimeout(600)  # Line ~180
```

## Requirements

- Python 3.7+
- Flask 3.0+
- Paramiko 3.4+ (SSH library)
- SSH access to all target servers
- SMTP email server credentials
- Scripts (Proforma.sh, Definitive.sh) deployed on servers

## Logging

All invoice generation runs create detailed log files in the `logs/` directory:

- **Log File Format:** `invoice_YYYYMMDDHHMMSS_XXXXX.log`
- **Access Logs:** Click **📋 View Logs** in the UI or check the `logs/` folder
- **Log Contents:** 
  - Input parameters
  - SSH connection details
  - Script execution output
  - File search and download details
  - Email delivery status
  - Complete error traces

## Support

For issues:
1. Check application logs in `logs/` folder
2. Review execution output in UI
3. Verify `config.json` settings are correct
4. Check server-side logs in configured log directory
5. Verify script paths and permissions on servers
