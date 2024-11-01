from sanic import Sanic, response
from asyncpg import create_pool
import os
from dotenv import load_dotenv

app = Sanic("EmployeeManagementApp")

# Load environment variables
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

# Database configuration
DB_CONFIG = {
    "dsn": DB_URL,
}

# Initialize database connection pool
@app.listener("before_server_start")
async def setup_db(app, loop):
    app.ctx.db_pool = await create_pool(**DB_CONFIG, loop=loop)

@app.listener("after_server_stop")
async def close_db(app, loop):
    await app.ctx.db_pool.close()

# Function to add an employee
@app.route("/employees", methods=["POST"])
async def add_employee(request):
    data = request.json
    async with app.ctx.db_pool.acquire() as connection:
        await connection.execute(
            "INSERT INTO employees (first_name, last_name, email, position, salary) VALUES ($1, $2, $3, $4, $5)",
            data["first_name"], data["last_name"], data["email"], data["position"], data["salary"]
        )
    return response.json({"status": "Employee added"}, status=201)

# Function to get all employees
@app.route("/employees", methods=["GET"])
async def get_employees(request):
    async with app.ctx.db_pool.acquire() as connection:
        rows = await connection.fetch("SELECT * FROM employees")
        employees = [{"id": row["id"], "first_name": row["first_name"], "last_name": row["last_name"], 
                      "email": row["email"], "position": row["position"], "salary": row["salary"],
                      "date_hired": row["date_hired"].isoformat()} for row in rows]
    return response.json({"employees": employees})

# Function to get a specific employee
@app.route("/employees/<employee_id>", methods=["GET"])
async def get_employee(request, employee_id):
    try:
        employee_id = int(employee_id)
    except ValueError:
        return response.json({"status": "Invalid employee ID"}, status=400)

    async with app.ctx.db_pool.acquire() as connection:
        row = await connection.fetchrow("SELECT * FROM employees WHERE id = $1", employee_id)

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

# Function to update an employee
@app.route("/employees/<employee_id>", methods=["PUT"])
async def update_employee(request, employee_id):
    try:
        employee_id = int(employee_id)
    except ValueError:
        return response.json({"status": "Invalid employee ID"}, status=400)

    updated_data = request.json
    required_fields = ["first_name", "last_name", "email", "position", "salary"]
    for field in required_fields:
        if field not in updated_data:
            return response.json({"status": f"Missing field: {field}"}, status=400)

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
            updated_data["first_name"],
            updated_data["last_name"],
            updated_data["email"],
            updated_data["position"],
            float(updated_data["salary"]),
            employee_id
        )

    if result == "UPDATE 0":
        return response.json({"status": "Employee not found"}, status=404)

    return response.json({"status": "Employee updated"})

# Function to delete an employee
@app.route("/employees/<employee_id>", methods=["DELETE"])
async def delete_employee(request, employee_id):
    try:
        employee_id = int(employee_id)
    except ValueError:
        return response.json({"status": "Invalid employee ID"}, status=400)

    async with app.ctx.db_pool.acquire() as connection:
        result = await connection.execute(
            "DELETE FROM employees WHERE id=$1", employee_id
        )
    
    if result == "DELETE 0":
        return response.json({"status": "Employee not found"}, status=404)
    
    return response.json({"status": "Employee deleted"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
