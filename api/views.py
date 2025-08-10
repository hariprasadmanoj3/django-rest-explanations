from django.shortcuts import render, get_object_or_404
# from django.http import JsonResponse
from students.models import Student
from .serializers import StudentSerializer, EmployeeSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from employees.models import Employee
from django.http import Http404
from rest_framework import mixins, generics, viewsets
from blogs.models import Blog, Comment
from blogs.serializers import BlogSerializer, CommentSerializer
from .paginations import CustomPagination

# ------------------------------------------------------------------------------
# api/views.py — a compact DRF learning reference + working views
# ------------------------------------------------------------------------------

# This file intentionally contains:
# 1) multiple approaches shown (Function-Based Views, Class-Based Views, Mixins,
#    Generics, ViewSets) kept as commented examples for learning,
# 2) the actual working endpoints used by the project.
#
# Why keep all approaches? They teach progression:
# - FBVs are the most explicit (great for understanding request flow)
# - APIView is the class-based version (organizes HTTP methods into a class)
# - Mixins / GenericAPIView reduce boilerplate
# - Generics are higher-level pre-built views
# - ViewSets + Routers are the most compact — great for production
#
# Real-life analogies woven into comments:
# - Think "Student" as rows in a school's Excel sheet
# - Think "Employee" as records in an HR app dashboard (list, add, edit, delete)
# - Think "Blog + Comment" as an article with its comment threads
#
# Read top-to-bottom: the commented-out blocks are intentionally preserved
# as an on-file learning guide. The active classes at the bottom are the
# actual implementation shipped with your project.
#
# Tip: When revisiting this file, treat it like a chapter of a textbook —
# scan headings (FBV → CBV → Mixins → Generics → ViewSets → Pagination).
#
# ------------------------------------------------------------------------------


##########################################################
# 1️⃣  FUNCTION-BASED VIEWS (FBVs) - Most explicit form
##########################################################
# Concept summary:
# - FBVs are plain Python functions decorated to accept HTTP methods.
# - Best when: you want total control and to learn every step (serializing,
#   validation, response codes).
# Real-life analogy:
# - Imagine a waiter (function) directly taking a customer's order (HTTP request),
#   going to the kitchen (database/ORM), and bringing back the response (JSON).
#
# Below: two commented examples demonstrating:
#  - listing & creating Students (GET/POST)
#  - retrieving/updating/deleting a single Student (GET/PUT/DELETE)
#
# Keep these around as an explicit reference for the full request → response flow.

# @api_view(['GET', 'POST'])  # Allowed HTTP methods for this function
# def studentsView(request):
#     """
#     GET /students/  -> return a list of students
#     POST /students/ -> create a student from request.data
#
#     Explanation:
#     - Student.objects.all() returns a QuerySet (like a DB cursor).
#     - StudentSerializer(..., many=True) converts QuerySet → JSON-ready list.
#     - serializer.is_valid() performs validation defined in serializer.
#     """
#     if request.method == 'GET':
#         students = Student.objects.all()  # Lazy QuerySet for all students
#         serializer = StudentSerializer(students, many=True)  # convert to JSON-able
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     elif request.method == 'POST':
#         serializer = StudentSerializer(data=request.data)  # incoming JSON -> serializer
#         if serializer.is_valid():
#             serializer.save()  # create Student object in DB
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         print(serializer.errors)  # helpful while developing
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(['GET', 'PUT', 'DELETE'])
# def studentDetailView(request, pk):
#     """
#     GET /students/{pk}/    -> return single student
#     PUT /students/{pk}/    -> update student
#     DELETE /students/{pk}/ -> remove student
#
#     Notes:
#     - This pattern manually handles lookup, errors, validation and responses.
#     - Use it when you want to see the explicit steps (good for learning).
#     """
#     try:
#         student = Student.objects.get(pk=pk)
#     except Student.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#
#     if request.method == 'GET':
#         serializer = StudentSerializer(student)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     elif request.method == 'PUT':
#         serializer = StudentSerializer(student, data=request.data)  # pre-populate + incoming
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     elif request.method == 'DELETE':
#         student.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


##########################################################
# 2️⃣  CLASS-BASED VIEWS (APIView) — organized handlers
##########################################################
# Concept summary:
# - APIView groups HTTP-method handlers (get, post, put ...) into a class.
# - Slightly more structured than FBVs and a stepping stone to generics.
# Real-life analogy:
# - Imagine a receptionist box with labeled slots for each action:
#   GET slot, POST slot, PUT slot — each slot has its handler method.
#
# Below: example classes (commented) that show the same functionality
# as the FBVs above but arranged as class methods.

