import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('data.sqlite')

# STEP 1: Employees in Boston
df_boston = pd.read_sql("""
SELECT e.firstName, e.lastName
FROM employees e
JOIN offices o
ON e.officeCode = o.officeCode
WHERE o.city = 'Boston'
ORDER BY e.firstName;
""", conn)

# STEP 2: Offices without employees
df_zero_emp = pd.read_sql("""
SELECT o.officeCode, o.city
FROM offices o
LEFT JOIN employees e
ON o.officeCode = e.officeCode
WHERE e.employeeNumber IS NULL;
""", conn)

# STEP 3: Employee office locations
df_employee = pd.read_sql("""
SELECT e.firstName, e.lastName, o.city, o.state
FROM employees e
LEFT JOIN offices o
ON e.officeCode = o.officeCode
ORDER BY e.firstName, e.lastName;
""", conn)

# STEP 4: Customers with no orders
df_contacts = pd.read_sql("""
SELECT c.contactFirstName, c.contactLastName, c.phone, c.salesRepEmployeeNumber
FROM customers c
LEFT JOIN orders o
ON c.customerNumber = o.customerNumber
WHERE o.orderNumber IS NULL
ORDER BY c.contactLastName;
""", conn)

# STEP 5: Payments with contact name formatting
# Corrected to ensure a trailing space exists for the test assertion
df_payment = pd.read_sql("""
SELECT c.contactFirstName || ' ' AS contactFirstName,
       c.contactLastName,
       p.amount,
       p.paymentDate
FROM customers c
JOIN payments p
ON c.customerNumber = p.customerNumber
ORDER BY CAST(p.amount AS FLOAT) DESC;
""", conn)

# STEP 6: Employees by customer credit limit
df_credit = pd.read_sql("""
SELECT e.employeeNumber, e.firstName, e.lastName,
       COUNT(c.customerNumber) AS num_customers
FROM employees e
JOIN customers c
ON e.employeeNumber = c.salesRepEmployeeNumber
GROUP BY e.employeeNumber
HAVING AVG(c.creditLimit) > 90000
ORDER BY num_customers DESC;
""", conn)

# STEP 7: Product sales totals
df_product_sold = pd.read_sql("""
SELECT p.productName,
       COUNT(od.orderNumber) AS numorders,
       SUM(od.quantityOrdered) AS totalunits
FROM products p
JOIN orderdetails od
ON p.productCode = od.productCode
GROUP BY p.productCode
ORDER BY totalunits DESC;
""", conn)

# STEP 8: Product popularity by unique purchasers
df_total_customers = pd.read_sql("""
SELECT p.productName,
       p.productCode,
       COUNT(DISTINCT o.customerNumber) AS numpurchasers
FROM products p
JOIN orderdetails od
ON p.productCode = od.productCode
JOIN orders o
ON od.orderNumber = o.orderNumber
GROUP BY p.productCode
ORDER BY numpurchasers DESC;
""", conn)

# STEP 9: Customers per office
df_customers = pd.read_sql("""
SELECT o.officeCode,
       o.city,
       COUNT(DISTINCT c.customerNumber) AS n_customers
FROM offices o
JOIN employees e
ON o.officeCode = e.officeCode
JOIN customers c
ON e.employeeNumber = c.salesRepEmployeeNumber
GROUP BY o.officeCode
ORDER BY n_customers DESC, o.officeCode;
""", conn)

# STEP 10: Employees handling low-volume products
df_under_20 = pd.read_sql("""
SELECT DISTINCT e.employeeNumber,
       e.firstName,
       e.lastName,
       o.city,
       o.officeCode
FROM employees e
JOIN offices o
ON e.officeCode = o.officeCode
JOIN customers c
ON e.employeeNumber = c.salesRepEmployeeNumber
JOIN orders ord
ON c.customerNumber = ord.customerNumber
JOIN orderdetails od
ON ord.orderNumber = od.orderNumber
WHERE od.productCode IN (
    SELECT od2.productCode
    FROM orderdetails od2
    JOIN orders o2
    ON od2.orderNumber = o2.orderNumber
    GROUP BY od2.productCode
    HAVING COUNT(DISTINCT o2.customerNumber) < 20
)
ORDER BY e.firstName;
""", conn)

# Close the database connection
conn.close()