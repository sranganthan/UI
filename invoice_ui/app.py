#!/usr/bin/env python3
"""
Flask Web Application for Multi-Environment Invoice Generation
Supports Proforma and Definitive invoices across IT, ST, System Test, and UAT environments
"""

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import subprocess
import os
import glob
from datetime import datetime
import json
import paramiko
from io import StringIO
import re
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Configuration
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')

# Create logs directory if it doesn't exist
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Check if config file exists, if not copy from template
if not os.path.exists(CONFIG_FILE):
    template_file = os.path.join(os.path.dirname(__file__), 'config_template.json')
    if os.path.exists(template_file):
        import shutil
        shutil.copy(template_file, CONFIG_FILE)
        print(f"Created {CONFIG_FILE} from template. Please update with your settings.")
    else:
        print(f"ERROR: {CONFIG_FILE} not found. Please create it from config_template.json")

def get_next_log_sequence():
    """Get next sequence number for log file"""
    today = datetime.now().strftime('%Y%m%d')
    pattern = os.path.join(LOG_DIR, f'invoice_{today}*.log')
    existing_logs = glob.glob(pattern)
    
    if not existing_logs:
        return 1
    
    # Extract sequence numbers
    sequences = []
    for log_file in existing_logs:
        basename = os.path.basename(log_file)
        # Extract sequence from invoice_YYYYMMDDHHMMSS_XXXXX.log
        match = re.search(r'_(\d{5})\.log$', basename)
        if match:
            sequences.append(int(match.group(1)))
    
    return max(sequences) + 1 if sequences else 1

