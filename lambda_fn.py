import json
import boto3

def lambda_handler(event, context):
    glue = boto3.client('glue')

    # Define your Glue job name here
    glue_job_name = 'ETL_Job'

    # Trigger the Glue job
    response = glue.start_job_run(JobName=glue_job_name)

    return {
        'statusCode': 200,
        'body': json.dumps('Glue job started successfully!')
    }



import json
import boto3
import os

def lambda_handler(event, context):
    sns_client = boto3.client('sns')
    
    # Determine the status from the Step Function input
    status = event.get('Status', 'FAILURE')  # Default to FAILURE if Status is not provided
    
    # Select the SNS topic ARN based on status
    if status.upper() == "SUCCESS":
        topic_arn = os.environ['SUCCESS_TOPIC_ARN']
        subject = "Glue ETL Job Success Notification"
        message = {
            "Status": "SUCCESS",
            "Details": "Glue ETL job completed successfully.",
            "ExecutionInfo": event  # Includes metadata about the Step Function execution
        }
    else:
        topic_arn = os.environ['FAILURE_TOPIC_ARN']
        subject = "Glue ETL Job Failure Notification"
        message = {
            "Status": "FAILURE",
            "Details": "Glue ETL job failed to complete.",
            "ExecutionInfo": event  # Includes metadata about the Step Function execution
        }
    
    # Publish the message to the appropriate SNS topic
    sns_client.publish(
        TopicArn=topic_arn,
        Message=json.dumps(message),
        Subject=subject
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps(f"{status} notification sent")
    }


