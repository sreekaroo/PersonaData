
# from conection import Connection
#
# connected = False
# dbUsername = ""
# dbPassword = ""
# dbHost = ""
# while not connected:
#     dbUsername = input("enter database username: ")
#     dbPassword = input("enter database password: ")
#     dbHost = input("enter database host(For example, localhost): ")
#     db, error = Connection(dbUsername, dbPassword, dbHost).connect()
#
#     if db is not None:
#         db.close()
#         connected = True
#         print("Congrats you are connected!")
#         break
#
#     print("Try again: " + error)
#

# credentials for aws rds database instance
dbUsername = 'sreekaroo'
dbPassword = 'sabertooth'
dbHost = 'persona-data-rds.c9dah5ykqjzd.us-east-1.rds.amazonaws.com'
