class User:
    def __init__(self,id,name,password):
        self.id=id
        self.name = name
        self.password = password
    def __str__(self):
        print(f"id: {self.id}")
        print(f"name: {self.name}")
        print(f"password: {self.password}")
