from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('patients/', views.PatientListView.as_view(), name='patients'),
    path('patient/create', views.PatientCreate.as_view(), name='patient-create'),
    path('patient/<int:pk>', views.PatientDetailView.as_view(), name='patient-detail'),
    path('patient/<int:pk>/update', views.PatientUpdateView.as_view(), name='patient-update'),
    path('patient/<int:pk>/delete', views.PatientDeleteView.as_view(), name='patient-delete'),
    path('patientbreasts/', views.PatientBreastListView.as_view(), name='patientbreasts'),
    path('patientbreast/create', views.PatientBreastCreate.as_view(), name='patientbreast-create'),
    path('patientbreast/<int:pk>', views.PatientBreastDetailView.as_view(), name='patientbreast-detail'),
    path('patientbreast/<int:pk>/update', views.PatientBreastUpdateView.as_view(), name='patientbreast-change'),
    path('patientbreast/<int:pk>/delete', views.PatientBreastDeleteView.as_view(), name='patientbreast-delete'),
    path('patientbreast/<int:pk>/predict', views.predict, name='predict'),
    path('patientbreast/<int:pk>/segment', views.segment, name='segment'),
]