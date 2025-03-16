from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import ClientError
import os

app = Flask(__name__)

# AWS SES configuration
AWS_REGION = os.environ.get('AWS_SES_REGION', 'ap-southeast-2')
AWS_ACCESS_KEY = os.environ.get('AWS_SES_ACCESS_KEY', '')
AWS_SECRET_KEY = os.environ.get('AWS_SES_SECRET_KEY', '')

# Create SES client
def get_ses_client():
    return boto3.client('ses',
                      region_name=AWS_REGION,
                      aws_access_key_id=AWS_ACCESS_KEY,
                      aws_secret_access_key=AWS_SECRET_KEY)

@app.route('/')
def health_check():
    return jsonify({"status": "healthy", "service": "notification-service"})

@app.route('/api/email/send', methods=['POST'])
def send_email():
    data = request.get_json()
    
    # Validate input
    required_fields = ['to', 'from', 'subject', 'body']
    for field in required_fields:
        if field not in data:
            return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
    
    recipient = data['to']
    sender = data['from']
    subject = data['subject']
    body_html = data['body']
    is_html = data.get('isHtml', True)
    
    # Create the email
    try:
        ses = get_ses_client()
        
        email_message = {
            'Subject': {'Data': subject},
            'Body': {}
        }
        
        if is_html:
            email_message['Body']['Html'] = {'Data': body_html}
        else:
            email_message['Body']['Text'] = {'Data': body_html}
        
        response = ses.send_email(
            Source=sender,
            Destination={'ToAddresses': [recipient]},
            Message=email_message
        )
        
        return jsonify({
            "success": True,
            "messageId": response['MessageId']
        })
        
    except ClientError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)