-- Database schema for the Cloud AWS appointments technical test.

CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    timezone VARCHAR(80) NOT NULL,
    address TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vehicles (
    id UUID PRIMARY KEY,
    vin VARCHAR(17) NOT NULL UNIQUE,
    plates VARCHAR(20) NOT NULL UNIQUE,
    color VARCHAR(50) NOT NULL,
    year INTEGER NOT NULL CHECK (year BETWEEN 1886 AND 2100),
    model VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE RESTRICT,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    comments TEXT,
    status VARCHAR(15) NOT NULL DEFAULT 'HABILITADA'
        CHECK (status IN ('HABILITADA', 'DESHABILITADA'))
);

-- Only enabled appointments reserve a date/time slot.
CREATE UNIQUE INDEX IF NOT EXISTS uq_appointments_active_slot
    ON appointments (appointment_date, appointment_time)
    WHERE status = 'HABILITADA';

CREATE INDEX IF NOT EXISTS ix_appointments_customer_id
    ON appointments (customer_id);

CREATE INDEX IF NOT EXISTS ix_appointments_vehicle_id
    ON appointments (vehicle_id);

CREATE INDEX IF NOT EXISTS ix_appointments_date
    ON appointments (appointment_date);

-- Demo records used to execute the API without adding customer/vehicle endpoints.
INSERT INTO customers (id, name, timezone, address)
VALUES (
    '11111111-1111-1111-1111-111111111111',
    'Alex Morgan',
    'America/Mexico_City',
    'Av. Reforma 100, Puebla, Puebla, Mexico'
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO vehicles (id, vin, plates, color, year, model)
VALUES (
    '22222222-2222-2222-2222-222222222222',
    '1HGCM82633A004352',
    'ABC-123-A',
    'White',
    2022,
    'Honda Accord'
)
ON CONFLICT (id) DO NOTHING;
