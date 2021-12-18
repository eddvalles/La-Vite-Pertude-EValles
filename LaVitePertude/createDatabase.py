import sqlite3
import faker
import os

def main():

    #The below OS portion will allow you to recreate a brand new scratch DB every time this program is run
    os.system('cd E:\\Database Development\\LaVitePertude')
    if 'LaVitePertude.db' in os.popen('dir').read():
        os.system('del LaVitePertude.db')
    os.system('sqlite3.exe LaVitePertude.db <createDatabase.txt')

    con = sqlite3.connect('LaVitePertude.db')
    fake = faker.Faker()
    cursor = con.cursor()

    default_customers = 15 #Change this variable to change the default # of customers generated (15 default)
    default_purchases = 20 #Change this variable to change the default # of bottles to purchase (20 default)
    default_markup = 1.20  #Change this variable to change the markup percentage (sell for 20% above vendor price)

    #The below 'with' statement will pull data from our vendor.txt and wine.txt files and insert into the DB
    with open('manufacturer.txt', 'r') as vendor, open('wine.txt') as wine:
        man_header = vendor.readline()
        wine_header = wine.readline()

        def line_strip(line):
            line = line.strip().split(',')
            entry_string = ''
            for entry in line:
                entry = '"' + entry.strip() + '"'
                entry_string = entry_string + entry + ', '
            return entry_string

        for vend_line in vendor: #Will go through the lines until there are no more left
            entry_string = line_strip(vend_line)
            if entry_string == '"", ': break
            entry_string = entry_string.rstrip(', ')
            cursor.execute(f"""INSERT INTO Vendor(Vendor_Name, Vendor_ID, Vendor_Address, Vendor_Contact) 
                VALUES ({entry_string});""")

        for wine_line in wine:
            entry_string = line_strip(wine_line).rstrip(', ')
            cursor.execute(f"""
            INSERT INTO Wine(Wine_ID, Wine_Name, Wine_Type, Vendor_ID, Wine_Price)
            VALUES ({entry_string});""")

    #The below portion will generate the customers and insert them into the Customers table
    for i in range(default_customers):
        cursor.execute(f"""
                    INSERT INTO Customer(
                        Customer_First_Name,
                        Customer_Last_Name,
                        Customer_St_Address,
                        Customer_City,
                        Customer_State,
                        Customer_Zip) 
                    VALUES(
                        '{fake.first_name()}',
                        '{fake.last_name()}',
                        '{fake.street_address()}',
                        '{fake.city()}',
                        '{fake.state()}',
                        '{fake.zipcode()}'
                    )""")

    #The below portion of code will generate a default 20 purchases to start off your inventory
    #This is what was bought from the vendor so our business can have bottles to sell
    wine_purchases = cursor.execute("SELECT Wine_ID, Wine_Price FROM Wine").fetchall()
    for i in range(len(wine_purchases)):
        cursor.execute(f"""
        INSERT INTO Purchases(Wine_ID, Num_Received, Purchase_Price)
        VALUES ('{wine_purchases[i][0]}',
                '{default_purchases}',
                '{wine_purchases[i][1]}')
        """)

    # The below portion of code uses the new contents in the purchases table, to create our store stock
    purchase_results = cursor.execute("SELECT Wine_ID, Num_Received, Purchase_Price FROM Purchases").fetchall()
    for i in range(len(purchase_results)):
        cursor.execute(f"""
        INSERT INTO Wine_Stock(Wine_ID, Wine_On_Hand, Minimum_Wine_Required, Wine_Sale_Price)
        Values('{purchase_results[i][0]}',
                '{purchase_results[i][1]}',
                3,
                '{purchase_results[i][2] * default_markup:.2f}'
        )""")

    #The below code block is to view the outputs of all the generated tables
    view_output = ["SELECT * FROM Wine;", "SELECT * FROM Vendor;", "SELECT * FROM Customer;",
                   "SELECT * FROM Purchases;", "SELECT * FROM Wine_Stock"]
    table_name = ['Wine', 'Vendor', 'Customer', 'Purchases', 'Wine_Stock']

    for i in range(len(view_output)):
        results = cursor.execute(view_output[i]).fetchall()
        print(table_name[i] + ':')
        for record in results:
            print(record)
        print()

    con.commit() #Do not uncomment unless you are ready to commit a brand new database
    con.close()

if __name__ == '__main__':
    main()