def setup_invoice_logger():
    """Create a new logger for each invoice generation run"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    sequence = get_next_log_sequence()
    log_filename = f'invoice_{timestamp}_{sequence:05d}.log'
    log_path = os.path.join(LOG_DIR, log_filename)
    
    # Create logger
    logger = logging.getLogger(log_filename)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    
    # Clear any existing handlers
    logger.handlers = []
    
    # File handler
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger, log_path

# Environment server configurations
ENVIRONMENTS = {
    'IT': {
        'name': 'IT Environment',
        'host': '',
        'port': 22,
        'username': '',
        'password': '',
        'key_file': '',
        'script_paths': {
            'Proforma': '/appl_sw/custbill/scripts/Proforma.sh',
            'Definitive': '/appl_sw/custbill/scripts/Definitive.sh'
        },
        'output_path': '/LOG/CIF/STAMPE',
        'log_path': '/appl_sw/custbill/log'
    },
    'ST': {
        'name': 'ST Environment',
        'host': '',
        'port': 22,
        'username': '',
        'password': '',
        'key_file': '',
        'script_paths': {
            'Proforma': '/appl_sw/custbill/scripts/Proforma.sh',
            'Definitive': '/appl_sw/custbill/scripts/Definitive.sh'
        },
        'output_path': '/LOG/CIF/STAMPE',
        'log_path': '/appl_sw/custbill/log'
    },
    'SystemTest': {
        'name': 'System Test Environment',
        'host': '',
        'port': 22,
        'username': '',
        'password': '',
        'key_file': '',
        'script_paths': {
            'Proforma': '/appl_sw/custbill/scripts/Proforma.sh',
            'Definitive': '/appl_sw/custbill/scripts/Definitive.sh'
        },
        'output_path': '/LOG/CIF/STAMPE',
        'log_path': '/appl_sw/custbill/log'
    },
    'UAT': {
        'name': 'UAT Environment',
        'host': '',
        'port': 22,
        'username': '',
        'password': '',
        'key_file': '',
        'script_paths': {
            'Proforma': '/appl_sw/custbill/scripts/Proforma.sh',
            'Definitive': '/appl_sw/custbill/scripts/Definitive.sh'
        },
        'output_path': '/LOG/CIF/STAMPE',
        'log_path': '/appl_sw/custbill/log'
    }
}

def load_config():
    """Load configuration from config.json and update ENVIRONMENTS"""
    global ENVIRONMENTS
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            
            # Load environment configs from config file
            if 'environments' in config:
                for env_key, env_data in config['environments'].items():
                    if env_key in ENVIRONMENTS:
                        ENVIRONMENTS[env_key].update(env_data)
                print(f"Configuration loaded from {CONFIG_FILE}")
        else:
            print(f"Warning: {CONFIG_FILE} not found. Using default configuration.")
    except Exception as e:
        print(f"Error loading config: {str(e)}")

def create_ssh_client(env_config):
    """Create and return an SSH client connection"""
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect using key file or password
        if env_config.get('key_file'):
            key = paramiko.RSAKey.from_private_key_file(env_config['key_file'])
            client.connect(
                hostname=env_config['host'],
                port=env_config.get('port', 22),
                username=env_config.get('user', env_config.get('username', '')),
                pkey=key,
                timeout=10
            )
        else:
            client.connect(
                hostname=env_config['host'],
                port=env_config.get('port', 22),
                username=env_config.get('user', env_config.get('username', '')),
                password=env_config.get('password', ''),
                timeout=10
            )
        
        return client, None
        
    except Exception as e:
        return None, f"SSH connection failed: {str(e)}"

def test_connection():
    """Test SSH connection to an environment using Plink"""
    try:
        data = request.get_json()
        env_key = data.get('environment')
        if env_key not in ENVIRONMENTS:
            return jsonify({'success': False, 'message': 'Invalid environment'}), 400
        env_config = ENVIRONMENTS[env_key]
        
        # Use Plink for all environments (supports jump hosts/CyberArk)
        plink_path = r'C:\Program Files\PuTTY\plink.exe'
        remote_command = 'echo "Connection successful"'
        
        user = env_config.get('user', env_config.get('username', ''))
        password = env_config.get('password', '')
        host = env_config.get('host', '')
        
        if not user or not host:
            return jsonify({'success': False, 'message': 'User or host not configured'}), 400
        
        # Construct connection string
        connection_string = f"{user}@{host}"
        
        try:
            # Use plink with password authentication
            result = subprocess.run(
                [plink_path, '-ssh', connection_string, '-pw', password, '-batch', remote_command],
                capture_output=True, text=True, timeout=30
            )
            if 'Connection successful' in result.stdout:
                return jsonify({'success': True, 'message': f'Connection successful to {env_key}!'})
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                return jsonify({'success': False, 'message': f'Connection failed: {error_msg}'}), 500
        except subprocess.TimeoutExpired:
            return jsonify({'success': False, 'message': 'Connection timeout'}), 500
        except Exception as e:
            return jsonify({'success': False, 'message': f'Plink error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
        if env_config.get('key_file') and os.path.exists(env_config['key_file']):
            key = paramiko.RSAKey.from_private_key_file(env_config['key_file'])
            client.connect(
                hostname=env_config['host'],
                port=env_config['port'],
                username=env_config['username'],
                pkey=key,
                timeout=30
            )
        else:
            client.connect(
                hostname=env_config['host'],
                port=env_config['port'],
                username=env_config['username'],
                password=env_config['password'],
                timeout=30
            )
        
        return client, None
    except Exception as e:
        return None, f"SSH connection failed: {str(e)}"

def extract_external_id_from_output(output):
    """Extract external_id from script output"""
    try:
        # Look for patterns like "external_id=XXXXX" or similar in the output
        import re
        
        # Try common patterns
        patterns = [
            r'external_id[:\s=]+([A-Z0-9_]+)',
            r'External_id[:\s=]+([A-Z0-9_]+)',
            r'EXTERNAL_ID[:\s=]+([A-Z0-9_]+)',
            r'external_id found:\s*([A-Z0-9_]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                external_id = match.group(1).strip()
                if external_id and len(external_id) > 0:
                    return external_id
        
        return None
    except Exception as e:
        return None

def find_latest_invoice_file_remote(ssh_client, output_path, invoice_type, external_id=None, logger=None):
    """
    Find the most recently created invoice file on remote server
    Optionally verify it contains the external_id
    Examples:
      Definitive: 20240101_BILR_60784_00001_N.txt (60784 is external_id)
      Proforma: FZ______FN_8_20211001_20260202165856.txt (FZ______FN_8 is external_id)
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    try:
        # Find the most recent .txt file created in the last 10 minutes
        command = f"find {output_path} -name '*.txt' -type f -mmin -10 -printf '%T@ %p\\n' 2>/dev/null | sort -rn | head -5"
        logger.debug(f"Find command: {command}")
        
        stdin, stdout, stderr = ssh_client.exec_command(command, timeout=10)
        output_lines = stdout.read().decode().strip().split('\n')
        
        logger.debug(f"Find command output: {output_lines}")
        
        if not output_lines or output_lines[0] == '':
            logger.warning("No .txt file found in output directory (searched files created in last 10 minutes)")
            return None, "No .txt file found in output directory (searched files created in last 10 minutes)"
        
        logger.info(f"Found {len(output_lines)} recent files, checking for external_id match...")
        
        # If external_id provided, find file containing it
        if external_id:
            for line in output_lines:
                if ' ' in line:
                    timestamp, filepath = line.split(' ', 1)
                    filename = filepath.split('/')[-1]
                    logger.debug(f"Checking file: {filename}")
                    
                    # Check if external_id is in the filename
                    if external_id in filename:
                        logger.info(f"Found matching invoice file: {filename}")
                        return filepath.strip(), None
            
            # If we reach here, external_id not found in any recent file
            logger.warning(f"No file found containing external_id '{external_id}'. Using most recent file.")
            most_recent = output_lines[0].split(' ', 1)[1].strip() if ' ' in output_lines[0] else None
            return most_recent, f"Warning: Most recent file found but does not contain external_id '{external_id}'. Proceeding with most recent file."
        else:
            # No external_id provided, return most recent
            if ' ' in output_lines[0]:
                latest_file = output_lines[0].split(' ', 1)[1].strip()
                logger.info(f"Found most recent file: {latest_file}")
                return latest_file, None
            else:
                logger.error("Could not parse file listing")
                return None, "Could not parse file listing"
            
    except Exception as e:
        logger.error(f"Error finding invoice file: {str(e)}")
        return None, f"Error finding invoice file: {str(e)}"

