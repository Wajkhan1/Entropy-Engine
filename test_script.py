
from dictionary_checker import load_common_passwords
from strength_evaluator import evaluate_strength
from password_generator import generate_secure_password


load_common_passwords()

password = input("Enter password: ")
algorithm = input("Choose algorithm (md5/sha256/bcrypt): ")

result = evaluate_strength(password, algorithm)

print(result)

print("\nGenerated suggestion:")
print(generate_secure_password())