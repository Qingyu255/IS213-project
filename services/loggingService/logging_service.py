import os
import time
import json
import threading
from datetime import datetime

import pika
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flasgger import Swagger
from prometheus_client import Counter, Histogram, generate_latest


load_dotenv(dotenv_path="../../.env", override=True)

POSTGRES_HOST=os.getenv("LOGGING_DB_HOST")
POSTGRES_PORT=5432
POSTGRES_USER=os.getenv("LOGGING_DB_USER")
POSTGRES_PASSWORD=os.getenv("LOGGING_DB_PASSWORD")
POSTGRES_DB=os.getenv("LOGGING_DB")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE")

RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")

# Create Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total HTTP Requests Count', 
    ['method', 'endpoint', 'status_code']
)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 
    'HTTP Request Latency', 
    ['method', 'endpoint']
)
LOGS_PROCESSED = Counter(
    'logs_processed_total',
    'Total number of logs processed from RabbitMQ'
)
RABBITMQ_CONNECTION_ERRORS = Counter(
    'rabbitmq_connection_errors_total',
    'Total number of RabbitMQ connection errors'
)


def get_db_connection():
    """Creates a new DB connection."""
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB
    )

# RabbitMQ Consumer

def on_message(ch, method, properties, body):
    """
    Called when a message is received from RabbitMQ. Stores the log in PostgreSQL.
    """
    try:
        data = json.loads(body)
        print("Received log from RabbitMQ:", data)

        # Validate fields
        if not all(k in data for k in ("service_name", "level", "message")):
            print("Missing required fields in log payload.")
            return

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO logs (service_name, level, message, transaction_id)
            VALUES (%s, %s, %s, %s)
            """,
            (
                data["service_name"],
                data["level"],
                data["message"],
                data.get("transaction_id", None)
            )
        )
        conn.commit()
        cur.close()
        conn.close()
        print("Log entry stored in DB.")
        
        # Increment the counter for processed logs
        LOGS_PROCESSED.inc()

    except json.JSONDecodeError:
        print("Error decoding JSON message.")
    except psycopg2.Error as e:
        print("Database error:", e)
    except Exception as e:
        print("Unexpected error:", e)
    finally:
        # Always ACK so it doesn't get stuck in unacked
        ch.basic_ack(delivery_tag=method.delivery_tag)

def run_rabbitmq_consumer():
    """
    Continuously tries to connect to RabbitMQ and consume messages.
    Reconnects if the connection fails.
    """
    while True:
        try:
            print(f"Attempting RabbitMQ connection to host: {RABBITMQ_HOST}")

            # Credentials (guest/guest by default)
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)

            # Create connection parameters
            parameters = pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                credentials=credentials,
                socket_timeout=5,  # Set explicit timeout
                connection_attempts=1  # Only try once per loop iteration
            )

            print(f"connection before")
            connection = None  # Initialize to avoid UnboundLocalError

            try:
                # Establish connection with more explicit error handling
                connection = pika.BlockingConnection(parameters)
                print(f"connection after - SUCCESS")
                
                # Only proceed if we have a valid connection
                if connection and connection.is_open:
                    print("RabbitMQ connection established!")
                    channel = connection.channel()

                    print(f"Declaring queue: {RABBITMQ_QUEUE}")
                    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

                    channel.basic_qos(prefetch_count=1)

                    print(f"Listening for logs on RabbitMQ queue: {RABBITMQ_QUEUE}")
                    channel.basic_consume(
                        queue=RABBITMQ_QUEUE,
                        on_message_callback=on_message,
                        auto_ack=False
                    )

                    channel.start_consuming()
                else:
                    print("Connection created but not open. Retrying in 5 seconds...")
                    if connection:
                        try:
                            connection.close()
                        except:
                            pass
                    time.sleep(5)
                    
            except pika.exceptions.AMQPConnectionError as e:
                print(f"AMQP Connection Error during connection attempt: {e}")
                RABBITMQ_CONNECTION_ERRORS.inc()
                time.sleep(5)
            except pika.exceptions.ConnectionClosedByBroker as e:
                print(f"Connection closed by broker: {e}")
                RABBITMQ_CONNECTION_ERRORS.inc()
                time.sleep(5)
            except pika.exceptions.ConnectionWrongStateError as e:
                print(f"Connection wrong state: {e}")
                RABBITMQ_CONNECTION_ERRORS.inc()
                time.sleep(5)
            except Exception as e:
                print(f"Unexpected error during connection attempt: {type(e).__name__}: {e}")
                RABBITMQ_CONNECTION_ERRORS.inc()
                time.sleep(5)
                
        except Exception as e:
            print(f"Outer exception: {type(e).__name__}: {e}")
            RABBITMQ_CONNECTION_ERRORS.inc()
            time.sleep(5)

# Flask API


app = Flask(__name__)
swagger = Swagger(app)

# Add Prometheus middleware
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    request_latency = time.time() - request.start_time
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.path
    ).observe(request_latency)
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
        status_code=response.status_code
    ).inc()
    
    return response

@app.route('/metrics')
def metrics():
    return generate_latest()

@app.route('/logs/getall', methods=['GET'])
def get_logs():
    """
    Get All Logs
    ---
    tags:
      - Logging
    responses:
      200:
        description: Successfully retrieved logs
      404:
        description: No logs found
    """

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM logs")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        if not rows:
            return jsonify({"message": "No logs found"}), 404

        columns = ["id", "service_name", "level", "message", "transaction_id", "timestamp"]
        data = [dict(zip(columns, row)) for row in rows]
        return jsonify(data)
    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500
    
#Get Logs by Transaction ID and Level
@app.route('/logs/by_transid_level/<transaction_id>/<level>', methods=['GET'])
def get_logs_by_transaction_level(transaction_id, level):
    """
    Get Logs by Transaction ID and Level
    ---
    tags:
      - Logging
    parameters:
      - name: transaction_id
        in: path
        type: string
        required: true
      - name: level
        in: path
        type: string
        required: true
        description: e.g. INFO, WARN, ERROR
    responses:
      200:
        description: Logs returned
      404:
        description: No logs found
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT * FROM logs WHERE transaction_id = %s AND lower(level) = lower(%s)",
            (transaction_id, level)
        )
        logs = cur.fetchall()
        if not logs:
            return jsonify({"message": "No logs found"}), 404
        
        columns = ["id", "service_name", "level", "message", "transaction_id", "timestamp"]
        return jsonify([dict(zip(columns, log)) for log in logs])

    except psycopg2.Error as e:
        return jsonify({"error": "Database error: " + str(e)}), 500
    finally:
        cur.close()
        conn.close()

