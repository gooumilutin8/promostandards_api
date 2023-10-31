import cryptocode

encoded = cryptocode.encrypt("mystring","mypassword")
print(encoded)
## And then to decode it:
decoded = cryptocode.decrypt(encoded, "mypassword")
print(decoded)