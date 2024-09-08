import mysql.connector
from mysql.connector import pooling

dbconfig ={
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "projectn"
}

connection_pool=pooling.MySQLConnectionPool(pool_name="mypool",pool_size=10,**dbconfig)

def connect():
 
    return connection_pool.get_connection()