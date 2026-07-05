class Student:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def greet(self) -> str:
        return f"Hello, my name is {self.name} and I am {self.age} years old."
    @staticmethod
    def is_adult(age: int) -> bool:
        return age >= 18

Student1 = Student("Alice", 20)
Student1.is_adult(10)
Student.is_adult(10)
Student1.greet()
Student.greet()