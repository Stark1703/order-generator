import azure.functions as func
import pyodbc
import random
import os
import logging
from datetime import datetime

app = func.FunctionApp()


@app.timer_trigger(
    schedule="0 * * * * *",
    arg_name="mytimer",
    run_on_startup=False,
    use_monitor=True
)
def GenerateOrders(mytimer: func.TimerRequest) -> None:

    server = os.environ["SQL_SERVER"]
    database = os.environ["SQL_DATABASE"]
    username = os.environ["SQL_USERNAME"]
    password = os.environ["SQL_PASSWORD"]

    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={server},1433;"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
    )

    products = [
        ("Laptop", 1200),
        ("Keyboard", 75),
        ("Monitor", 350),
        ("Mouse", 25),
        ("Mechanical Keyboard", 95),
        ("Headphones", 120)
    ]

    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT ISNULL(MAX(order_id), 1000) FROM Orders"
    )

    order_id = cursor.fetchone()[0] + 1

    for _ in range(12):

        customer_id = random.randint(1, 4)
        product, price = random.choice(products)
        quantity = random.randint(1, 3)
        amount = price * quantity

        status = random.choice([
            "Completed",
            "Pending"
        ])

        now = datetime.now()

        cursor.execute(
            """
            INSERT INTO Orders
            (
                order_id,
                customer_id,
                product,
                quantity,
                amount,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            order_id,
            customer_id,
            product,
            quantity,
            amount,
            status,
            now,
            now
        )

        order_id += 1

    conn.commit()

    cursor.close()
    conn.close()

    logging.info("Generated 12 new orders.")