# Get Logs by Date and Level
@app.route('/logs/by_date_level/<date>/<level>', methods=['GET'])
def get_logs_by_date_level(date, level):
    """
    Get Logs by Date and Level
    ---
    tags:
      - Logging
    parameters:
      - name: date
        in: path
        type: string
        required: true
        description: YYYY-MM-DD
      - name: level
        in: path
        type: string
        required: true
        description: e.g. INFO, ERROR, etc.
    responses:
      200:
        description: Logs returned
      400:
        description: Invalid date format
      404:
        description: No logs found
    """
    try:
        datetime.strptime(date, "%Y-%m-%d")  # Validate Date Format
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM logs WHERE DATE(timestamp) = %s AND lower(level) = lower(%s)",
            (date, level)
        )
        logs = cur.fetchall()
        if not logs:
            return jsonify({"message": "No logs found"}), 404

        columns = ["id", "service_name", "level", "message", "transaction_id", "timestamp"]
        return jsonify([dict(zip(columns, log)) for log in logs])

    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

# Get Logs by Service and Level
@app.route('/logs/by_service_level/<service>/<level>', methods=['GET'])
def get_logs_by_service_level(service, level):
    """
    Get Logs by Service and Level
    ---
    tags:
      - Logging
    parameters:
      - name: service
        in: path
        type: string
        required: true
      - name: level
        in: path
        type: string
        required: true
    responses:
      200:
        description: Logs returned
      404:
        description: No logs found
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT * FROM logs WHERE lower(service_name) = lower(%s) AND lower(level) = lower(%s)",
            (service, level)
        )
        logs = cur.fetchall()
        if not logs:
            return jsonify({"message": "No logs found"}), 404

        columns = ["id", "service_name", "level", "message", "transaction_id", "timestamp"]
        return jsonify([dict(zip(columns, log)) for log in logs])

    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

# Get Logs by Date Range and Level
@app.route('/logs/by_date_range_level/<start_date>/<end_date>/<level>', methods=['GET'])
def get_logs_by_date_range_level(start_date, end_date, level):
    """
    Get Logs by Date Range and Level
    ---
    tags:
      - Logging
    parameters:
      - name: start_date
        in: path
        type: string
        required: true
        description: YYYY-MM-DD
      - name: end_date
        in: path
        type: string
        required: true
        description: YYYY-MM-DD
      - name: level
        in: path
        type: string
        required: true
    responses:
      200:
        description: Logs returned
      400:
        description: Invalid date format
      404:
        description: No logs found
    """
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM logs WHERE DATE(timestamp) BETWEEN %s AND %s AND lower(level) = lower(%s)",
            (start_date, end_date, level)
        )
        logs = cur.fetchall()
        if not logs:
            return jsonify({"message": "No logs found"}), 404

        columns = ["id", "service_name", "level", "message", "transaction_id", "timestamp"]
        return jsonify([dict(zip(columns, log)) for log in logs])

    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

# Get Logs by Service, Level, and Date Range
@app.route('/logs/by_service_level_daterange/<service>/<level>/<start_date>/<end_date>', methods=['GET'])
def get_logs_by_service_level_daterange(service, level, start_date, end_date):
    """
    Get Logs by Service, Level, and Date Range
    ---
    tags:
      - Logging
    parameters:
      - name: service
        in: path
        type: string
        required: true
      - name: level
        in: path
        type: string
        required: true
      - name: start_date
        in: path
        type: string
        required: true
        description: YYYY-MM-DD
      - name: end_date
        in: path
        type: string
        required: true
        description: YYYY-MM-DD
    responses:
      200:
        description: Logs returned
      400:
        description: Invalid date format
      404:
        description: No logs found
    """
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """SELECT * FROM logs WHERE lower(service_name) = lower(%s) 
            AND lower(level) = lower(%s) 
            AND DATE(timestamp) BETWEEN %s AND %s""",
            (service, level, start_date, end_date)
        )
        logs = cur.fetchall()
        if not logs:
            return jsonify({"message": "No logs found"}), 404

        columns = ["id", "service_name", "level", "message", "transaction_id", "timestamp"]
        return jsonify([dict(zip(columns, log)) for log in logs])

    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()


# Start
if __name__ == '__main__':
    print("Starting Logging Service...")

    # Start the RabbitMQ consumer in a background thread
    consumer_thread = threading.Thread(target=run_rabbitmq_consumer, daemon=True)
    consumer_thread.start()

    # Run Flask with debug=False to avoid multiple consumer threads
    app.run(host="0.0.0.0", port=9000, debug=False)
