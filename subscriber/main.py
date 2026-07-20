import os
import json
from google.cloud import pubsub_v1
from app.services import vertex_ai_service, drive_service, gcs_service
from app.processors import image_enhancement_processor, text_normalization_processor, drive_upload_processor

PROJECT_ID = os.environ.get("PROJECT_ID")
SUBSCRIPTION_ID = os.environ.get("PUBSUB_SUBSCRIPTION_ID")

def process_message(message):
    """Process a single Pub/Sub message"""
    try:
        data = json.loads(message.data.decode('utf-8'))
        job_id = data['job_id']

        print(f"Processing job: {job_id}")

        # 1. Enhance images
        enhanced_images = image_enhancement_processor.process(job_id)

        # 2. Normalize text and generate WhatsApp message
        normalized_data = text_normalization_processor.process(job_id)

        # 3. Upload to Drive
        drive_links = drive_upload_processor.process(job_id, enhanced_images, normalized_data)

        print(f"Job {job_id} completed successfully")
        return True

    except Exception as e:
        print(f"Error processing job: {str(e)}")
        return False

def main():
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

    def callback(message):
        success = process_message(message)
        if success:
            message.ack()
        else:
            message.nack()

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}...")

    with subscriber:
        try:
            streaming_pull_future.result()
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
