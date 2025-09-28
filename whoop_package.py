from whoop import WhoopClient

# Using a traditional constructor
client = WhoopClient(username, password)
...

# Using a context manager
with WhoopClient(username, password) as client:
    ...