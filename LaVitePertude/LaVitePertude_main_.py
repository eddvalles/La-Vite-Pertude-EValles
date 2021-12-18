import sqlite3
import tkinter as ttk
import tkinter.ttk
from tabulate import tabulate
from tkinter import *


def main():
    con = sqlite3.connect('LaVitePertude.db')
    cursor = con.cursor()

    inventoryRoot = ttk.Tk()

    storeRoot = ttk.Tk()

    Inventory(inventoryRoot, cursor)
    Storefront(storeRoot, cursor)

    storeRoot.mainloop()
    inventoryRoot.mainloop()

    #con.commit() #Uncomment this if you are ready to commit any changes at the end of database usage

#Serves as the basic framework for shared methods between Inventory and Storefront
class Frame:
    def __init__(self, master, cursor):
        self.title = master.title("La Vite Pertuda Wine Retailer")
        self.icon = master.iconbitmap('icon.ico')
        self.cursor = cursor
        self.font = ("Times", 10)

        # Set window size for both screens
        width = 932
        height = 642

        master.geometry("932x642")  # Put alignstr variable in this to center the creation of the screens
        master.resizable(width=False, height=False)

        # Vendor Drop Down Box
        self.vendors = [vendor[0] for vendor in self.cursor.execute("SELECT Vendor_Name FROM Vendor").fetchall()]

        self.vendor_label = tkinter.Label(master, text='Choose a Vendor: ', font=self.font)
        self.vendor_label.place(x=500, y=70, width=100, height=25)

        self.vendor_combo = tkinter.ttk.Combobox(master, value=self.vendors)
        self.vendor_combo.place(x=600, y=70, width=275, height=25)
        self.vendor_combo.bind("<<ComboboxSelected>>", self.vendor_func)

        # Dependent Wine Drop Down Box
        self.wine_label = tkinter.Label(master, text='Choose a Wine: ', font=self.font)
        self.wine_label.place(x=505, y=95, width=100, height=25)

        self.wine_combo = tkinter.ttk.Combobox(master, value=[" "])
        self.wine_combo.place(x=600, y=95, width=275, height=25)
        self.wine_combo.bind("<<ComboboxSelected>>", self.wine_func)

        #Quantity to purchase
        self.quantity_label = tkinter.Label(master, text='Quantity: ', font=self.font)
        self.quantity_label.place(x=522, y=120, width=100, height=25)

        self.n = ttk.StringVar()
        self.spinbox = tkinter.Spinbox(master, from_=0, to_=20, textvariable=self.n, command=self.spin_func)
        self.spinbox.place(x=600, y=120, width=275, height=25)

        #Dependent Price Tag (Cost you are selling that wine to the buyer)
        self.price_label = tkinter.Label(master, text='Price: ', font=self.font)
        self.price_label.place(x=531, y=145, width=100, height=25)

        self.price_calc = tkinter.Label(master, text='0.00', font=self.font)
        self.price_calc.place(x=631, y=145, width=100, height=25)

    def spin_func(self):
        result = self.cursor.execute(f"""
                    SELECT *
                    FROM ((Wine_Stock
                    INNER JOIN Purchases ON Wine_Stock.Wine_ID=Purchases.Wine_ID)
                    INNER JOIN Wine ON Wine_Stock.Wine_ID=Wine.Wine_ID)
                    WHERE Wine.Wine_Name='{self.wine_combo.get()}';""").fetchall()
        price = result[0][3]
        quantity = float(self.spinbox.get())

        self.price_calc.config(text=f'{price * quantity:.2f}$')

    def wine_func(self, event):
        result = self.cursor.execute(f"""
            SELECT *
            FROM ((Wine_Stock
            INNER JOIN Purchases ON Wine_Stock.Wine_ID=Purchases.Wine_ID)
            INNER JOIN Wine ON Wine_Stock.Wine_ID=Wine.Wine_ID)
            WHERE Wine.Wine_Name='{self.wine_combo.get()}';""").fetchall()
        price = result[0][3]
        quantity = float(self.spinbox.get())
        self.price_calc.config(text=f'{price * quantity:.2f}$')

    def vendor_func(self, event):
        vendor = self.vendor_combo.get()
        wine_items = [wine for wine in self.cursor.execute(f"""
            SELECT Wine_Name
            FROM Wine, Vendor
            WHERE Wine.Vendor_ID=Vendor.Vendor_ID AND Vendor.Vendor_Name LIKE '{vendor}';
        """).fetchall()]
        self.wine_combo.config(value=[wine[0] for wine in wine_items])
        self.wine_combo.current(0)

        quantity = float(self.spinbox.get())

        result = self.cursor.execute(f"""
            SELECT *
            FROM ((Wine_Stock
            INNER JOIN Purchases ON Wine_Stock.Wine_ID=Purchases.Wine_ID)
            INNER JOIN Wine ON Wine_Stock.Wine_ID=Wine.Wine_ID)
            WHERE Wine.Wine_Name='{self.wine_combo.get()}';""").fetchall()

        price = result[0][3]

        answer = quantity * price

        self.price_calc.config(text=f'{answer:.2f}')