# class Employees(APIView):
#     """
#     Example: APIView-based list/create for Employee.
#     GET  -> list employees
#     POST -> create an employee
#
#     This shows:
#     - How to place logic for each HTTP verb into one class,
#     - Cleaner than FBV when handling many HTTP verbs.
#     """
#     def get(self, request):
#         employees = Employee.objects.all()
#         serializer = EmployeeSerializer(employees, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     def post(self, request):
#         serializer = EmployeeSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class EmployeeDetail(APIView):
#     """
#     APIView-based single-object operations:
#     - get_object is a helper to fetch the DB row or raise 404
#     - get/put/delete: naturally map to read/update/delete
#     """
#     def get_object(self, pk):
#         try:
#             return Employee.objects.get(pk=pk)
#         except Employee.DoesNotExist:
#             raise Http404
#
#     def get(self, request, pk):
#         employee = self.get_object(pk)
#         serializer = EmployeeSerializer(employee)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     def put(self, request, pk):
#         employee = self.get_object(pk)
#         serializer = EmployeeSerializer(employee, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk):
#         employee = self.get_object(pk)
#         employee.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


##########################################################
# 3️⃣  MIXINS + GenericAPIView — reusable building blocks
##########################################################
# Concept summary:
# - Mixins are small classes that give a single capability:
#   ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
# - GenericAPIView provides the infrastructure (queryset, serializer_class)
# - Combine them to get repeatable CRUD behaviors with less boilerplate
#
# Real-life analogy:
# - Mixins are like small kitchen appliances: the blender (list), the mixer (create).
# - You assemble the tools you need for a recipe (view).
#
# Below: examples using ListModelMixin/CreateModelMixin (for listing + creating)
# and RetrieveModelMixin/UpdateModelMixin/DestroyModelMixin (for single-object ops).

# class Employees(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
#     """
#     Equivalent to GET (list) and POST (create) but using mixins:
#     - list() comes from ListModelMixin
#     - create() comes from CreateModelMixin
#     """
#     queryset = Employee.objects.all()
#     serializer_class = EmployeeSerializer
#
#     def get(self, request):
#         return self.list(request)  # ListModelMixin provides `.list`
#
#     def post(self, request):
#         return self.create(request)  # CreateModelMixin provides `.create`
#
#
# class EmployeeDetail(mixins.RetrieveModelMixin,
#                      mixins.UpdateModelMixin,
#                      mixins.DestroyModelMixin,
#                      generics.GenericAPIView):
#     """
#     Retrieve + Update + Destroy combined via mixins.
#     Very little code — mixins provide the real implementations.
#     """
#     queryset = Employee.objects.all()
#     serializer_class = EmployeeSerializer
#
#     def get(self, request, pk):
#         return self.retrieve(request, pk)  # RetrieveModelMixin
#
#     def put(self, request, pk):
#         return self.update(request, pk)  # UpdateModelMixin
#
#     def delete(self, request, pk):
#         return self.destroy(request, pk)  # DestroyModelMixin


##########################################################
# 4️⃣  GENERICS — high-level ready-made views
##########################################################
# Concept summary:
# - Generics are pre-bundled combinations of mixins + GenericAPIView.
# - Examples: ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, CreateAPIView etc.
# - Use them when you want concise code without hand-wiring mixins.
#
# Real-life analogy:
# - Generics are like pre-made meal kits: you get a full combo (list + create),
#   so you just need to specify the queryset and serializer.
#
# Examples (commented) below show how very compact a view becomes with generics.

# class Employees(generics.ListCreateAPIView):
#     """
#     ListCreateAPIView = list (GET) + create (POST)
#     Only need to provide queryset & serializer_class
#     """
#     queryset = Employee.objects.all()
#     serializer_class = EmployeeSerializer
#
#
# class EmployeeDetail(generics.RetrieveUpdateDestroyAPIView):
#     """
#     RetrieveUpdateDestroyAPIView = GET single + PUT/PATCH + DELETE
#     Provide queryset & serializer_class & optionally lookup_field
#     """
#     queryset = Employee.objects.all()
#     serializer_class = EmployeeSerializer
#     lookup_field = 'pk'  # default, but explicit is clearer for readers


##########################################################
# 5️⃣  VIEWSETS — compact, router-friendly endpoints
##########################################################
# Concept summary:
# - ViewSets group related view logic for a resource into a single class.
# - Two styles:
#    - viewsets.ViewSet  -> you implement methods like list/create/retrieve/update/destroy
#    - viewsets.ModelViewSet -> auto-implements standard CRUD if you set queryset & serializer
# - Routers map a ViewSet to multiple URL patterns automatically.
#
# Real-life analogy:
# - A ViewSet is like a multi-tool admin console: one object that handles list/add/edit/delete.
# - Router is the wiring behind a dashboard that exposes all those actions at neat URLs.
#
# Example: manual ViewSet (commented) shows how you'd write each action yourself.

