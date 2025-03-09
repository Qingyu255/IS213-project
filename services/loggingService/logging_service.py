from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask.cli import load_dotenv
import psycopg2
import os
from datetime import datetime

load_dotenv(".env")
DB_HOST = os.getenv("DB_HOST")  # Correct way to access env variables
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


app = Flask(__name__)
# Connectto PostgreSQL and handle any errors
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )
    cur = conn.cursor()
except psycopg2.Error as e:
    print("Error connecting to PostgreSQL:", e)
    exit(1)  # Stop execution if DB connection fails


# Create Logs Table if does not exists
try:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            service_name VARCHAR(100) NOT NULL,
            level VARCHAR(10) CHECK (level IN ('info', 'debug', 'error')),
            message TEXT NOT NULL,
            transaction_id VARCHAR(50) DEFAULT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
except psycopg2.Error as e:
    print("Error creating table:", e)
    exit(1)  # Stop execution if table creation fails


# Store log in database
@app.route('/logs/save', methods=['POST'])
def create_log():
    try:
        data = request.get_json()
        # Validate required fields
        if not all(k in data for k in ("service_name", "level", "message", "transaction_id")):
            return jsonify({"error": "Missing required fields: service_name, level, message or transaction_id"}), 400

        # Insert log entry
        cur = conn.cursor() 
        cur.execute(
                "INSERT INTO logs (service_name, level, message, transaction_id) VALUES (%s, %s, %s, %s)",
                (data["service_name"], data["level"], data["message"], data.get("transaction_id", None)),
            )
        conn.commit()
        return jsonify({"message": "Log entry stored successfully"}), 201
    except psycopg2.Error as e:
            return jsonify({"error": "Database error: " + str(e)}), 500
    except Exception as e:
            return jsonify({"error": "Server error: " + str(e)}), 500


# Retrieve all logs
@app.route('/logs/getall', methods=['GET'])
def get_logs():
    try:
        cur.execute("SELECT * FROM logs")
        logs = cur.fetchall()
        columns = ["id", "service_name", "level", "message", "transaction_id", "timestamp"]
        if not logs:
            return jsonify({"message": "No logs found"}), 404
        return jsonify([dict(zip(columns, log)) for log in logs])
    except psycopg2.Error as e:
        return jsonify({"error": "Database error: " + str(e)}), 500

#Retrieve log by transaction id and level
@app.route('/logs/by_transId_and_level/<transaction_id>/<level>', methods=['GET'])
def get_logs_by_transId_and_level(transaction_id,level):
    try:
        cur.execute("SELECT * FROM logs WHERE transaction_id = %s AND level = %s", (transaction_id,level))
        logs = cur.fetchall()
        columns = ["id", "service_name", "level", "message", "transaction_id", "timestamp"]
        if not logs:
            return jsonify({"message": "No logs found for this transaction ID and level"}), 404
        return jsonify([dict(zip(columns, log)) for log in logs])
    except psycopg2.Error as e:
        return jsonify({"error": "Database error: " + str(e)}), 500

#Retrieve log by service_name and level
@app.route('/logs/by_service_and_level/<service_name>/<level>', methods=['GET'])
def get_logs_by_service_and_level(service_name, level):
    try:
        cur.execute("SELECT * FROM logs WHERE service_name = %s AND level = %s", (service_name, level))
        logs = cur.fetchall()
        columns = ["id", "service_name", "level", "message", "transaction_id", "timestamp"]
        if not logs:
            return jsonify({"message": "No logs found for this service and level"}), 404
        return jsonify([dict(zip(columns, log)) for log in logs])
    except psycopg2.Error as e:
        return jsonify({"error": "Database error: " + str(e)}), 500