class Storefront(Frame):
    #Placement of all widgets in the Storefront GUI Window
    def __init__(self, store_master, cursor):
        super().__init__(store_master, cursor)

        # Title label
        self.store_label = ttk.Label(store_master, text='Welcome to La Vite Pertude !', font=("Times", 15))
        self.store_label.place(x=320, y=20, width=270, height=25)

        # Purchase Item label
        self.purchase_label = ttk.Label(store_master, text='Purchase Item:', font=self.font)
        self.purchase_label.place(x=585, y=65, width=110, height=25)

        # Place vendor label
        self.vendor_label.place(x=500, y=120, width=100, height=25)
        self.vendor_combo.place(x=600, y=120, width=275, height=25)

        #Place wine label
        self.wine_label.place(x=505, y=145, width=100, height=25)
        self.wine_combo.place(x=600, y=145, width=275, height=25)

        #Place quantity label
        self.quantity_label.place(x=522, y=170, width=100, height=25)
        self.spinbox.place(x=600, y=170, width=275, height=25)

        #Place Price label
        self.price_label.place(x=531, y=195, width=100, height=25)
        self.price_calc.place(x=631, y=195, width=100, height=25)

        # Customer Purchase Button
        self.purchase_item = ttk.Button(store_master, text='Purchase', command=self.make_purchase)
        self.purchase_item.place(x=600, y=220, width=50, height=25)

        # Returning Customer Label
        self.rtrn_cust_label = ttk.Label(store_master, text='Customer ID: ', font=self.font)
        self.rtrn_cust_label.place(x=487, y=95, width=150, height=25)

        self.rtrn_cust_entry = ttk.Entry(store_master, width=30)
        self.rtrn_cust_entry.place(x=600, y=95, width=150, height=25)

        # Customer Information Label
        self.customerLabel = ttk.Label(store_master, text='Customer Information: ', font=self.font)
        self.customerLabel.place(x=0, y=65, width=150, height=25)

        # Customer First Name
        self.Customer_First_Name_Label = ttk.Label(store_master, text='First Name:', font=self.font)
        self.Customer_First_Name_Label.place(x=0, y=90, width=150, height=25)

        self.Customer_First_Name_Entry = ttk.Entry(store_master, width=50)
        self.Customer_First_Name_Entry.place(x=150, y=90, width=150, height=25)

        # Customer Last Name
        self.Customer_Last_Name_Label = ttk.Label(store_master, text='Last Name:', font=self.font)
        self.Customer_Last_Name_Label.place(x=0, y=115, width=150, height=25)

        self.Customer_Last_Name_Entry = ttk.Entry(store_master, width=50)
        self.Customer_Last_Name_Entry.place(x=150, y=115, width=150, height=25)

        # Customer St Address
        self.Customer_St_Address_Label = ttk.Label(store_master, text='Address:', font=self.font)
        self.Customer_St_Address_Label.place(x=0, y=140, width=150, height=25)

        self.Customer_St_Address_Entry = ttk.Entry(store_master, width=50)
        self.Customer_St_Address_Entry.place(x=150, y=140, width=150, height=25)

        # Customer City
        self.Customer_City_Label = ttk.Label(store_master, text='City:', font=self.font)
        self.Customer_City_Label.place(x=0, y=165, width=150, height=25)

        self.Customer_City_Entry = ttk.Entry(store_master, width=50)
        self.Customer_City_Entry.place(x=150, y=165, width=150, height=25)

        # Customer State
        self.Customer_State_Label = ttk.Label(store_master, text='State:', font=self.font)
        self.Customer_State_Label.place(x=0, y=190, width=150, height=25)

        self.Customer_State_Entry = ttk.Entry(store_master, width=30)
        self.Customer_State_Entry.place(x=150, y=190, width=150, height=25)

        # Customer Zip
        self.Customer_Zip_Label = ttk.Label(store_master, text='Zip:', font=self.font)
        self.Customer_Zip_Label.place(x=0, y=215, width=150, height=25)

        self.Customer_Zip_Entry = ttk.Entry(store_master, width=30)
        self.Customer_Zip_Entry.place(x=150, y=215, width=150, height=25)

        # Customer Submit Button
        self.getCustomerInfo = ttk.Button(store_master, text='Submit', command=self.getCustomerInfo)
        self.getCustomerInfo.place(x=125, y=265, width=50, height=25)

        # Delete Customer Record
        self.delete_cust_label = ttk.Label(store_master, text='Customer ID: ', font=self.font)
        self.delete_cust_label.place(x=0, y=350, width=100, height=25)

        self.delete_cust_entry = ttk.Entry(store_master)
        self.delete_cust_entry.place(x=100, y=350, width=150, height=25)

        self.delete_cust_button = ttk.Button(store_master, text='Delete', font=self.font)
        self.delete_cust_button["command"] = self.delete_customer
        self.delete_cust_button.place(x=250, y=350, width=50, height=25)

    #Where the transaction for each purchase are being made
    def make_purchase(self):

        wine_id = self.cursor.execute(f"""
        SELECT Wine_ID
        FROM Wine
        WHERE Wine_Name LIKE '{self.wine_combo.get()}'""").fetchall()[0][0]

        purchase_price = self.cursor.execute(f"""
        SELECT Wine_Sale_Price
        FROM Wine_Stock, Wine
        WHERE Wine_Stock.Wine_ID=Wine.Wine_ID 
        AND Wine.Wine_Name LIKE '{self.wine_combo.get()}'""").fetchall()[0][0]

        customer_ID = self.rtrn_cust_entry.get()

        quantity = self.spinbox.get()

        self.cursor.execute(f"""
        INSERT INTO Customer_Orders(
            Wine_ID,
            Num_Purchased,
            Purchase_Price,
            Customer_ID)
        VALUES(
            '{wine_id}',
            '{quantity}',
            '{purchase_price}',
            '{customer_ID}')
        """)

        #Removes the quantity from our stock
        result = self.cursor.execute(f"""
            UPDATE Wine_Stock
            SET Wine_On_Hand=Wine_On_Hand - {quantity}
            WHERE Wine_Stock.Wine_ID LIKE '{wine_id}';
        """)

        self.vendor_combo.delete(0, END)
        self.wine_combo.delete(0, END)
        self.rtrn_cust_entry.delete(0, END)
        self.price_calc.config(text=0.00)

        get_wine_id = self.cursor.execute(f"""
        SELECT Wine_ID, SUM(Num_Purchased) AS Total_Purchased
        FROM Customer_Orders
        GROUP BY Wine_ID
        ORDER BY Total_Purchased DESC
        LIMIT 1""").fetchall()

        get_wine_id = get_wine_id[0][0]
        get_wine_name = self.cursor.execute(f"SELECT Wine_Name FROM Wine WHERE Wine_ID LIKE '{get_wine_id}';").fetchall()

        best_seller_display.config(text=get_wine_name[0][0])

        total_sold = self.cursor.execute("""
                    SELECT SUM(Num_Purchased)
                    FROM Customer_Orders""").fetchall()

        total_sold_display.config(text=total_sold[0][0])

        total_stock = self.cursor.execute(f"""SELECT SUM(Wine_On_Hand * Wine_Sale_Price) AS Total_Stock_Value
                            FROM Wine_Stock""").fetchall()

        total_value_display.config(text=total_stock[0][0])

    #Retrieves provided customer information and inserts into Customer table
    def getCustomerInfo(self):
        #Regex could be added here to validate user entry
        self.cursor.execute(f"""INSERT INTO Customer
        (Customer_First_Name,Customer_Last_Name,Customer_St_Address, Customer_City, Customer_State, Customer_Zip)
        VALUES ('{self.Customer_First_Name_Entry.get()}',
                '{self.Customer_Last_Name_Entry.get()}',
                '{self.Customer_St_Address_Entry.get()}',
                '{self.Customer_City_Entry.get()}',
                '{self.Customer_State_Entry.get()}',
                '{self.Customer_Zip_Entry.get()}'
        )""")

        name= self.Customer_First_Name_Entry.get()
        print(f"Hello, {name}")
        print("Here is your record!")
        print(self.cursor.execute(f"SELECT * FROM Customer WHERE Customer_First_Name LIKE '{name}'").fetchall())
        print()

        self.Customer_Last_Name_Entry.delete(0, END)
        self.Customer_First_Name_Entry.delete(0, END)
        self.Customer_St_Address_Entry.delete(0, END)
        self.Customer_City_Entry.delete(0, END)
        self.Customer_State_Entry.delete(0, END)
        self.Customer_Zip_Entry.delete(0, END)

    #Deletes the specified customer information by CustomerID
    def delete_customer(self):
        record = self.delete_cust_entry.get()
        self.cursor.execute(f"""
        DELETE
        FROM Customer
        WHERE Customer_ID LIKE '{record}';
        """)


