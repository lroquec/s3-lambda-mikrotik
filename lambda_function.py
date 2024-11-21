import os
import pandas as pd
import re
import boto3
import io
from urllib.parse import unquote_plus

def normalize_mac(mac):
    """Normalize MAC to the format 50:91:e3:9c:67:3e."""
    if isinstance(mac, str):
        mac = re.sub(r'[^0-9a-fA-F]', '', mac)  # Remove non-hex characters
        if len(mac) == 12:
            mac = ':'.join(mac[i:i+2] for i in range(0, 12, 2))
            return mac.lower()  # Return normalized MAC
    return None  # Return None if not valid

def is_valid_ip(ip):
    """Validate IPv4 address."""
    if isinstance(ip, str):
        pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9][0-9]?)$'
        if re.match(pattern, ip):
            return ip  # Return IP if valid
    return None  # Return None if not valid


def create_mikrotik_script(df):
    """
    Create a Mikrotik script from DataFrame.
    Returns the script content as a string.
    """
    script_lines = [
        ":global roscsv [:toarray \"\"];\n"
    ]
    
    for _, row in df.iterrows():
        line = f':set roscsv ($roscsv, {{ {{"Hostname"="{row["HOSTNAME"]}";"MAC"="{row["MAC"]}";"IP"="{row["IP"]}";}} }})\n'
        script_lines.append(line)
    
    # Add the verification and netwatch configuration part
    script_lines.extend([
        "\n# Print list content for verification",
        ':put "Initial content of roscsv list:"',
        ':foreach i in=$roscsv do={',
        '    :put ("IP: " . $i->"IP" . " Hostname: " . $i->"Hostname" . " MAC: " . $i->"MAC")',
        '}',
        '\n# Add devices to Netwatch',
        ':foreach i in=$roscsv do={',
        '    :local ipValue ($i->"IP");',
        '    :local hostnameValue ($i->"Hostname");',
        '    :local macValue ($i->"MAC");',
        '    :local commentValue ($hostnameValue . " " . $macValue);',
        '',
        '    # Print values to be added',
        '    :put ("Adding host: " . $ipValue . " with comment: " . $commentValue);',
        '',
        '    # Add to Netwatch',
        '    /tool netwatch add host=$ipValue comment=$commentValue disabled=no',
        '}'
    ])
    
    return '\n'.join(script_lines)


def process_file(s3_client, bucket, key):
    OUTPUT_PATH = os.environ.get('OUTPUT_PATH', 'output/')
    """Process input file from S3 and create Mikrotik script."""
    try:
        # Get file from S3
        response = s3_client.get_object(Bucket=bucket, Key=key)
        file_extension = key.split('.')[-1].lower()
        
        # Read file content
        if file_extension == 'xlsx':
            data = pd.read_excel(io.BytesIO(response['Body'].read()), sheet_name=0)
        elif file_extension == 'csv':
            data = pd.read_csv(io.BytesIO(response['Body'].read()))
        else:
            raise ValueError("Unsupported file type. Please provide an Excel or CSV file.")

        # Normalize column names
        data.columns = [col.strip().upper() for col in data.columns]

        # Define mappings for both Excel and CSV
        column_map = {
            'HOSTNAME': 'HOSTNAME',
            'DEVICE NAME': 'HOSTNAME',
            'MAC': 'MAC',
            'MAC ADDRESS': 'MAC',
            'IP': 'IP',
            'IP ADDRESS': 'IP'
        }

        # Rename columns based on the map
        data.rename(columns={col: column_map[col] for col in data.columns if col in column_map}, inplace=True)

        # Check if required columns are present
        required_columns = ['HOSTNAME', 'MAC', 'IP']
        if not all(col in data.columns for col in required_columns):
            raise KeyError("Missing required columns in the input file.")

        # Normalize and validate MAC and IP addresses
        data['MAC'] = data['MAC'].apply(normalize_mac)
        data['IP'] = data['IP'].apply(is_valid_ip)

        # Filter rows: Keep only those with valid MAC and IP
        filtered_data = data.dropna(subset=['MAC', 'IP'])

        # Select required columns
        output_data = filtered_data[required_columns]

        # Generate output paths
        file_name = key.split('/')[-1].rsplit('.', 1)[0]
        csv_output_key = f'{OUTPUT_PATH}{file_name}.csv'
        script_output_key = f'{OUTPUT_PATH}{file_name}.rsc'

        # Save CSV to S3
        csv_buffer = io.StringIO()
        output_data.to_csv(csv_buffer, index=False)
        s3_client.put_object(
            Bucket=bucket,
            Key=csv_output_key,
            Body=csv_buffer.getvalue()
        )

        # Generate and save Mikrotik script to S3
        script_content = create_mikrotik_script(output_data)
        s3_client.put_object(
            Bucket=bucket,
            Key=script_output_key,
            Body=script_content
        )

        return {
            'statusCode': 200,
            'body': f'Successfully processed {key} and generated output files'
        }

    except Exception as e:
        print(f"Error processing file: {e}")
        raise e

def lambda_handler(event, context):
    # Get environment variables
    INPUT_PATH = os.environ.get('INPUT_PATH', 'input/')
    OUTPUT_PATH = os.environ.get('OUTPUT_PATH', 'output/')

    s3_client = boto3.client('s3')
    
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        
        # Use environment variable for input path
        if key.startswith(INPUT_PATH):
            return process_file(s3_client, bucket, key)