#Retrieve log by date and level
@app.route('/logs/by_date_and_level/<date>/<level>', methods=['GET'])
def get_logs_by_date_and_level(date, level):
    try:
        # Validate the date format (YYYY-MM-DD)
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    try:
        print("date:" + date)
        print(f"""
    SELECT id, service_name, level, message, transaction_id, timestamp
    FROM logs 
    WHERE timestamp::date = '{date}' 
    AND level = '{level}'
    """)
        # Query logs based on the extracted date
        cur.execute("""
            SELECT id, service_name, level, message, transaction_id, timestamp 
            FROM logs 
             WHERE timestamp::date = %s  
            AND level = %s
        """, (date, level))

        logs = cur.fetchall()
        columns = ["id", "service_name", "level", "message", "transaction_id", "timestamp"]

        if not logs:
            return jsonify({"message": "No logs found for this date and level"}), 404

        return jsonify([dict(zip(columns, log)) for log in logs])
    except psycopg2.Error as e:
        return jsonify({"error": "Database error: " + str(e)}), 500

@app.route('/logs/by_date_range_and_level/<start_date>/<end_date>/<level>', methods=['GET'])
def get_logs_by_date_range_and_level(start_date, end_date, level):
    try:
        # Validate date format (YYYY-MM-DD)
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    try:
        print(f"""
        SELECT id, service_name, level, message, transaction_id, timestamp 
        FROM logs 
        WHERE timestamp::date BETWEEN '{start_date}' AND '{end_date}' 
        AND level = '{level}'
        """)

        # Query logs based on the date range
        cur.execute("""
            SELECT id, service_name, level, message, transaction_id, timestamp 
            FROM logs 
            WHERE timestamp::date BETWEEN %s AND %s 
            AND level = %s
        """, (start_date, end_date, level))

        logs = cur.fetchall()
        columns = ["id", "service_name", "level", "message", "transaction_id", "timestamp"]

        if not logs:
            return jsonify({"message": "No logs found in this date range and level"}), 404

        return jsonify([dict(zip(columns, log)) for log in logs])

    except psycopg2.Error as e:
        return jsonify({"error": "Database error: " + str(e)}), 500


#retrieve by service_name, daterange, and level.    
@app.route('/logs/by_service_and_level/<service_name>/<level>/datetime', methods=['GET'])
def get_logs_by_service_datetime_and_level(service_name, level):
    start_time = request.args.get("start")
    end_time = request.args.get("end")

    # Validate input parameters
    if not start_time or not end_time:
        return jsonify({"error": "Please provide both start and end timestamps in YYYY-MM-DD HH:MM:SS format"}), 400

    try:
        # Ensure correct timestamp format
        datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({"error": "Invalid timestamp format. Use YYYY-MM-DD HH:MM:SS"}), 400

    try:
        # Execute query to filter by service_name, timestamp range, and level
        cur.execute("""
            SELECT * FROM logs 
            WHERE service_name = %s 
            AND timestamp BETWEEN %s AND %s 
            AND level = %s
        """, (service_name, start_time, end_time, level))

        logs = cur.fetchall()
        columns = ["id", "service_name", "level", "message", "transaction_id", "timestamp"]

        if not logs:
            return jsonify({"message": "No logs found for this service, time range, and level"}), 404

        return jsonify([dict(zip(columns, log)) for log in logs])
    except psycopg2.Error as e:
        return jsonify({"error": "Database error: " + str(e)}), 500

@app.route('/logs/by_service__level__daterange/<service_name>/<level>/<start_date>/<end_date>', methods=['GET'])
def get_logs_by_service_level_date_range(service_name, level, start_date, end_date):
    try:
        # Validate date format (YYYY-MM-DD)
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    try:
        print(f"""
        SELECT id, service_name, level, message, transaction_id, timestamp 
        FROM logs 
        WHERE service_name = '{service_name}'
        AND level = '{level}'
        AND timestamp::date BETWEEN '{start_date}' AND '{end_date}'
        """)

        # Query logs based on service, level, and date range
        cur.execute("""
            SELECT id, service_name, level, message, transaction_id, timestamp 
            FROM logs 
            WHERE service_name = %s 
            AND level = %s 
            AND timestamp::date BETWEEN %s AND %s
        """, (service_name, level, start_date, end_date))

        logs = cur.fetchall()
        columns = ["id", "service_name", "level", "message", "transaction_id", "timestamp"]

        if not logs:
            return jsonify({"message": "No logs found for this service, level, and date range"}), 404

        return jsonify([dict(zip(columns, log)) for log in logs])

    except psycopg2.Error as e:
        return jsonify({"error": "Database error: " + str(e)}), 500

# Run Flask server
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True) 