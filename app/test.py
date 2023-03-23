from pymongo import MongoClient
client = MongoClient(username="root", password="password")
db = client.test_database
users = db.users
users.insert_one({"name":"abc"})
users.insert_one({"name":"def"})
users.insert_one({"name":"ghi"})
my = users.find_one({"name":"def"})
print(my)


