"""List appointments for a specific date."""

from common.db import connect_db
from common.http import response, is_valid_date


def lambda_handler(event, context):
    query = event.get("queryStringParameters") or {}
    appointment_date = query.get("date")
    status = query.get("status")

    if not appointment_date:
        return response(400, {"message": "Query parameter 'date' is required."})
    if not is_valid_date(appointment_date):
        return response(400, {"message": "Date must use YYYY-MM-DD format."})
    if status and status not in ("HABILITADA", "DESHABILITADA"):
        return response(400, {
            "message": "Status must be HABILITADA or DESHABILITADA."
        })

    connection = None
    try:
        connection = connect_db()
        cursor = connection.cursor()
        sql = """
            SELECT
                a.id::text AS id,
                a.customer_id::text AS customer_id,
                c.name AS customer_name,
                a.vehicle_id::text AS vehicle_id,
                v.plates AS vehicle_plates,
                v.model AS vehicle_model,
                a.appointment_date,
                a.appointment_time,
                a.created_at,
                a.updated_at,
                a.comments,
                a.status
            FROM appointments a
            INNER JOIN customers c ON c.id = a.customer_id
            INNER JOIN vehicles v ON v.id = a.vehicle_id
            WHERE a.appointment_date = %s
        """
        parameters = [appointment_date]
        if status:
            sql += " AND a.status = %s"
            parameters.append(status)
        sql += " ORDER BY a.appointment_time ASC"

        cursor.execute(sql, tuple(parameters))
        column_names = [column[0] for column in cursor.description]
        appointments = [dict(zip(column_names, row)) for row in cursor.fetchall()]
        cursor.close()
        return response(200, {
            "date": appointment_date,
            "count": len(appointments),
            "data": appointments,
        })
    except Exception as exc:
        return response(500, {"message": "Unable to retrieve appointments."})
    finally:
        if connection:
            connection.close()