# class EmployeeViewset(viewsets.ViewSet):
#     def list(self, request):
#         queryset = Employee.objects.all()
#         serializer = EmployeeSerializer(queryset, many=True)
#         return Response(serializer.data)
#
#     def create(self, request):
#         serializer = EmployeeSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors)
#
#     def retrieve(self, request, pk=None):
#         employee = get_object_or_404(Employee, pk=pk)
#         serializer = EmployeeSerializer(employee)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     def update(self, request, pk=None):
#         employee = get_object_or_404(Employee, pk=pk)
#         serializer = EmployeeSerializer(employee, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.data)
#
#     def delete(self, request, pk=None):
#         employee = get_object_or_404(Employee, pk=pk)
#         employee.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


##########################################################
# ------------------- ACTIVE WORKING VIEWS -------------------
# (These are the views your project currently uses)
##########################################################

# -----------------------------
# EMPLOYEE API (ModelViewSet)
# -----------------------------
# Why ModelViewSet?
# - Almost everything you need for a typical REST resource (list/retrieve/create/update/delete)
#   is already implemented for you if you supply `queryset` and `serializer_class`.
# - This is ideal for production: short, consistent, and works neatly with routers.
#
# Real-life: imagine an HR dashboard:
# - An admin can browse pages of employees (pagination),
# - filter by designation (filtering),
# - and open/edit a specific employee profile (retrieve + update).
class EmployeeViewset(viewsets.ModelViewSet):
    queryset = Employee.objects.all()              # the DB table we expose
    serializer_class = EmployeeSerializer          # how to convert to/from JSON
    pagination_class = CustomPagination            # custom per-view pagination
    filterset_fields = ['designation']             # simple filtering: ?designation=Manager


# -----------------------------
# BLOGS - list & create
# -----------------------------
# ListCreateAPIView: used for endpoints where you want both:
# - GET /blogs/  -> list all blogs
# - POST /blogs/ -> create a new blog
#
# Real-life: like a blog homepage (readers see posts) + a "new post" form for authors.
class BlogsView(generics.ListCreateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer


# -----------------------------
# COMMENTS - list & create
# -----------------------------
# Similar to BlogsView but for comments:
# - GET /comments/  -> list comments
# - POST /comments/ -> create a comment
#
# Real-life: the comment thread under a blog post or video.
class CommentsView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


# -----------------------------
# BLOG DETAIL - single object CRUD
# -----------------------------
# RetrieveUpdateDestroyAPIView handles:
# - GET  /blogs/{pk}/  -> read single blog (with nested comments, if serializer includes them)
# - PUT  /blogs/{pk}/  -> replace blog content
# - PATCH /blogs/{pk}/ -> partial update
# - DELETE /blogs/{pk}/ -> delete blog
#
# Real-life: opening a blog post page and editing/deleting from admin tools.
class BlogDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    lookup_field = 'pk'


# -----------------------------
# COMMENT DETAIL - single object CRUD
# -----------------------------
# Same CRUD behavior but for comments.
class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_field = 'pk'


# ------------------------------------------------------------------------------
# PAGINATION & FILTERING NOTES (short, practical)
# ------------------------------------------------------------------------------
# - Pagination: splits large result sets into pages (helps performance & UX).
#   You configured a CustomPagination class (see .paginations.py). That class
#   controls page size, next/previous links and the JSON structure returned.
#
# - filterset_fields = ['designation'] above enables simple field filtering:
#   e.g., GET /employees/?designation=Software%20Engineer
#
# - If you need more advanced filtering, implement django-filter FilterSet classes
#   and assign `filterset_class = MyFilter` on the view (or set a global default
#   in settings).
#
# ------------------------------------------------------------------------------
# Final tips (for future-you reading this file):
# ------------------------------------------------------------------------------
# - When debugging: curl or Postman is your friend. Try:
#     GET  /api/employees/
#     POST /api/employees/  (body JSON)
#     GET  /api/employees/{id}/
#     PUT  /api/employees/{id}/  (body JSON)
# - To inspect serializers/fields quickly: print(serializer.data) in a dev shell.
# - If you forget DRF specifics later:
#     1) FBV — explicit control (good for debugging)
#     2) APIView — class-based grouping
#     3) mixins + GenericAPIView — reusable building blocks
#     4) generics — compact ready-made views
#     5) viewsets + routers — best for production endpoints
#
# Keep this file as your "cheat-sheet" and living textbook — it's deliberately
# long so it teaches the API patterns in one place.
#
# ------------------------------------------------------------------------------
# End of file — api/views.py
# ------------------------------------------------------------------------------
