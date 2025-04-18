from fastapi import FastAPI
from pydantic import BaseModel
from kafka import KafkaProducer
import json
import os

app = FastAPI()

KAFKA_BROKER = 'localhost:9092'
INPUT_TOPIC = 'image-prompts'

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda m: json.dumps(m).encode('utf-8')
)

class Item(BaseModel):
    image_path: str

@app.get("/")
def read_root():
    return {"message": "Welcome to Question Verse"}

@app.post("/v1/input_image")
def send_to_kafka(item: Item):
    message = {"image_path": item.image_path}
    producer.send(INPUT_TOPIC, value=message)
    producer.flush()
    return {"status": "Message sent to Kafka", "image_path": item.image_path}