def download_file_from_server(ssh_client, remote_path, local_path):
    """Download file from remote server using SFTP"""
    try:
        sftp = ssh_client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
        return True, None
    except Exception as e:
        return False, f"Failed to download file: {str(e)}"

def download_file_from_server(ssh_client, remote_path, local_path, logger=None):
    """Download file from remote server using SFTP"""
    if logger is None:
        logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Downloading file via SFTP...")
        logger.debug(f"Remote path: {remote_path}")
        logger.debug(f"Local path: {local_path}")
        sftp = ssh_client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
        logger.info("File downloaded successfully")
        return True, None
    except Exception as e:
        logger.error(f"Failed to download file: {str(e)}")
        return False, f"Failed to download file: {str(e)}"



def run_remote_invoice_script(environment, invoice_type, account_no, logger=None):
    """Execute invoice script on remote server via SSH"""
    if logger is None:
        logger = logging.getLogger(__name__)
    
    try:
        env_config = ENVIRONMENTS.get(environment)
        if not env_config:
            logger.error(f"Unknown environment: {environment}")
            return False, "", f"Unknown environment: {environment}", None
        
        # Validate configuration
        if not env_config.get('host'):
            logger.error(f"Server host not configured for {environment}")
            return False, "", f"Server host not configured for {environment}", None
        
        # Get script path
        script_path = env_config['script_paths'].get(invoice_type)
        if not script_path:
            logger.error(f"Script path not configured for {invoice_type}")
            return False, "", f"Script path not configured for {invoice_type}", None
        
        # Create SSH connection
        logger.info(f"Connecting to {env_config['host']}:{env_config.get('port', 22)}...")
        ssh_client, error = create_ssh_client(env_config)
        if error:
            logger.error(f"SSH connection failed: {error}")
            return False, "", error, None
        
        logger.info("SSH connection established successfully")
        
        try:
            # Execute script with account_no as input
            command = f"bash {script_path}"
            logger.info(f"Executing command: {command}")
            
            # Create channel for interactive command
            channel = ssh_client.invoke_shell()
            channel.send(f"{command}\n")
            
            # Wait a moment for prompt
            import time
            time.sleep(2)
            
            # Send account number
            logger.info(f"Sending customer ID: {account_no}")
            channel.send(f"{account_no}\n")
            logger.info("Waiting for script execution (timeout: 10 minutes)...")
            
            # Collect output with timeout
            output = ""
            channel.settimeout(600)  # 10 minutes timeout
            
            try:
                while True:
                    if channel.recv_ready():
                        chunk = channel.recv(4096).decode('utf-8', errors='ignore')
                        output += chunk
                    
                    if channel.exit_status_ready():
                        # Get any remaining output
                        while channel.recv_ready():
                            chunk = channel.recv(4096).decode('utf-8', errors='ignore')
                            output += chunk
                        break
                    
                    time.sleep(0.5)
            except Exception as e:
                logger.warning(f"Timeout or error during output collection: {str(e)}")
                output += f"\n[Timeout or error: {str(e)}]"
            
            exit_status = channel.recv_exit_status()
            channel.close()
            
            logger.info(f"Script execution completed with exit code: {exit_status}")
            logger.debug(f"Script output:\n{output}")
            
            if exit_status == 0:
                logger.info("Script executed successfully")
                return True, output, None, ssh_client
            else:
                logger.error(f"Script failed with exit code {exit_status}")
                ssh_client.close()
                return False, output, f"Script exited with code {exit_status}", None
        
        except Exception as e:
            logger.error(f"Error during script execution: {str(e)}")
            ssh_client.close()
            return False, "", str(e), None
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False, "", str(e), None

