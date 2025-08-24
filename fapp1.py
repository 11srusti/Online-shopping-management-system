import streamlit as st
import mysql.connector
from mysql.connector import pooling
from decimal import Decimal

# Database connection pool
def create_connection_pool():
    return mysql.connector.pooling.MySQLConnectionPool(
        pool_name="mypool",
        pool_size=5,
        host="localhost",
        user="root",
        password="HeyVaibhsOracle@2030",  # Your database password
        database="shopping_system"
    )

connection_pool = create_connection_pool()

# Check customer credentials
def check_credentials(email, password):
    connection = connection_pool.get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM customer WHERE email=%s AND password=%s", (email, password))
        customer = cursor.fetchone()
    finally:
        connection.close()
    return customer


# Login function
def login():
    st.sidebar.title("Login")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        customer = check_credentials(email, password)
        if customer:
            st.session_state["customer"] = customer
            st.session_state["customer_id"] = customer['c_id']  # Ensure customer_id is set
            st.success(f"Welcome, {customer['f_name']}!")
        else:
            st.error("Invalid email or password")


# Format data for display
def format_data(data):
    for item in data:
        for key, value in item.items():
            if isinstance(value, Decimal):
                item[key] = float(value)
            elif hasattr(value, 'isoformat'):
                item[key] = value.isoformat()
    return data

# Admin dashboard
def admin_dashboard():
    st.markdown("<h3 style='text-align: center;'>Admin Dashboard</h3>", unsafe_allow_html=True)

    operation = st.selectbox("Select Operation", ["Add", "Update", "Delete", "View"])
    table = st.selectbox("Select Table", ["Customer", "Product", "Order", "Payment", "Cart", "Cart Item"])

    if operation == "Add":
        add_entry(table)
    elif operation == "Update":
        update_entry(table)
    elif operation == "Delete":
        delete_entry(table)
    elif operation == "View":
        view_entries(table)

# Function to add an entry to a table
def add_entry(table):
    st.subheader(f"Add {table}")
    with st.form(key=f'add_{table.lower()}_form'):
        if table == "Customer":
            f_name = st.text_input("First Name")
            l_name = st.text_input("Last Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            ph_no = st.text_input("Phone Number")
            street = st.text_input("Street")
            house_number = st.text_input("House Number")
            city = st.text_input("City")
            state = st.text_input("State")
            pincode = st.text_input("Pincode")
            submit_button = st.form_submit_button("Add Customer")
            if submit_button:
                connection = connection_pool.get_connection()
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO customer (f_name, l_name, email, password, ph_no, street, house_number, city, state, pincode) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (f_name, l_name, email, password, ph_no, street, house_number, city, state, pincode))
                connection.commit()
                connection.close()
                st.success("Customer added successfully!")
        elif table == "Product":
            p_name = st.text_input("Product Name")
            price = st.number_input("Price", min_value=0.0)
            material = st.text_input("Material")
            gst_id = st.text_input("GST ID")
            description = st.text_area("Description")
            stock = st.number_input("Stock", min_value=0)
            submit_button = st.form_submit_button("Add Product")
            if submit_button:
                connection = connection_pool.get_connection()
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO product (p_name, price, material, gst_id, description, stock) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (p_name, price, material, gst_id, description, stock))
                connection.commit()
                connection.close()
                st.success("Product added successfully!")
        # Similar forms can be created for Order, Payment, Cart, and Cart Item tables...

