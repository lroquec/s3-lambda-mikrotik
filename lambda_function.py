import pandas as pd
import re
import boto3
import io
from urllib.parse import unquote_plus

# Get environment variables
INPUT_PATH = os.environ.get('INPUT_PATH', 'input/')
OUTPUT_PATH = os.environ.get('OUTPUT_PATH', 'output/')

def normalize_mac(mac):
    pass

def is_valid_ip(ip):
    pass

def create_mikrotik_script(df):
    """
    Create a Mikrotik script from DataFrame.
    Returns the script content as a string.
    """
    script_lines = [":global roscsv [:toarray \"\"];\n"]
    
    for _, row in df.iterrows():
        line = f':set roscsv ($roscsv, {{ {{"Hostname"="{row["HOSTNAME"]}";"MAC"="{row["MAC"]}";"IP"="{row["IP"]}";}} }})\n'
        script_lines.append(line)
    
    
    return '\n'.join(script_lines)

def process_file(s3_client, bucket, key):
    """Process input file from S3 and create Mikrotik script."""
    try:
        # Get file from S3
        response = s3_client.get_object(Bucket=bucket, Key=key)
        file_extension = key.split('.')[-1].lower()
        
        # Read file content
        if file_extension == 'xlsx':
            data = pd.read_excel(io.BytesIO(response['Body'].read()))
        elif file_extension == 'csv':
            data = pd.read_csv(io.BytesIO(response['Body'].read()))
        else:
            raise ValueError("Unsupported file type. Please provide an Excel or CSV file.")

        # [Rest of your data processing logic]
        # Normalize column names
        data.columns = [col.strip().upper() for col in data.columns]
        
        # [Rest of your column mapping and data processing]
        
        # Generate output paths usando las variables de entorno
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
    s3_client = boto3.client('s3')
    
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        
        # Use environment variable for input path
        if key.startswith(INPUT_PATH):
            return process_file(s3_client, bucket, key)