@app.route('/')
def index():
    """Render the main page"""
    # Pass environment names to template
    env_list = [{'key': k, 'name': v['name']} for k, v in ENVIRONMENTS.items()]
    return render_template('index.html', environments=env_list)



@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    """Handle invoice generation request"""
    # Setup logger for this run
    logger, log_path = setup_invoice_logger()
    
    logger.info("="*80)
    logger.info("INVOICE GENERATION STARTED")
    logger.info("="*80)
    
    ssh_client = None
    try:
        data = request.get_json()
        environment = data.get('environment', '').strip()
        invoice_type = data.get('invoice_type', '').strip()
        account_no = data.get('account_no', '').strip()
        
        # Log input parameters
        logger.info("Input Parameters:")
        logger.info(f"  Environment: {environment}")
        logger.info(f"  Invoice Type: {invoice_type}")
        logger.info(f"  Customer ID: {account_no}")
        
        # Validate inputs
        logger.info("Validating input parameters...")
        if not environment:
            logger.error("Validation failed: Environment is required")
            return jsonify({'success': False, 'message': 'Environment is required', 'log_file': os.path.basename(log_path)}), 400
        
        if not invoice_type:
            logger.error("Validation failed: Invoice type is required")
            return jsonify({'success': False, 'message': 'Invoice type is required', 'log_file': os.path.basename(log_path)}), 400
        
        if not account_no:
            logger.error("Validation failed: Customer ID is required")
            return jsonify({'success': False, 'message': 'Customer ID is required', 'log_file': os.path.basename(log_path)}), 400
        
        logger.info("Input validation passed")
        
        # Get environment configuration
        logger.info(f"Loading configuration for environment: {environment}")
        env_config = ENVIRONMENTS.get(environment)
        if not env_config:
            logger.error(f"Unknown environment: {environment}")
            return jsonify({'success': False, 'message': f'Unknown environment: {environment}', 'log_file': os.path.basename(log_path)}), 400
        
        # Log server connection details (mask password)
        logger.info("Server Connection Details:")
        logger.info(f"  Host: {env_config.get('host', 'Not configured')}")
        logger.info(f"  Port: {env_config.get('port', 22)}")
        logger.info(f"  Username: {env_config.get('username', 'Not configured')}")
        logger.info(f"  Auth Method: {'SSH Key' if env_config.get('key_file') else 'Password'}")
        logger.info(f"  Script Path: {env_config['script_paths'].get(invoice_type, 'Not configured')}")
        logger.info(f"  Output Path: {env_config.get('output_path', 'Not configured')}")
        
        # Check if script path is configured
        if not env_config['script_paths'].get(invoice_type):
            logger.error(f"Script path not configured for {invoice_type}")
            return jsonify({'success': False, 'message': f'Script path not configured for {invoice_type}', 'log_file': os.path.basename(log_path)}), 400
        
        # Run the script on remote server
        logger.info("="*80)
        logger.info("EXECUTING INVOICE SCRIPT ON REMOTE SERVER")
        logger.info("Script will handle invoice generation and email delivery")
        logger.info("="*80)
        
        result = run_remote_invoice_script(environment, invoice_type, account_no, logger)
        
        if len(result) == 4:
            success, stdout, stderr, ssh_client = result
        else:
            success, stdout, stderr = result
            ssh_client = None
        
        if not success:
            logger.error(f"Script execution failed: {stderr}")
            logger.info("="*80)
            logger.info("INVOICE GENERATION FAILED")
            logger.info("="*80)
            return jsonify({
                'success': False,
                'message': f'Script execution failed: {stderr}',
                'output': stdout,
                'log_file': os.path.basename(log_path)
            }), 500
        
        # Close SSH connection
        if ssh_client:
            ssh_client.close()
            logger.info("SSH connection closed")
        
        # Script handles email sending, so we're done
        logger.info("="*80)
        logger.info("INVOICE GENERATION COMPLETED SUCCESSFULLY")
        logger.info("Script has handled invoice generation and email delivery")
        logger.info("="*80)
        logger.info(f"Log file: {os.path.basename(log_path)}")
        
        return jsonify({
            'success': True,
            'message': f'{invoice_type} invoice for {environment} environment generated successfully. Email sent by script.',
            'output': stdout,
            'log_file': os.path.basename(log_path)
        })
    
    except Exception as e:
        logger.exception("Unexpected error during invoice generation")
        logger.info("="*80)
        logger.info("INVOICE GENERATION FAILED")
        logger.info("="*80)
        if ssh_client:
            try:
                ssh_client.close()
            except:
                pass
        return jsonify({'success': False, 'message': str(e), 'log_file': os.path.basename(log_path)}), 500