# Function to update an entry in a table
def update_entry(table):
    st.subheader(f"Update {table}")
    id_to_update = st.number_input(f"{table} ID to Update", min_value=1)
    connection = connection_pool.get_connection()
    cursor = connection.cursor(dictionary=True)

    if table == "Customer":
        cursor.execute("SELECT * FROM customer WHERE c_id=%s", (id_to_update,))
        entry = cursor.fetchone()
        if entry:
            with st.form(key=f'update_{table.lower()}_form'):
                f_name = st.text_input("First Name", entry["f_name"])
                l_name = st.text_input("Last Name", entry["l_name"])
                email = st.text_input("Email", entry["email"])
                password = st.text_input("Password", entry["password"])
                ph_no = st.text_input("Phone Number", entry["ph_no"])
                street = st.text_input("Street", entry["street"])
                house_number = st.text_input("House Number", entry["house_number"])
                city = st.text_input("City", entry["city"])
                state = st.text_input("State", entry["state"])
                pincode = st.text_input("Pincode", entry["pincode"])
                submit_button = st.form_submit_button("Update Customer")
                if submit_button:
                    cursor.execute("""
                        UPDATE customer 
                        SET f_name=%s, l_name=%s, email=%s, password=%s, ph_no=%s, street=%s, house_number=%s, city=%s, state=%s, pincode=%s 
                        WHERE c_id=%s
                    """, (f_name, l_name, email, password, ph_no, street, house_number, city, state, pincode, id_to_update))
                    connection.commit()
                    st.success("Customer updated successfully!")
        else:
            st.error("Customer not found")
    
    elif table == "Product":
        cursor.execute("SELECT * FROM product WHERE p_id=%s", (id_to_update,))
        entry = cursor.fetchone()
        if entry:
            with st.form(key=f'update_{table.lower()}_form'):
                p_name = st.text_input("Product Name", entry["p_name"])
                price = st.number_input("Price", min_value=0.0, value=entry["price"])
                material = st.text_input("Material", entry["material"])
                gst_id = st.text_input("GST ID", entry["gst_id"])
                description = st.text_area("Description", entry["description"])
                stock = st.number_input("Stock", min_value=0, value=entry["stock"])
                submit_button = st.form_submit_button("Update Product")
                if submit_button:
                    cursor.execute("""
                        UPDATE product 
                        SET p_name=%s, price=%s, material=%s, gst_id=%s, description=%s, stock=%s 
                        WHERE p_id=%s
                    """, (p_name, price, material, gst_id, description, stock, id_to_update))
                    connection.commit()
                    st.success("Product updated successfully!")
        else:
            st.error("Product not found")

    # Similar forms can be created for Order, Payment, Cart, and Cart Item tables...

    connection.close()

# Function to delete an entry from a table
def delete_entry(table):
    st.subheader(f"Delete {table}")
    id_to_delete = st.number_input(f"{table} ID to Delete", min_value=1)

    # Mapping of table names to their primary key column names
    primary_key_columns = {
        "Customer": "c_id",          # Ensure this column exists in the customer table
        "Product": "p_id",           # Ensure this column exists in the product table
        "Order": "order_id",         # Ensure this column exists in the order table
        "Payment": "payment_id",     # Ensure this column exists in the payment table
        "Cart": "cart_id",           # Ensure this column exists in the cart table
        "Cart Item": "cart_item_id"  # Ensure this column exists in the cart_item table
    }

    primary_key_column = primary_key_columns.get(table)
    if primary_key_column is None:
        st.error("Unknown table selected")
        return

    if st.button("Delete"):
        connection = connection_pool.get_connection()
        cursor = connection.cursor()

        try:
            if table == "Customer":
                # Delete dependent rows in the 'cart_item' table
                cursor.execute("""
                    DELETE FROM cart_item 
                    WHERE cart_id IN (SELECT cart_id FROM cart WHERE c_id=%s)
                """, (id_to_delete,))
                
                # Delete rows in the 'cart' table
                cursor.execute("DELETE FROM cart WHERE c_id=%s", (id_to_delete,))

                # Delete rows in the 'order_item' table
                cursor.execute("""
                    DELETE FROM order_item 
                    WHERE order_id IN (SELECT order_id FROM `order` WHERE c_id=%s)
                """, (id_to_delete,))
                
                # Delete rows in the 'order' table
                cursor.execute("DELETE FROM `order` WHERE c_id=%s", (id_to_delete,))

                # Delete rows in the 'payment' table
                cursor.execute("""
                    DELETE FROM payment 
                    WHERE order_id IN (SELECT order_id FROM `order` WHERE c_id=%s)
                """, (id_to_delete,))

            elif table == "Product":
                # Delete dependent rows in the 'cart_item' table
                cursor.execute("DELETE FROM cart_item WHERE p_id=%s", (id_to_delete,))

                # Delete rows in the 'order_item' table
                cursor.execute("DELETE FROM order_item WHERE p_id=%s", (id_to_delete,))

            # Delete the row in the parent table
            cursor.execute(f"DELETE FROM {table.lower().replace(' ', '_')} WHERE {primary_key_column}=%s", (id_to_delete,))
            connection.commit()
            st.success(f"{table[:-1]} deleted successfully!")
        except mysql.connector.Error as err:
            st.error(f"Error: {err}")
        finally:
            connection.close()


