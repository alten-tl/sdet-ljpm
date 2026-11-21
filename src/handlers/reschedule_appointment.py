"""Update the date and time of an existing enabled appointment."""

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
    appointment_id = path_parameters.get("appointmentId")
    if not is_valid_uuid(appointment_id):
        return response(400, {"message": "A valid appointmentId is required in the URL."})

    try:
        body = read_json_body(event)
    except ValueError as exc:
        return response(400, {"message": str(exc)})

    appointment_date = body.get("date")
    appointment_time = body.get("time")
    if not appointment_date or not appointment_time:
        return response(400, {"message": "Fields 'date' and 'time' are required."})
    if not is_valid_date(appointment_date):
        return response(400, {"message": "Date must use YYYY-MM-DD format."})
    if not is_valid_time(appointment_time):
        return response(400, {"message": "Time must use HH:MM or HH:MM:SS format."})

    connection = None
    try:
        connection = connect_db()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT status FROM appointments WHERE id = %s::uuid",
            (appointment_id,),
        )
        current_appointment = cursor.fetchone()
        if not current_appointment:
            cursor.close()
            return response(404, {"message": "Appointment was not found."})
        if current_appointment[0] != "HABILITADA":
            cursor.close()
            return response(409, {"message": "A disabled appointment cannot be rescheduled."})

        cursor.execute(
            """SELECT id FROM appointments
               WHERE appointment_date = %s
                 AND appointment_time = %s
                 AND status = 'HABILITADA'
                 AND id <> %s::uuid""",
            (appointment_date, appointment_time, appointment_id),
        )
        if cursor.fetchone():
            cursor.close()
            return response(409, {
                "message": "The selected date and time are already reserved."
            })

        cursor.execute(
            """UPDATE appointments
               SET appointment_date = %s,
                   appointment_time = %s,
                   updated_at = NOW()
               WHERE id = %s::uuid
               RETURNING id::text AS id,
                         customer_id::text AS customer_id,
                         vehicle_id::text AS vehicle_id,
                         appointment_date,
                         appointment_time,
                         created_at,
                         updated_at,
                         comments,
                         status""",
            (appointment_date, appointment_time, appointment_id),
        )
        column_names = [column[0] for column in cursor.description]
        appointment = dict(zip(column_names, cursor.fetchone()))
        connection.commit()
        cursor.close()
        return response(200, {
            "message": "Appointment rescheduled successfully.",
            "data": appointment,
        })
    except Exception as exc:
        if connection:
            connection.rollback()
        return database_error_response(exc)
    finally:
        if connection:
            connection.close()