@app.route('/test_connection', methods=['POST'])
def test_connection():
    """Test SSH connection to an environment"""
    try:
        data = request.get_json()
        env_key = data.get('environment')
        
        if env_key not in ENVIRONMENTS:
            return jsonify({'success': False, 'message': 'Invalid environment'}), 400
        
        env_config = ENVIRONMENTS[env_key]
        
        if not env_config.get('host'):
            return jsonify({'success': False, 'message': 'Server host not configured'}), 400
        
        ssh_client, error = create_ssh_client(env_config)
        
        if error:
            return jsonify({'success': False, 'message': error}), 500
        
        # Test connection by running simple command
        stdin, stdout, stderr = ssh_client.exec_command('echo "Connection successful"')
        result = stdout.read().decode().strip()
        ssh_client.close()
        
        if result:
            return jsonify({'success': True, 'message': 'Connection successful!'})
        else:
            return jsonify({'success': False, 'message': 'Connection failed'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/logs')
def view_logs():
    """View recent log files"""
    try:
        log_files = []
        if os.path.exists(LOG_DIR):
            files = glob.glob(os.path.join(LOG_DIR, 'invoice_*.log'))
            files.sort(key=os.path.getmtime, reverse=True)
            
            for log_file in files[:10]:  # Show latest 10 logs
                log_files.append({
                    'name': os.path.basename(log_file),
                    'path': log_file,
                    'modified': datetime.fromtimestamp(os.path.getmtime(log_file)).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        return render_template('logs.html', logs=log_files)
    except Exception as e:
        return render_template('logs.html', logs=[], error=str(e))

@app.route('/view_log/<path:log_name>')
def view_log_content(log_name):
    """View content of a specific log file"""
    try:
        log_path = os.path.join(LOG_DIR, log_name)
        
        # Security check
        if not os.path.abspath(log_path).startswith(os.path.abspath(LOG_DIR)):
            return "Invalid log file", 403
        
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                content = f.read()
            return render_template('log_content.html', log_name=log_name, content=content)
        else:
            return "Log file not found", 404
    except Exception as e:
        return f"Error reading log: {str(e)}", 500

if __name__ == '__main__':
    # Load configuration on startup
    load_config()
    
    print("\n" + "="*60)
    print("Multi-Environment Invoice Generator")
    print("="*60)
    print(f"Configuration file: {CONFIG_FILE}")
    print(f"Log directory: {LOG_DIR}")
    print("\nStarting Flask application...")
    print("Access the UI at: http://localhost:5000")
    print("="*60 + "\n")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
