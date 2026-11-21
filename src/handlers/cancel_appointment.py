"""Disable an appointment without deleting its history."""

from common.db import connect_db
from common.http import response, is_valid_uuid, database_error_response


def lambda_handler(event, context):
    path_parameters = event.get("pathParameters") or {}
    appointment_id = path_parameters.get("appointmentId")
    if not is_valid_uuid(appointment_id):
        return response(400, {"message": "A valid appointmentId is required in the URL."})

    connection = None
    try:
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute(
            """UPDATE appointments
               SET status = 'DESHABILITADA', updated_at = NOW()
               WHERE id = %s::uuid AND status = 'HABILITADA'
               RETURNING id::text AS id,
                         customer_id::text AS customer_id,
                         vehicle_id::text AS vehicle_id,
                         appointment_date,
                         appointment_time,
                         created_at,
                         updated_at,
                         comments,
                         status""",
            (appointment_id,),
        )
        row = cursor.fetchone()
        if not row:
            cursor.execute(
                "SELECT status FROM appointments WHERE id = %s::uuid",
                (appointment_id,),
            )
            existing = cursor.fetchone()
            cursor.close()
            if not existing:
                return response(404, {"message": "Appointment was not found."})
            return response(409, {"message": "Appointment is already disabled."})

        column_names = [column[0] for column in cursor.description]
        appointment = dict(zip(column_names, row))
        connection.commit()
        cursor.close()
        return response(200, {
            "message": "Appointment cancelled successfully.",
            "data": appointment,
        })
    except Exception as exc:
        if connection:
            connection.rollback()
        return database_error_response(exc)
    finally:
        if connection:
            connection.close()
