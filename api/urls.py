from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter  # 🚦 DRF tool that auto-generates URL patterns for ViewSets

"""
Think of this file as the “address book” of your API.
Each path here tells Django:
'When someone visits THIS URL, send them to THAT view.'
"""

# ============================================================
# 📦 Router Setup (For ViewSets)
# ============================================================
# A Router is like a “smart delivery manager”:
# Instead of you manually defining every CRUD route for a ViewSet,
# it automatically creates routes for:
#   - list (GET all)
#   - retrieve (GET one)
#   - create (POST)
#   - update/partial_update (PUT/PATCH)
#   - destroy (DELETE)
#
# Example:
# If we register an 'employees' ViewSet here,
# it will give us URLs like:
#   GET     /employees/        → List all employees
#   POST    /employees/        → Add new employee
#   GET     /employees/1/      → Get employee with ID 1
#   PUT     /employees/1/      → Update employee with ID 1
#   DELETE  /employees/1/      → Remove employee with ID 1
#

router = DefaultRouter()  # Create the Router object
router.register(
    'employees',                 # URL prefix
    views.EmployeeViewset,       # ViewSet to handle logic
    basename='employee'          # Required when ViewSet has no queryset attribute
)

# ============================================================
# 📜 URL Patterns
# ============================================================
urlpatterns = [
    # ============================================================
    # 📚 Function-Based Views (Commented Out)
    # ============================================================
    # path('students', views.studentsView),  
    #     → GET all students, or POST a new one.
    # path('students/<int:pk>/', views.studentDetailView),
    #     → GET, UPDATE, or DELETE a specific student.

    # ============================================================
    # 🏛 Class-Based Views (APIViews) - Commented Out
    # ============================================================
    # path('employees/', views.Employees.as_view()),
    #     → Handles listing & creating employees.
    # path('employees/<int:pk>/', views.EmployeeDetail.as_view()),
    #     → Handles retrieving, updating, deleting a specific employee.

    # ============================================================
    # 🤖 ViewSets with Routers (Active)
    # ============================================================
    path('', include(router.urls)),  
    # Includes all automatically generated employee routes from the router.

    # ============================================================
    # 📝 Blog Endpoints
    # ============================================================
    path('blogs/', views.BlogsView.as_view()),  
    # GET all blogs or POST a new blog (like your Medium dashboard)

    path('blogs/<int:pk>/', views.BlogDetailView.as_view()),  
    # GET, PUT, DELETE one specific blog (by ID)

    # ============================================================
    # 💬 Comment Endpoints
    # ============================================================
    path('comments/', views.CommentsView.as_view()),  
    # GET all comments or POST a new one

    path('comments/<int:pk>/', views.CommentDetailView.as_view()),  
    # GET, PUT, DELETE one specific comment (by ID)
]
