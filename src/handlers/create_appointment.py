"""Create an appointment for an existing customer and vehicle."""

from common.db import connect_db
from common.http import (
    response,
    read_json_body,
    is_valid_date,
    is_valid_time,
    is_valid_uuid,
    database_error_response,
)


def lambda_handler(event, context):
    path_parameters = event.get("pathParameters") or {}
    customer_id = path_parameters.get("customerId")

    if not is_valid_uuid(customer_id):
        return response(400, {"message": "A valid customerId is required in the URL."})

    try:
        body = read_json_body(event)
    except ValueError as exc:
        return response(400, {"message": str(exc)})

    appointment_date = body.get("date")
    appointment_time = body.get("time")
    vehicle_id = body.get("vehicle_id")
    comments = body.get("comments")

    if not appointment_date or not appointment_time or not vehicle_id:
        return response(400, {
            "message": "Fields 'date', 'time', and 'vehicle_id' are required."
        })
    if not is_valid_date(appointment_date):
        return response(400, {"message": "Date must use YYYY-MM-DD format."})
    if not is_valid_time(appointment_time):
        return response(400, {"message": "Time must use HH:MM or HH:MM:SS format."})
    if not is_valid_uuid(vehicle_id):
        return response(400, {"message": "Field 'vehicle_id' must be a valid UUID."})

    connection = None
    try:
        connection = connect_db()
        cursor = connection.cursor()

        cursor.execute("SELECT id FROM customers WHERE id = %s::uuid", (customer_id,))
        if not cursor.fetchone():
            cursor.close()
            return response(404, {"message": "Customer was not found."})

        cursor.execute("SELECT id FROM vehicles WHERE id = %s::uuid", (vehicle_id,))
        if not cursor.fetchone():
            cursor.close()
            return response(404, {"message": "Vehicle was not found."})

        cursor.execute(
            """SELECT id FROM appointments
               WHERE appointment_date = %s
                 AND appointment_time = %s
                 AND status = 'HABILITADA'""",
            (appointment_date, appointment_time),
        )
        if cursor.fetchone():
            cursor.close()
            return response(409, {
                "message": "The selected date and time are already reserved."
            })

        cursor.execute(
            """INSERT INTO appointments
                   (customer_id, vehicle_id, appointment_date, appointment_time, comments)
               VALUES (%s::uuid, %s::uuid, %s, %s, %s)
               RETURNING id::text AS id,
                         customer_id::text AS customer_id,
                         vehicle_id::text AS vehicle_id,
                         appointment_date,
                         appointment_time,
                         created_at,
                         updated_at,
                         comments,
                         status""",
            (customer_id, vehicle_id, appointment_date, appointment_time, comments),
        )
        column_names = [column[0] for column in cursor.description]
        appointment = dict(zip(column_names, cursor.fetchone()))
        connection.commit()
        cursor.close()
        return response(201, {
            "message": "Appointment created successfully.",
            "data": appointment,
        })
    except Exception as exc:
        if connection:
            connection.rollback()
        return database_error_response(exc)
    finally:
        if connection:
            connection.close()
