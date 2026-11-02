from sanic import Sanic, response, Request
from asyncpg import create_pool, Pool
import os
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr, ValidationError
import logging

# Optional: Uncomment if you need CORS
# from sanic_cors import CORS

app = Sanic("EmployeeManagementApp")

# Optional: Enable CORS for all routes
# CORS(app)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    logger.error("DATABASE_URL environment variable not set.")
    raise RuntimeError("DATABASE_URL environment variable not set.")

DB_CONFIG = {
    "dsn": DB_URL,
}

# --- Pydantic Models for Validation ---
class EmployeeModel(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    position: str
    salary: float

# --- Global Exception Handler ---
@app.exception(Exception)
async def handle_exceptions(request: Request, exception: Exception):
    logger.exception("Unhandled exception: %s", exception)
    return response.json({"status": "error", "message": str(exception)}, status=500)

# --- Database Setup ---
@app.listener("before_server_start")
async def setup_db(app: Sanic, loop):
    app.ctx.db_pool: Pool = await create_pool(**DB_CONFIG, loop=loop)
    logger.info("Database pool created.")

@app.listener("after_server_stop")
async def close_db(app: Sanic, loop):
    await app.ctx.db_pool.close()
    logger.info("Database pool closed.")

# --- Routes ---

@app.route("/employees", methods=["POST"])
async def add_employee(request: Request):
    try:
        data = EmployeeModel.parse_obj(request.json)
    except ValidationError as e:
        return response.json({"status": "Invalid input", "errors": e.errors()}, status=400)
    async with app.ctx.db_pool.acquire() as connection:
        try:
            await connection.execute(
                "INSERT INTO employees (first_name, last_name, email, position, salary) VALUES ($1, $2, $3, $4, $5)",
                data.first_name, data.last_name, data.email, data.position, data.salary
            )
        except Exception as db_exc:
            logger.error("Database error: %s", db_exc)
            return response.json({"status": "Database error", "error": str(db_exc)}, status=500)
    return response.json({"status": "Employee added"}, status=201)

@app.route("/employees", methods=["GET"])
async def get_employees(request: Request):
    # Pagination support
    try:
        limit = int(request.args.get("limit", 20))
        offset = int(request.args.get("offset", 0))
        if limit < 1 or offset < 0:
            raise ValueError
    except ValueError:
        return response.json({"status": "Invalid pagination parameters"}, status=400)

    async with app.ctx.db_pool.acquire() as connection:
        rows = await connection.fetch(
            "SELECT * FROM employees ORDER BY id LIMIT $1 OFFSET $2", limit, offset
        )
        employees = [{
            "id": row["id"],
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "email": row["email"],
            "position": row["position"],
            "salary": row["salary"],
            "date_hired": row["date_hired"].isoformat() if row["date_hired"] else None
        } for row in rows]
    return response.json({"employees": employees})

@app.route("/employees/<employee_id>", methods=["GET"])
async def get_employee(request: Request, employee_id: str):
    try:
        employee_id_int = int(employee_id)
    except ValueError:
        return response.json({"status": "Invalid employee ID"}, status=400)

    async with app.ctx.db_pool.acquire() as connection:
        row = await connection.fetchrow("SELECT * FROM employees WHERE id = $1", employee_id_int)

    if row is None:
        return response.json({"status": "Employee not found"}, status=404)

    employee = {
        "id": row["id"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        "email": row["email"],
        "position": row["position"],
        "salary": row["salary"],
        "date_hired": row["date_hired"].isoformat() if row["date_hired"] else None
    }

    return response.json({"employee": employee})

@app.route("/employees/<employee_id>", methods=["PUT"])
async def update_employee(request: Request, employee_id: str):
    try:
        employee_id_int = int(employee_id)
    except ValueError:
        return response.json({"status": "Invalid employee ID"}, status=400)

    try:
        updated_data = EmployeeModel.parse_obj(request.json)
    except ValidationError as e:
        return response.json({"status": "Invalid input", "errors": e.errors()}, status=400)

    async with app.ctx.db_pool.acquire() as connection:
        result = await connection.execute(
            """
            UPDATE employees
            SET first_name = $1,
                last_name = $2,
                email = $3,
                position = $4,
                salary = $5
            WHERE id = $6
            """,
            updated_data.first_name,
            updated_data.last_name,
            updated_data.email,
            updated_data.position,
            float(updated_data.salary),
            employee_id_int
        )

    if result == "UPDATE 0":
        return response.json({"status": "Employee not found"}, status=404)

    return response.json({"status": "Employee updated"})

@app.route("/employees/<employee_id>", methods=["DELETE"])
async def delete_employee(request: Request, employee_id: str):
    try:
        employee_id_int = int(employee_id)
    except ValueError:
        return response.json({"status": "Invalid employee ID"}, status=400)

    async with app.ctx.db_pool.acquire() as connection:
        result = await connection.execute(
            "DELETE FROM employees WHERE id=$1", employee_id_int
        )
    
    if result == "DELETE 0":
        return response.json({"status": "Employee not found"}, status=404)
    
    return response.json({"status": "Employee deleted"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