# Function to view entries in a table
def view_entries(table):
    st.subheader(f"View All {table}")

    # Map table names to actual table names in the database, if necessary
    table_name_map = {
        "Customer": "customer",
        "Product": "product",
        "Order": "order",
        "Payment": "payment",
        "Cart": "cart",
        "Cart Item": "cart_item"
    }

    # Get the correct table name
    table_name = table_name_map.get(table, table.lower())

    # Enclose the table name in backticks to handle reserved keywords
    query = f"SELECT * FROM `{table_name}`"

    connection = connection_pool.get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(query)
        results = cursor.fetchall()

        # Display results in a table format
        if results:
            st.write(f"Showing data from the `{table_name}` table")
            st.dataframe(results)  # Display results in a dataframe
        else:
            st.write("No data available.")

    except mysql.connector.Error as err:
        st.error(f"Error: {err}")

    finally:
        connection.close()



# Customer dashboard
def customer_dashboard():
    st.markdown("<h3 style='text-align: center;'>Customer Dashboard</h3>", unsafe_allow_html=True)
    
    connection = connection_pool.get_connection()
    cursor = connection.cursor(dictionary=True)

    # Display available products
    cursor.execute("SELECT * FROM product")
    products = cursor.fetchall()
    products = format_data(products)

    st.subheader("Available Products")

    # Debugging info: Print the first product's keys
    if products:
        st.write("Debug info: product dictionary keys:", products[0].keys())

    for product in products:
        st.write(f"Product ID: {product.get('p_id', 'N/A')}, Product Name: {product.get('p_name', 'N/A')}, Price: {product.get('price', 'N/A')}")
        if st.button(f"Add to Cart: {product.get('p_name', 'N/A')}", key=f"add_to_cart_{product['p_id']}"):
            add_to_cart(product['p_id'])

    # View cart and proceed to checkout
    if st.button("View Cart"):
        view_cart()

    connection.close()


def add_to_cart(p_id):
    connection = connection_pool.get_connection()
    cursor = connection.cursor(dictionary=True)
    customer_id = st.session_state.get('customer_id')

    cursor.execute("SELECT * FROM cart WHERE c_id=%s AND checked_out=False", (customer_id,))
    cart = cursor.fetchone()

    if cart:
        cart_id = cart['cart_id']
    else:
        cursor.execute("INSERT INTO cart (c_id, checked_out) VALUES (%s, False)", (customer_id,))
        connection.commit()
        cart_id = cursor.lastrowid

    cursor.execute("SELECT * FROM cart_item WHERE cart_id=%s AND p_id=%s", (cart_id, p_id))
    cart_item = cursor.fetchone()

    if cart_item:
        new_quantity = cart_item['quantity'] + 1
        cursor.execute("UPDATE cart_item SET quantity=%s WHERE cart_item_id=%s", (new_quantity, cart_item['cart_item_id']))
    else:
        cursor.execute("INSERT INTO cart_item (cart_id, p_id, quantity) VALUES (%s, %s, 1)", (cart_id, p_id))

    connection.commit()
    connection.close()
    st.success("Item added to cart!")

def remove_from_cart(p_id):
    connection = connection_pool.get_connection()
    cursor = connection.cursor(dictionary=True)
    customer_id = st.session_state.get('customer_id')

    cursor.execute("SELECT * FROM cart WHERE c_id=%s AND checked_out=False", (customer_id,))
    cart = cursor.fetchone()
    if cart:
        cart_id = cart['cart_id']
        cursor.execute("DELETE FROM cart_item WHERE cart_id=%s AND p_id=%s", (cart_id, p_id))
        connection.commit()

    connection.close()
    st.success("Item removed from cart!")

def update_quantity(p_id, quantity):
    connection = connection_pool.get_connection()
    cursor = connection.cursor(dictionary=True)
    customer_id = st.session_state.get('customer_id')

    cursor.execute("SELECT * FROM cart WHERE c_id=%s AND checked_out=False", (customer_id,))
    cart = cursor.fetchone()
    if cart:
        cart_id = cart['cart_id']
        if quantity > 0:
            cursor.execute("UPDATE cart_item SET quantity=%s WHERE cart_id=%s AND p_id=%s", (quantity, cart_id, p_id))
        else:
            cursor.execute("DELETE FROM cart_item WHERE cart_id=%s AND p_id=%s", (cart_id, p_id))
        connection.commit()

    connection.close()
    st.success("Cart updated!")

