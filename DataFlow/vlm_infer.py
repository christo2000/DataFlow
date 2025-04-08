import requests
from PIL import Image
import base64
from io import BytesIO
from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
import json
import os
import time

# Hugging Face API settings
API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN', '')}"}

# Kafka settings
KAFKA_BROKER = 'localhost:9092'
INPUT_TOPIC = 'image-prompts'
OUTPUT_TOPIC = 'inference-results'

def image_to_base64(image_path):
    try:
        with Image.open(image_path) as img:
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        print(f"[ERROR] Unable to open image {image_path}: {e}")
        return None

def run_blip_inference(image_path: str) -> str:
    image_base64 = image_to_base64(image_path)
    if not image_base64:
        return "Failed to encode image."

    payload = {"inputs": {"image": image_base64}}

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        result = response.json()
        if isinstance(result, dict) and "error" in result:
            return f"Error: {result['error']}"
        return result[0]["generated_text"]
    except Exception as e:
        return f"API request failed: {e}"

def ensure_topic_exists(topic_name: str, broker: str):
    try:
        admin = KafkaAdminClient(bootstrap_servers=broker)
        if topic_name not in admin.list_topics():
            admin.create_topics([NewTopic(name=topic_name, num_partitions=1, replication_factor=1)])
            print(f"[✅] Created topic: {topic_name}")
        admin.close()
    except Exception as e:
        print(f"[ERROR] Could not ensure topic '{topic_name}': {e}")

def main():
    ensure_topic_exists(INPUT_TOPIC, KAFKA_BROKER)
    ensure_topic_exists(OUTPUT_TOPIC, KAFKA_BROKER)

    consumer = KafkaConsumer(
        INPUT_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        group_id="blip-infer-group",
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda m: json.dumps(m).encode('utf-8')
    )

    print("🟢 BLIP worker running... Polling Kafka every 1s.")

    while True:
        msg_pack = consumer.poll(timeout_ms=1000)
        if not msg_pack:
            print("⏳ No new messages. Still waiting...")
            continue

        for tp, messages in msg_pack.items():
            for msg in messages:
                try:
                    data = msg.value
                    image_path = data.get("image_path")
                    print(f"\n📥 Received image path: {image_path}")

                    caption = run_blip_inference(image_path)
                    output = {
                        "image_path": image_path,
                        "caption": caption
                    }

                    print(f"[📤] Sending caption to Kafka: {json.dumps(output, indent=2)}")
                    producer.send(OUTPUT_TOPIC, value=output)
                    producer.flush()

                except Exception as e:
                    print(f"[ERROR] Failed to process message: {e}")


if __name__ == "__main__":
    main()
