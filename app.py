
from database import conn, cursor
from flask import Flask, render_template, request, redirect
from datetime import date

app = Flask(__name__)


from database import conn

@app.route("/testdb")
def testdb():
    try:
        conn.ping(reconnect=True)
        return "✅ Database Connected Successfully!"
    except Exception as e:
        return f"❌ Database Connection Failed: {e}"



@app.route("/")
def home():
    return render_template("index.html")



@app.route("/about")
def about():
    return render_template("about.html")



@app.route("/contact")
def contact():
    return render_template("contact.html")



@app.route("/menu")
def menu():

    cursor.execute("SELECT * FROM food")
    foods = cursor.fetchall()

    return render_template("menu.html", foods=foods)


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM admin WHERE username=%s AND password=%s",
            (username, password)
        )

        admin = cursor.fetchone()

        if admin:
            return redirect("/dashboard")
        else:
            return "Invalid Username or Password"

    return render_template("loging.html")



@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")



@app.route("/addfood", methods=["GET", "POST"])
def addfood():

    if request.method == "POST":

        food_name = request.form["food_name"]
        category = request.form["category"]
        price = request.form["price"]
        quantity = request.form["quantity"]
        description = request.form["description"]

        sql = """
        INSERT INTO food (food_name, category, price, quantity, description)
        VALUES (%s, %s, %s, %s, %s)
        """

        values = (food_name, category, price, quantity, description)

        cursor.execute(sql, values)
        conn.commit()

        return redirect("/viewfood")

    return render_template("addfood.html")




@app.route("/viewfood")
def viewfood():

    cursor.execute("SELECT * FROM food")
    foods = cursor.fetchall()

    return render_template("viewfood.html", foods=foods)



@app.route("/report")
def report():

    conn.ping(reconnect=True)

    # Total Orders
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]

    # Total Sales
    cursor.execute("SELECT IFNULL(SUM(total),0) FROM orders")
    total_sales = cursor.fetchone()[0]

    # Total Customers
    cursor.execute("SELECT COUNT(DISTINCT customer_name) FROM orders")
    total_customers = cursor.fetchone()[0]

    # Most Popular Food
    cursor.execute("""
        SELECT food_name, COUNT(*) AS total
        FROM orders
        GROUP BY food_name
        ORDER BY total DESC
        LIMIT 1
    """)

    food = cursor.fetchone()

    if food:
        popular_food = food[0]
    else:
        popular_food = "No Orders"

    # Daily Report
    cursor.execute("""
        SELECT
            DATE(order_date) AS day,
            COUNT(*) AS orders,
            SUM(total) AS income,
            (
                SELECT food_name
                FROM orders o2
                WHERE DATE(o2.order_date)=DATE(o1.order_date)
                GROUP BY food_name
                ORDER BY COUNT(*) DESC
                LIMIT 1
            ) AS top_food
        FROM orders o1
        GROUP BY DATE(order_date)
        ORDER BY DATE(order_date) DESC
    """)

    reports = cursor.fetchall()

    return render_template(
        "report.html",
        total_orders=total_orders,
        total_sales=total_sales,
        total_customers=total_customers,
        popular_food=popular_food,
        reports=reports
    )


@app.route("/bill")
def bill():
    return render_template("bill.html")

@app.route("/vieworder/<int:id>")
def view_order(id):

    cursor.execute("SELECT * FROM orders WHERE id=%s", (id,))
    order = cursor.fetchone()

    return render_template("vieworder.html", order=order)



@app.route("/updateorder/<int:id>", methods=["GET","POST"])
def update_order(id):

    if request.method == "POST":

        status = request.form["status"]

        cursor.execute(
            "UPDATE orders SET status=%s WHERE id=%s",
            (status, id)
        )
        conn.commit()

        return redirect("/allorder")

    cursor.execute("SELECT * FROM orders WHERE id=%s", (id,))
    order = cursor.fetchone()

    return render_template("updateorder.html", order=order)



@app.route("/deleteorder/<int:id>")
def delete_order(id):

    cursor.execute("DELETE FROM orders WHERE id=%s", (id,))
    conn.commit()

    return redirect("/allorder")

@app.route("/allorder")
def allorder():

    conn.ping(reconnect=True)

    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()

    return render_template("allorder.html", orders=orders)

@app.route("/order", methods=["GET", "POST"])
def order():

    food = request.args.get("food", "")

    if request.method == "POST":

        customer_name = request.form["customer_name"]
        student_id = request.form["student_id"]
        phone = request.form["phone"]
        food_name = request.form["food_name"]
        quantity = request.form["quantity"]
        total = request.form["total"]
        instructions = request.form["instructions"]
        

        sql = """
        INSERT INTO orders
        (customer_name, student_id, phone, food_name, quantity, total, instructions, status, order_date)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        today = date.today()

        values = (
            customer_name,
            student_id,
            phone,
            food_name,
            quantity,
            total,
            instructions,
            "Pending",
            today
            )

        cursor.execute(sql, values)
        conn.commit()

        return redirect("/allorder")

    return render_template("order.html", selected_food=food)


@app.route("/deletefood/<int:id>")
def deletefood(id):

    cursor.execute("DELETE FROM food WHERE id=%s", (id,))
    conn.commit()

    return redirect("/viewfood")

if __name__ == "__main__":
    app.run(debug=True)
    