class Inventory(Frame):
    #Placement of all widgets in the Inventory GUI Window
    def __init__(self, inv_master, cursor):
        super().__init__(inv_master, cursor)

        # Title label
        inv_label = ttk.Label(inv_master, text='Inventory', font=("Times", 16))
        inv_label.place(x=400, y=20, width=100, height=20)

        # Purchase Label
        self.purchase_label = ttk.Label(inv_master, text='Purchase Inventory:', font=self.font)
        self.purchase_label.place(x=600, y=40, width=110, height=25)

        #Display ALL Tables
        self.output_all = ttk.Button(inv_master, text='All', command=self.output_all)
        self.output_all.place(x=775, y=200, width=100, height=25)

        #Display Customer Table
        self.display_customer_label = ttk.Label(inv_master, text='Display Customer Information: ', font=self.font)
        self.display_customer_label.place(x=575, y=225, width=200, height=25)

        self.display_customer = ttk.Button(inv_master, text='Customer', font=self.font)
        self.display_customer["command"] = self.output_customer
        self.display_customer.place(x=775, y=225, width=100, height=25)

        #Display Customer_Orders Table
        self.display_customer_orders_label = ttk.Label(inv_master, text='Display Customer Orders: ', font=self.font)
        self.display_customer_orders_label.place(x=612, y=250, width=150, height=25)

        self.display_customer_orders = ttk.Button(inv_master, text='Customer_Orders', font=self.font)
        self.display_customer_orders["command"] = self.output_customer_orders
        self.display_customer_orders.place(x=775, y=250, width=100, height=25)

        #Display Wine_Stock Table
        self.display_wine_stock_label = ttk.Label(inv_master, text='Display Wine Stock: ', font=self.font)
        self.display_wine_stock_label.place(x=612, y=275, width=150, height=25)

        self.display_wine_stock = ttk.Button(inv_master, text='Wine_Stock', font=self.font)
        self.display_wine_stock["command"] = self.output_wine_stock
        self.display_wine_stock.place(x=775, y=275, width=100, height=25)

        #Display Purchases Table
        self.display_purchases_label = ttk.Label(inv_master, text='Display Purchases: ', font=self.font)
        self.display_purchases_label.place(x=612, y=300, width=150, height=25)

        self.display_purchases = ttk.Button(inv_master, text='Purchases', font=self.font)
        self.display_purchases["command"] = self.output_purchase
        self.display_purchases.place(x=775, y=300, width=100, height=25)

        #Purchase Stock button
        self.purchase_item = ttk.Button(inv_master, text='Purchase', command=self.make_purchase)
        self.purchase_item.place(x=600, y=180, width=50, height=25)

        # Current Stock Label
        self.stock_label = ttk.Label(inv_master, text='Current Stock:', font=self.font)
        self.stock_label.place(x=0, y=40, width=100, height=25)

        #Wine_ID Label
        self.wine_id_label = ttk.Label(inv_master, text='Wine_ID', font=self.font)
        self.wine_id_label.place(x=0, y=65, width=100, height=25)

        #Wine Name Label
        self.wine_name_label = ttk.Label(inv_master, text='Wine_Name', font=self.font)
        self.wine_name_label.place(x=100, y=65, width=200, height=25)

        #Wine_Price
        self.wine_price_label = ttk.Label(inv_master, text='Wine_Price', font=self.font)
        self.wine_price_label.place(x=300, y=65, width=100, height=25)

        self.wine_id_one, self.wine_id_two, self.wine_id_three = ('W002', 'W020', 'W023')

        self.wine_one, self.wine_two, self.wine_three = [id[0] for id in self.cursor.execute("""
            SELECT Wine_Name 
            FROM Wine 
            WHERE Wine_ID IN ('W002','W020','W023');""").fetchall()]

        #Modify Price 1
        self.wine_one_label = ttk.Label(inv_master, text=self.wine_id_one, font=self.font)
        self.wine_one_label.place(x=0, y=90, width=100, height=25)

        self.wine_one_name_label = ttk.Label(inv_master, text=self.wine_one, font=("Times", 7))
        self.wine_one_name_label.place(x=100, y=90, width=200, height=25)

        self.p = ttk.DoubleVar(value=self.get_wine_price(self.wine_id_one))
        self.wine_one_spinbox = ttk.Spinbox(inv_master,
                                            from_=1,
                                            to_=300,
                                            increment=0.01,
                                            textvariable=self.p)
        self.wine_one_spinbox.place(x=300, y=90, width=100, height=25)

        #Modify Price 2
        self.wine_two_label = ttk.Label(inv_master, text=self.wine_id_two, font=self.font)
        self.wine_two_label.place(x=0, y=115, width=100, height=25)

        self.wine_two_name_label = ttk.Label(inv_master, text=self.wine_two, font=("Times", 7))
        self.wine_two_name_label.place(x=100, y=115, width=200, height=25)

        self.q = ttk.DoubleVar(value=self.get_wine_price(self.wine_id_two))
        self.wine_two_spinbox = ttk.Spinbox(inv_master,
                                            from_=1,
                                            to_=300,
                                            increment=0.01,
                                            textvariable=self.q)
        self.wine_two_spinbox.place(x=300, y=115, width=100, height=25)

        #Modify Price 3
        self.wine_three_label = ttk.Label(inv_master, text=self.wine_id_three, font=self.font)
        self.wine_three_label.place(x=0, y=140, width=100, height=25)

        self.wine_three_name_label = ttk.Label(inv_master, text=self.wine_three, font=("Times", 7))
        self.wine_three_name_label.place(x=100, y=140, width=200, height=25)

        self.r = ttk.DoubleVar(value=self.get_wine_price(self.wine_id_three))
        self.wine_three_spinbox = ttk.Spinbox(inv_master,
                                            from_=1,
                                            to_=300,
                                            increment=0.01,
                                            textvariable=self.r)
        self.wine_three_spinbox.place(x=300, y=140, width=100, height=25)

        #Update Prices
        self.update_stock_prices = ttk.Button(inv_master, text='Update', font=self.font)
        self.update_stock_prices["command"] = self.update_prices
        self.update_stock_prices.place(x=300, y=165, width=100, height=25)

        # Reports label
        self.show_reports = ttk.Label(inv_master, text='Reports: ', font=self.font)
        self.show_reports.place(x=0, y=375, width=60, height=25)

        # Total Wine Purchased From Vendors
        self.total_purchased_label = ttk.Label(inv_master, text='Total Purchased: ', font=self.font)
        self.total_purchased_label.place(x=0, y=400, width=100, height=25)

        total_purchased = self.cursor.execute("""
            SELECT SUM(Num_Received * Purchase_Price) AS Total_Cost
            FROM Purchases""").fetchall()

        self.total_purchased_display = ttk.Label(inv_master, text=total_purchased[0][0], font=self.font)
        self.total_purchased_display.place(x=100, y=400, width=100, height=25)

        total_purchased = 'Total Cost of all wines purchased from the vendor'
        self.total_purchased_text = ttk.Label(inv_master, text=total_purchased, font=self.font)
        self.total_purchased_text.place(x=200, y=400, width=300, height=25)


        # Total Value of Wine in Wine_Stock
        self.total_value_label = ttk.Label(inv_master, text='Total Stock Value: ', font=self.font)
        self.total_value_label.place(x=0, y=425, width=100, height=25)

        self.total_stock = self.cursor.execute(f"""SELECT SUM(Wine_On_Hand * Wine_Sale_Price) AS Total_Stock_Value
            FROM Wine_Stock""").fetchall()

        global total_value_display
        total_value_display = ttk.Label(inv_master, text=self.total_stock[0][0], font=self.font)
        total_value_display.place(x=100, y=425, width=100, height=25)

        total_value = 'Total value of all wine in our Wine_Stock table'
        self.total_value_text = ttk.Label(inv_master, text=total_value, font=self.font)
        self.total_value_text.place(x=200, y=425, width=300, height=25)


        # Total Wine Sold to Customers
        self.total_sold_label = ttk.Label(inv_master, text='Total Bottles Sold: ', font=self.font)
        self.total_sold_label.place(x=0, y=450, width=100, height=25)

        total_sold = self.cursor.execute("""
            SELECT SUM(Num_Purchased)
            FROM Customer_Orders""").fetchall()

        global total_sold_display
        total_sold_display = ttk.Label(inv_master, text=total_sold, font=self.font)
        total_sold_display.place(x=100, y=450, width=100, height=25)

        self.total_sold_text = ttk.Label(inv_master, text='Total Sold to Customers', font=self.font)
        self.total_sold_text.place(x=200, y=450, width=300, height=25)

        # Wine that is the best seller (the one with the most purchases made)
        self.best_seller_label = ttk.Label(inv_master, text='Top Seller: ')
        self.best_seller_label.place(x=0, y=475, width=100, height=25)

        get_wine_id = self.cursor.execute(f"""
                SELECT Wine_ID, SUM(Num_Purchased) AS Total_Purchased
                FROM Customer_Orders
                GROUP BY Wine_ID
                ORDER BY Total_Purchased DESC
                LIMIT 1""").fetchall()

        get_wine_name = self.cursor.execute(f"""
                SELECT Wine_Name
                FROM WINE
                WHERE Wine_ID LIKE '{get_wine_id[0][0]}';""").fetchall()

        global best_seller_display
        best_seller_display = ttk.Label(inv_master, text=get_wine_name[0][0], font=("Times", 10))
        best_seller_display.place(x=100, y=475, width=300, height=25)

        # Total Purchases made by a specific Customer (by Customer_ID)
        self.rtrn_cust_advise = ttk.Label(inv_master, text='View purchases made by a specific customer:', font=self.font)
        self.rtrn_cust_advise.place(x=0, y=525, width=250, height=25)

        self.rtrn_cust_label = ttk.Label(inv_master, text='Customer ID: ', font=self.font)
        self.rtrn_cust_label.place(x=0, y=550, width=100, height=25)

        self.rtrn_cust_entry = ttk.Entry(inv_master, width=30)
        self.rtrn_cust_entry.place(x=100, y=550, width=150, height=25)

        self.rtrn_cust_button = ttk.Button(inv_master, text='Query', command=self.get_cust_purchases)
        self.rtrn_cust_button.place(x=250, y=550, width=40, height=25)

    def make_purchase(self):
        wine_id = self.cursor.execute(f"""
        SELECT Wine_ID
        FROM Wine
        WHERE Wine_Name LIKE '{self.wine_combo.get()}';
        """).fetchall()[0][0]

        num_received = self.spinbox.get()

        purchase_price = self.cursor.execute(f"""
        SELECT Wine_Price
        FROM Wine
        WHERE Wine.Wine_Name='{self.wine_combo.get()}'""").fetchall()[0][0]

        #Creates the record in the Purchases table
        self.cursor.execute(f"""
        INSERT INTO Purchases(Wine_ID, Num_Received, Purchase_Price)
        VALUES(
            '{wine_id}',
            '{num_received}',
            '{purchase_price}');
        """)

        #Updates the appropriate record in the Wine_Stock table
        self.cursor.execute(f"""
        UPDATE Wine_Stock
        SET Wine_On_Hand=Wine_On_Hand + {num_received} 
        WHERE Wine_ID LIKE '{wine_id}';
        """)

        self.vendor_combo.delete(0, END)
        self.wine_combo.delete(0, END)
        self.price_calc.config(text=0.00)

        total_purchased = self.cursor.execute("""
                    SELECT SUM(Num_Received * Purchase_Price) AS Total_Cost
                    FROM Purchases""").fetchall()

        self.total_purchased_display.config(text=f"{total_purchased[0][0]}")

        total_stock = self.cursor.execute(f"""SELECT SUM(Wine_On_Hand * Wine_Sale_Price) AS Total_Stock_Value
                    FROM Wine_Stock""").fetchall()

        total_value_display.config(text=total_stock[0][0])

    #Retrieves purchases made by a specific customer and outputs using Tabulate
    def get_cust_purchases(self):

        customer_id = self.rtrn_cust_entry.get()

        result = self.cursor.execute(f"""
        SELECT Customer_Orders.Customer_ID, Customer_Last_Name, Wine_ID, Num_Purchased, Purchase_Price,
            Num_Purchased * Purchase_Price AS Total_Cost
        FROM Customer_Orders, Customer
        WHERE Customer_Orders.Customer_ID=Customer.Customer_ID
        AND Customer_Orders.Customer_ID LIKE '{customer_id}';
        """).fetchall()

        print(tabulate(result, headers=[
            "Customer_ID",
            "Customer_Last_Name",
            "Wine_ID",
            "Num_Purchased",
            "Purchase_Price",
            "Total_Cost"
        ]))

    #Updates prices of three wines available in the Inventory window
    def update_prices(self):
        price_one = self.wine_one_spinbox.get()
        price_two = self.wine_two_spinbox.get()
        price_three = self.wine_three_spinbox.get()

        self.cursor.execute(f"""
        UPDATE Wine_Stock
        SET Wine_Sale_Price={price_one}
        WHERE Wine_ID LIKE '{self.wine_id_one}'""")

        self.cursor.execute(f"""
        UPDATE Wine_Stock
        SET Wine_Sale_Price={price_two}
        WHERE Wine_ID LIKE '{self.wine_id_two}'""")

        self.cursor.execute(f"""
        UPDATE Wine_Stock
        SET Wine_Sale_Price={price_three}
        WHERE Wine_ID LIKE '{self.wine_id_three}'""")

    #Used to retrieve the current price of a particular wine by it's ID
    def get_wine_price(self, wine_id):
        price = self.cursor.execute(f"""
        SELECT Wine_Sale_Price
        FROM Wine_Stock
        WHERE Wine_ID LIKE '{wine_id}'""").fetchall()

        return price[0]

    #Used to output the current contents of all tables
    def output_all(self): #No format provided with the use of this method
        view_output = ["SELECT * FROM Wine;", "SELECT * FROM Vendor;", "SELECT * FROM Customer;",
                       "SELECT * FROM Purchases;", "SELECT * FROM Wine_Stock", "SELECT * FROM Customer_Orders"]
        table_name = ['Wine', 'Vendor', 'Customer', 'Purchases', 'Wine_Stock', 'Customer_Orders']

        for i in range(len(view_output)):
            results = self.cursor.execute(view_output[i]).fetchall()
            print(table_name[i] + ':')
            for record in results:
                print(record)
            print()

    #Used to output the current contents of the Customer table
    def output_customer(self):
        result = self.cursor.execute("SELECT * FROM Customer").fetchall()
        print(tabulate(result, headers=[
            "Customer_ID",
            "Customer_First_Name",
            "Customer_Last_Name",
            "Customer_St_Address",
            "Customer_City",
            "Customer_State",
            "Customer_Zip"
        ]))

    #Used to output the current contents of the Customer Orders table
    def output_customer_orders(self):
        result = self.cursor.execute("SELECT *, Num_Purchased * Purchase_Price AS Total_Cost FROM Customer_Orders")
        result = result.fetchall()
        print(tabulate(result, headers=[
            "Order_ID",
            "Wine_ID",
            "Num_Purchased",
            "Purchase_Price",
            "Customer_ID",
            "Total_Cost"
        ]))

    #Used to output the current contents of the Wine_Stock table
    def output_wine_stock(self):
        result = self.cursor.execute("SELECT * FROM Wine_Stock").fetchall()
        print(tabulate(result, headers=[
            "Wine_ID",
            "Wine_On_Hand",
            "Minimum_Wine_Required",
            "Wine_Sale_Price",
        ]))

    #Used to output the current contents of the Purchases table
    def output_purchase(self):
        result = self.cursor.execute("SELECT *, Num_Received * Purchase_Price AS Total_Paid FROM Purchases").fetchall()
        print(tabulate(result, headers=[
            "Purchase_ID",
            "Wine_ID",
            "Num_Received",
            "Purchase_Price",
            "Total Paid"
        ]))

    def spin_func(self):
        result = self.cursor.execute(f"""
            SELECT Wine_Price
            FROM WINE
            WHERE Wine.Wine_Name='{self.wine_combo.get()}';""").fetchall()
        price = result[0][0]
        quantity = float(self.spinbox.get())

        self.price_calc.config(text=f'{price * quantity:.2f}$')

    def wine_func(self, event):
        result = self.cursor.execute(f"""
            SELECT Wine_Price
            FROM WINE
            WHERE Wine.Wine_Name='{self.wine_combo.get()}';""").fetchall()
        price = result[0][0]
        quantity = float(self.spinbox.get())
        self.price_calc.config(text=f'{price * quantity:.2f}$')

    def vendor_func(self, event):
        vendor = self.vendor_combo.get()
        wine_items = [wine for wine in self.cursor.execute(f"""
            SELECT Wine_Name
            FROM Wine, Vendor
            WHERE Wine.Vendor_ID=Vendor.Vendor_ID AND Vendor.Vendor_Name LIKE '{vendor}';
        """).fetchall()]
        self.wine_combo.config(value=[wine[0] for wine in wine_items])
        self.wine_combo.current(0)

        quantity = float(self.spinbox.get())

        result = self.cursor.execute(f"""
            SELECT Wine_Price
            FROM WINE
            WHERE Wine.Wine_Name='{self.wine_combo.get()}';""").fetchall()
        price = result[0][0]

        answer = quantity * price

        self.price_calc.config(text=f'{answer:.2f}')

if __name__ == '__main__':
    main()