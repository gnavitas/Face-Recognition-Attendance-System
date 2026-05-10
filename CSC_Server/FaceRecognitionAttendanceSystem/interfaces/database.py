import sys
import mysql.connector
from mysql.connector import Error
from PyQt5.QtWidgets import QMessageBox, QApplication
import configparser as cp
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('database.log'),
        logging.StreamHandler()
    ]
)

class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance
    
    def _initialize_connection(self):
        filename = 'config.ini'
        inifile = cp.ConfigParser()
        inifile.read(filename, 'UTF-8')
        
        try:
            self.connection = mysql.connector.connect(
                host=inifile.get("db", "host"),
                port=inifile.get("db", "port"),
                user=inifile.get("db", "user"),
                password=inifile.get("db", "password"),
                database=inifile.get("db", "database")
            )
            # Use buffered cursor to prevent unread result errors
            self.cursor = self.connection.cursor(buffered=True, dictionary=True)
            logging.info("Database connection established successfully.")
        except Error as e:
            logging.error(f"Error connecting to MySQL database: {e}")
            QMessageBox.critical(None, "Database Connection Error", 
                                 f"Failed to connect to database:\n{str(e)}")
            sys.exit("Failed to start application")
    
    def execute_query(self, query, params=None):
        try:
            # Close any existing open results
            if self.cursor.with_rows:
                self.cursor.fetchall()
            
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            # Commit for write operations
            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                self.connection.commit()
            
            return self.cursor
        except Error as e:
            logging.error(f"Database query error: {e}")
            self.connection.rollback()
            raise
    
    def commit(self):
        """
        Commit the current database transaction.
        
        This method explicitly commits any pending database changes.
        Useful for write operations like INSERT, UPDATE, or DELETE.
        """
        try:
            if hasattr(self, 'connection') and self.connection.is_connected():
                self.connection.commit()
                logging.info("Database transaction committed successfully.")
            else:
                logging.warning("Cannot commit: No active database connection.")
        except Exception as e:
            logging.error(f"Error committing database transaction: {e}")
            raise

    def rollback(self):
        """
        Rollback the current database transaction.
        
        This method rolls back any pending changes in case of an error.
        Helps maintain database integrity.
        """
        try:
            if hasattr(self, 'connection') and self.connection.is_connected():
                self.connection.rollback()
                logging.info("Database transaction rolled back.")
            else:
                logging.warning("Cannot rollback: No active database connection.")
        except Exception as e:
            logging.error(f"Error rolling back database transaction: {e}")
            raise
    
    def close_connection(self):
        if hasattr(self, 'connection') and self.connection.is_connected():
            # Ensure cursor is closed first
            if hasattr(self, 'cursor'):
                self.cursor.close()
            self.connection.close()
            logging.info("Database connection closed.")

    def get_current_time(self):
        """
        Get the current time from the database server.
        Returns a datetime object representing the current time on the database server.
        """
        try:
            cursor = self.execute_query("SELECT NOW() as current_time")
            result = cursor.fetchone()
            return result['current_time']
        except Error as e:
            logging.error(f"Error getting database time: {e}")
            raise

# Global database manager instance
mydb = DatabaseManager()

App = QApplication(sys.argv)