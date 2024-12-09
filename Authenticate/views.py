import base64
from io import BytesIO
import json
import random
import cv2
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.contrib import messages
import face_recognition
import numpy as np
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UserTab
from .models import Department
from .models import RegisterFace
from .serializers import RegisterFaceSerializer, UserTabSerializer
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from PIL import Image

class RegisterFaceView(APIView):
    def post(self, request, *args, **kwargs):
        return Response({"message": "Face registered successfully!"})

# Generate and send OTP email
def request_otp_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        
        # Generate a random 6-digit OTP
        otp = random.randint(100000, 999999) 
        
        # Store OTP in session
        request.session['otp'] = otp
        request.session['email'] = email
        
        # Send OTP via email
        send_mail(
            subject='Your OTP Verification Code',
            message=f'Your OTP is: {otp}',
            from_email='spinnyds2021@gmail.com',
            recipient_list=[email],
            fail_silently=False,
        )
        messages.success(request, f"OTP sent to {email}")
        return redirect('verify_otp')
    
    return render(request, 'otp_request.html')

# Verify OTP
def verify_otp_view(request):
    if request.method == "POST":
        entered_otp = request.POST.get('otp')
        session_otp = str(request.session.get('otp'))  # Retrieve OTP from session
        
        # Check if OTP matches
        if entered_otp == session_otp:
            # OTP is correct, clear it from session
            request.session.pop('otp', None)
            request.session.pop('email', None)
            return HttpResponse("OTP verified successfully!")
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect('verify_otp')
    
    return render(request, 'otp_verify.html')

@csrf_exempt
def register_face(request):
    if request.method == 'POST':
        # Extract the form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        department_id = 10
        address = request.POST.get('address')
        phone_number = request.POST.get('phone')
        face_data = request.POST.get('faceData')

        # Convert the base64 image data to an image
        if face_data:
            format, imgstr = face_data.split(';base64,')
            ext = format.split('/')[-1]
            image = Image.open(BytesIO(base64.b64decode(imgstr)))

            # Save the image to a file
            image_path = f'user_faces/{name.replace(" ", "_")}.{ext}'
            image.save(image_path)

            # Create and save the RegisterFace instance
            RegisterFace.objects.create(
                name=name,
                email=email,
                department_id=department_id,  # This now takes the correct ID
                address=address,
                mobile_number=phone_number,
                face_image=image_path
            )

            return JsonResponse({'message': 'Registration successful!'}, status=201)
        else:
            return JsonResponse({'error': 'No face data provided!'}, status=400)

    # Pass departments to the template for rendering
    departments = Department.objects.all()
    return render(request, 'capture.html', {'departments': departments})

def authenticate_face(request):
    if request.method == "POST":
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            image_data = data.get("image")
            if not image_data:
                return JsonResponse({"status": "error", "message": "No image data provided."})

            # Decode the Base64 image
            image_data = image_data.split(",")[1]  # Remove the data URI prefix
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            image_np = np.array(image)

            # Encode the captured frame
            try:
                captured_encoding = face_recognition.face_encodings(image_np)[0]
            except IndexError:
                return JsonResponse({"status": "error", "message": "No face detected in the captured image."})

            # Iterate through registered faces in the database
            registered_faces = RegisterFace.objects.all()
            for user_face in registered_faces:
                # Load and encode the stored image
                registered_image_path = user_face.face_image.path
                registered_image = face_recognition.load_image_file(registered_image_path)
                registered_encoding = face_recognition.face_encodings(registered_image)[0]

                # Compare the captured encoding with registered encoding
                matches = face_recognition.compare_faces([registered_encoding], captured_encoding)
                if True in matches:
                    return JsonResponse({"status": "success", "name": user_face.name})

            return JsonResponse({"status": "error", "message": "Face not recognized."})

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON payload."})

    # Render the face_authenticate.html template for GET requests
    return render(request, 'face_authenticate.html')

@csrf_exempt
@api_view(['GET', 'POST'])
def create_user(request):
    """
    Handle GET and POST requests:
    - GET: Render the user.html file
    - POST: Create a new user and return a JSON response
    """
    if request.method == 'POST':
        # Extract data from the request
        serial = request.data.get('serial')
        name = request.data.get('name')
        email = request.data.get('email')
        department_id = request.data.get('department_id')
        access = request.data.get('access')

        try:
            # Try to create the user
            UserTab.objects.create(
                serial=serial,
                name=name,
                email=email,
                department_id=department_id,
                access=access
            )
            return Response({'message': 'User created successfully!'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Handle UNIQUE constraint error
            if 'UNIQUE constraint failed' in str(e):
                return Response({'error': 'A user with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
            # Handle other exceptions
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # If the request is GET, render the user.html template
    return render(request, 'user.html')


@csrf_exempt  # Disable CSRF protection for simplicity
@api_view(['GET', 'POST'])  # Handle both GET and POST requests
def create_department(request):
    """
    Handle GET and POST requests:
    - GET: Render the create_department.html file
    - POST: Create a new department and return a JSON response
    """
    if request.method == 'GET':
        # Render the HTML form for creating a department
        return render(request, 'create_department.html')

    if request.method == 'POST':
        try:
            # Extract data from the request
            department_id = request.data.get('department_id')
            department_name = request.data.get('department_name')
            key = request.data.get('key')

            # Check if department_id is unique (if needed)
            if Department.objects.filter(department_id=department_id).exists():
                return Response(
                    {'error': 'Department ID already exists.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create a new department record
            department = Department.objects.create(
                department_id=department_id,
                department_name=department_name,
                key=key
            )

            return Response(
                {
                    'message': 'Department created successfully!',
                    'department': {
                        'department_id': department.department_id,
                        'department_name': department.department_name,
                        'key': department.key,
                    }
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        

class RegisterFaceListView(APIView):
    def get(self, request):
        register_faces = RegisterFace.objects.all()
        serializer = RegisterFaceSerializer(register_faces, many=True)
        return Response(serializer.data)  

class RegisterFaceByEmailView(APIView):
    def post(self, request):
        email = request.data.get('email', None)  # Get email from the request body
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            register_face = RegisterFace.objects.get(email=email)
            serializer = RegisterFaceSerializer(register_face)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except RegisterFace.DoesNotExist:
            return Response({"error": "Record not found."}, status=status.HTTP_404_NOT_FOUND)

class UpdateRegisterFaceView(APIView):
    def put(self, request):
        email = request.data.get('email', None)  # Email is required to identify the record
        
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Fetch the user by email
        try:
            register_face = RegisterFace.objects.get(email=email)
        except RegisterFace.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Update fields if provided in the request body
        fields_to_update = ['name', 'mobile_number', 'address', 'department_id', 'access']
        updated_fields = {}
        
        for field in fields_to_update:
            if field in request.data:
                setattr(register_face, field, request.data[field])
                updated_fields[field] = request.data[field]
        
        # Save the updated instance
        register_face.save()
        
        return Response({
            "message": "User details updated successfully.",
            "updated_fields": updated_fields
        }, status=status.HTTP_200_OK)
       

        
def default_view(request):
    return render(request,"hello.html")