def view_cart():
    connection = connection_pool.get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        customer_id = st.session_state.get('customer_id')

        cursor.execute("SELECT * FROM cart WHERE c_id=%s AND checked_out=False", (customer_id,))
        cart = cursor.fetchone()

        if not cart:
            st.warning("Your cart is empty.")
            return

        cart_id = cart['cart_id']
        cursor.execute("SELECT p.p_id, p.p_name, p.price, ci.quantity FROM product p JOIN cart_item ci ON p.p_id = ci.p_id WHERE ci.cart_id=%s", (cart_id,))
        items = cursor.fetchall()

        st.subheader("Your Cart")
        total_price = 0
        for item in items:
            st.write(f"Product ID: {item['p_id']}, Product Name: {item['p_name']}, Price: {item['price']}, Quantity: {item['quantity']}")
            total_price += item['price'] * item['quantity']
            if st.button(f"Remove: {item['p_name']}", key=f"remove_{item['p_id']}"):
                remove_from_cart(item['p_id'])
            if st.button(f"Increase Quantity: {item['p_name']}", key=f"increase_{item['p_id']}"):
                update_quantity(item['p_id'], item['quantity'] + 1)
            if st.button(f"Decrease Quantity: {item['p_name']}", key=f"decrease_{item['p_id']}"):
                update_quantity(item['p_id'], item['quantity'] - 1)

        st.write(f"Total Price: {total_price}")

        if st.button("Checkout"):
            checkout()
    finally:
        connection.close()

    



def checkout():
    connection = connection_pool.get_connection()
    cursor = connection.cursor(dictionary=True)
    customer_id = st.session_state.get('customer_id')

    cursor.execute("SELECT * FROM cart WHERE c_id=%s AND checked_out=False", (customer_id,))
    cart = cursor.fetchone()
    if cart:
        cart_id = cart['cart_id']
        cursor.execute("UPDATE cart SET checked_out=True WHERE cart_id=%s", (cart_id,))
        connection.commit()

    connection.close()
    st.success("Checkout successful!")

def place_order(payment_method, card_number, card_expiry, card_cvv, upi_id):
    connection = connection_pool.get_connection()
    cursor = connection.cursor()
    customer_id = st.session_state["customer"]["c_id"]

    cursor.execute("SELECT * FROM cart WHERE c_id=%s AND checked_out=False", (customer_id,))
    cart = cursor.fetchone()
    if not cart:
        st.error("No items in the cart")
        return

    cursor.execute("INSERT INTO `order` (c_id, total_price) VALUES (%s, %s)", (customer_id, 0))
    connection.commit()
    cursor.execute("SELECT LAST_INSERT_ID()")
    order_id = cursor.fetchone()["LAST_INSERT_ID()"]

    cursor.execute("""
        SELECT product.p_id, product.price, cart_item.quantity 
        FROM cart_item 
        JOIN product ON cart_item.p_id = product.p_id 
        WHERE cart_item.cart_id=%s
    """, (cart["cart_id"],))
    cart_items = cursor.fetchall()

    total_price = 0
    for item in cart_items:
        total_price += item["price"] * item["quantity"]
        cursor.execute("INSERT INTO order_item (order_id, p_id, quantity) VALUES (%s, %s, %s)", (order_id, item["p_id"], item["quantity"]))
        cursor.execute("UPDATE product SET stock = stock - %s WHERE p_id=%s", (item["quantity"], item["p_id"]))

    cursor.execute("UPDATE `order` SET total_price=%s WHERE order_id=%s", (total_price, order_id))

    if payment_method == "Cash on Delivery":
        cursor.execute("INSERT INTO payment (order_id, payment_method) VALUES (%s, %s)", (order_id, payment_method))
    elif payment_method == "Card":
        cursor.execute("INSERT INTO payment (order_id, payment_method, card_number, card_expiry, card_cvv) VALUES (%s, %s, %s, %s, %s)", (order_id, payment_method, card_number, card_expiry, card_cvv))
    elif payment_method == "UPI":
        cursor.execute("INSERT INTO payment (order_id, payment_method, upi_id) VALUES (%s, %s, %s)", (order_id, payment_method, upi_id))

    cursor.execute("UPDATE cart SET checked_out=True WHERE cart_id=%s", (cart["cart_id"],))

    connection.commit()
    connection.close()
    st.success("Order placed successfully!")

# Main app
def main():
    st.title("Shopping System Management")

    if "customer" not in st.session_state:
        login()
    else:
        user_role = st.sidebar.selectbox("Role", ["Admin", "Customer"])
        if user_role == "Admin":
            admin_dashboard()
        elif user_role == "Customer":
            customer_dashboard()

if __name__ == "__main__":
    main()
