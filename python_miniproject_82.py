import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector

class BudgetTrackerSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Budget Tracker System")
        self.root.geometry("600x500")
        self.root.configure(bg="#d1e7dd")  # Light green theme

        self.current_page = None
        self.username = ""
        self.user_pin = ""
        self.balance = 0
        self.user_id = None

        self.db_connect()
        self.show_login_page()

    def db_connect(self):
        """Connect to MySQL and create necessary tables if not exists."""
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root"  # Change this to your MySQL password
        )
        self.cursor = self.conn.cursor()

        self.cursor.execute("CREATE DATABASE IF NOT EXISTS budget_tracker")
        self.conn.database = "budget_tracker"

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                pin VARCHAR(10),
                balance FLOAT DEFAULT 0
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                type VARCHAR(50),
                amount FLOAT,
                balance_after FLOAT,
                description TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cart (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                item_name VARCHAR(255),
                price FLOAT,
                quantity INT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        self.conn.commit()

    def show_login_page(self):
        """Page 1 - Login User"""
        self.clear_current_page()
        self.current_page = tk.Frame(self.root, bg="#d1e7dd")
        self.current_page.pack(fill="both", expand=True)

        tk.Label(self.current_page, text="Enter Your PIN", font=("Arial", 18, "bold"), bg="#d1e7dd").pack(pady=20)
        self.pin_entry = tk.Entry(self.current_page, width=30, font=("Arial", 14), show="*")
        self.pin_entry.pack(pady=5)

        tk.Button(self.current_page, text="Login", font=("Arial", 14, "bold"), bg="#007bff", fg="white", command=self.login_user).pack(pady=10)
        tk.Button(self.current_page, text="New User", font=("Arial", 14, "bold"), bg="#28a745", fg="white", command=self.show_register_page).pack(pady=10)

    def login_user(self):
        pin = self.pin_entry.get().strip()
        if not pin:
            messagebox.showwarning("Input Error", "Please enter your PIN.")
            return

        self.cursor.execute("SELECT id, name, balance FROM users WHERE pin = %s", (pin,))
        user = self.cursor.fetchone()

        if user:
            self.user_id, self.username, self.balance = user
            self.user_pin = pin
            self.show_welcome_page()
        else:
            messagebox.showerror("Login Failed", "Invalid PIN. Try again.")

    def show_register_page(self):
        """Page 2 - New User Registration"""
        self.clear_current_page()
        self.current_page = tk.Frame(self.root, bg="#d1e7dd")
        self.current_page.pack(fill="both", expand=True)

        tk.Label(self.current_page, text="Enter Name", font=("Arial", 14), bg="#d1e7dd").pack(pady=5)
        self.name_entry = tk.Entry(self.current_page, width=30)
        self.name_entry.pack(pady=5)

        tk.Label(self.current_page, text="Enter PIN", font=("Arial", 14), bg="#d1e7dd").pack(pady=5)
        self.new_pin_entry = tk.Entry(self.current_page, width=30, show="*")
        self.new_pin_entry.pack(pady=5)

        tk.Label(self.current_page, text="Initial Balance", font=("Arial", 14), bg="#d1e7dd").pack(pady=5)
        self.balance_entry = tk.Entry(self.current_page, width=30)
        self.balance_entry.pack(pady=5)

        tk.Button(self.current_page, text="Register", font=("Arial", 14, "bold"), bg="#007bff", fg="white", command=self.register_user).pack(pady=10)
        tk.Button(self.current_page, text="Back to Login", font=("Arial", 14, "bold"), bg="#dc3545", fg="white", command=self.show_login_page).pack(pady=5)

    def register_user(self):
        name = self.name_entry.get().strip()
        pin = self.new_pin_entry.get().strip()
        balance = self.balance_entry.get().strip()

        if not name or not pin or not balance.isdigit():
            messagebox.showwarning("Input Error", "Please enter valid details.")
            return

        balance = float(balance)
        self.cursor.execute("INSERT INTO users (name, pin, balance) VALUES (%s, %s, %s)", (name, pin, balance))
        self.conn.commit()
        messagebox.showinfo("Success", "User Registered Successfully!")
        self.show_login_page()

    def show_welcome_page(self):
        """Page 3 - User Dashboard"""
        self.clear_current_page()
        self.current_page = tk.Frame(self.root, bg="#d1e7dd")
        self.current_page.pack(fill="both", expand=True)

        tk.Label(self.current_page, text=f"Welcome {self.username}!", font=("Arial", 18, "bold"), bg="#d1e7dd").pack(pady=10)
        tk.Label(self.current_page, text=f"Current Balance: Rs.{self.balance:.2f}", font=("Arial", 14), bg="#d1e7dd").pack(pady=10)

        tk.Button(self.current_page, text="Add Item to Cart", font=("Arial", 14), bg="#007bff", fg="white", command=self.show_cart_page).pack(pady=10)
        tk.Button(self.current_page, text="View Cart", font=("Arial", 14), bg="#ffc107", fg="black", command=self.show_cart_page).pack(pady=10)
        tk.Button(self.current_page, text="Logout", font=("Arial", 14), bg="#dc3545", fg="white", command=self.show_login_page).pack(pady=5)

    def show_cart_page(self):
        """Page 4 - Cart Page"""
        self.clear_current_page()
        self.current_page = tk.Frame(self.root, bg="#d1e7dd")
        self.current_page.pack(fill="both", expand=True)

        tk.Label(self.current_page, text="Cart", font=("Arial", 18, "bold"), bg="#d1e7dd").pack(pady=10)

        self.cart_tree = ttk.Treeview(self.current_page, columns=("Item", "Price", "Quantity"), show="headings", height=6)
        self.cart_tree.heading("Item", text="Item Name")
        self.cart_tree.heading("Price", text="Price (Rs)")
        self.cart_tree.heading("Quantity", text="Quantity")
        self.cart_tree.pack(pady=10, padx=10)

        self.cursor.execute("SELECT item_name, price, quantity FROM cart WHERE user_id=%s", (self.user_id,))
        cart_items = self.cursor.fetchall()

        for item in cart_items:
            self.cart_tree.insert("", "end", values=(item[0], item[1], item[2]))

        if not cart_items:
            tk.Label(self.current_page, text="Your cart is empty.", font=("Arial", 12), bg="#d1e7dd").pack(pady=10)

        tk.Label(self.current_page, text="Item Name", font=("Arial", 14), bg="#d1e7dd").pack(pady=5)
        self.item_name_entry = tk.Entry(self.current_page, width=30)
        self.item_name_entry.pack(pady=5)

        tk.Label(self.current_page, text="Price (Rs)", font=("Arial", 14), bg="#d1e7dd").pack(pady=5)
        self.item_price_entry = tk.Entry(self.current_page, width=30)
        self.item_price_entry.pack(pady=5)

        tk.Label(self.current_page, text="Quantity", font=("Arial", 14), bg="#d1e7dd").pack(pady=5)
        self.item_quantity_entry = tk.Entry(self.current_page, width=30)
        self.item_quantity_entry.pack(pady=5)

        tk.Button(self.current_page, text="Add to Cart", font=("Arial", 14, "bold"), bg="#28a745", fg="white", command=self.add_to_cart).pack(pady=10)
        tk.Button(self.current_page, text="Proceed to Checkout", font=("Arial", 14, "bold"), bg="#007bff", fg="white", command=self.checkout).pack(pady=10)
        tk.Button(self.current_page, text="Back", font=("Arial", 14), bg="#dc3545", fg="white", command=self.show_welcome_page).pack(pady=5)

    def add_to_cart(self):
        """Add items to the cart."""
        item_name = self.item_name_entry.get().strip()
        price = self.item_price_entry.get().strip()
        quantity = self.item_quantity_entry.get().strip()

        if not item_name or not price.isdigit() or not quantity.isdigit():
            messagebox.showwarning("Input Error", "Please enter valid item details.")
            return

        price = float(price)
        quantity = int(quantity)

        self.cursor.execute("INSERT INTO cart (user_id, item_name, price, quantity) VALUES (%s, %s, %s, %s)", 
                            (self.user_id, item_name, price, quantity))
        self.conn.commit()
        messagebox.showinfo("Success", "Item added to cart.")
        self.show_cart_page()

    def checkout(self):
        """Handle checkout and update balance."""
        total_cost = 0
        self.cursor.execute("SELECT price, quantity FROM cart WHERE user_id=%s", (self.user_id,))
        cart_items = self.cursor.fetchall()

        for item in cart_items:
            total_cost += item[0] * item[1]

        if total_cost > self.balance:
            messagebox.showerror("Insufficient Funds", "You do not have enough balance to complete the purchase.")
            return

        # Deduct balance
        new_balance = self.balance - total_cost
        self.cursor.execute("UPDATE users SET balance = %s WHERE id = %s", (new_balance, self.user_id))
        self.conn.commit()

        # Clear cart
        self.cursor.execute("DELETE FROM cart WHERE user_id=%s", (self.user_id,))
        self.conn.commit()

        self.balance = new_balance
        messagebox.showinfo("Purchase Complete", f"Your purchase was successful! Total Cost: Rs.{total_cost:.2f}")
        self.show_welcome_page()

    def clear_current_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()

root = tk.Tk()
app = BudgetTrackerSystem(root)
root.mainloop()

