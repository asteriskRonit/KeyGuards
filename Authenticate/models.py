from django.db import models

class User_Admin(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email}"
    

class UserTab(models.Model):

    serial = models.IntegerField()  # Integer field for serial
    name = models.CharField(max_length=255)  # String field for name
    email = models.EmailField(primary_key=True)  # String field for email (email validation included)
    department_id = models.IntegerField()  # Integer field for department ID
    access = models.BooleanField(default=False)  # Boolean field for access

    def __str__(self):
        return f"{self.name} ({self.email})"


class Department(models.Model):
    department_id = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    department_name = models.CharField(max_length=100)  # String field for department name
    key = models.CharField(max_length=255)  # String field for the key

    def __str__(self):
        return self.department_name  # Display the department name in the admin panel    


class RegisterFace(models.Model):
    # Fields for the user face model
    name = models.CharField(max_length=100)
    face_image = models.ImageField(upload_to='user_faces/')
    email = models.EmailField(primary_key=True,default=False)  # Email as the primary key
    mobile_number = models.CharField(max_length=15, unique=True,default=False)  # Mobile number should be unique
    address = models.TextField(default= False)  # Address field for storing the user's address
    department_id = models.IntegerField(default=False)  # Assuming department_id is an integer reference
    access = models.BooleanField(default=False)  # Boolean field indicating access rights

    def __str__(self):
        return f"{self.name} - {self.email}"


