from kafka import KafkaProducer
import json

KAFKA_BROKER = 'localhost:9092'
INPUT_TOPIC = 'image-prompts'

def publish_image_prompt(image_path, prompt):
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda m: json.dumps(m).encode('utf-8')
    )

    message = {
        "image_path": image_path,
        "prompt": prompt
    }

    producer.send(INPUT_TOPIC, value=message)
    producer.flush()
    print(f"✅ Sent message to topic '{INPUT_TOPIC}'")

def main():
    image_path = "/home/christopher/Downloads/wallpaperflare.com_wallpaper.jpg"
    prompt = "what is happening in the image?"
    publish_image_prompt(image_path, prompt)


if __name__ == "__main__":
    main()
