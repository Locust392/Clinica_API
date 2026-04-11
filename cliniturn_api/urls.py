from django.contrib import admin
from django.urls import path
from cliniturn_api.views import bootstrap
from cliniturn_api.views import auth
from cliniturn_api.views import users
from cliniturn_api.views import doctors
from cliniturn_api.views import patients
from cliniturn_api.views import specialties
from cliniturn_api.views import appointments
from cliniturn_api.views import records
from cliniturn_api.views import reports
from cliniturn_api.views import consultorios

urlpatterns = [
    # Version
    path('bootstrap/version', bootstrap.VersionView.as_view()),
    path("profile/", users.ProfileView.as_view()),

    # Login / Logout
    path('token/', auth.CustomAuthToken.as_view()),
    path('logout/', auth.Logout.as_view()),

    # Admin
    path('admin/', users.AdminView.as_view()),
    path('lista-admins/', users.AdminAll.as_view()),
    path('admins-edit/', users.AdminsViewEdit.as_view()),

    # Médicos
    path('doctors/', doctors.DoctorsView.as_view()),
    path('lista-medicos/', doctors.DoctorsAll.as_view()),
    path('doctors-edit/', doctors.DoctorsViewEdit.as_view()),
    path('doctors/change-status/', doctors.DoctorsChangeStatusView.as_view()),

    # Pacientes
    path('patients/', patients.PatientsView.as_view()),
    path('lista-pacientes/', patients.PatientsAll.as_view()),
    path('patients-edit/', patients.PatientsViewEdit.as_view()),
    path('patients/change-status/', patients.PatientsChangeStatusView.as_view()),

    # Especialidades
    path('specialties/', specialties.SpecialtiesView.as_view()),
    path('lista-especialidades/', specialties.SpecialtiesAll.as_view()),
    path('specialties-edit/', specialties.SpecialtiesViewEdit.as_view()),
    path('specialties/change-status/', specialties.SpecialtyChangeStatusView.as_view()),

    # Citas
    path('appointments/', appointments.AppointmentsView.as_view()),
    path('lista-appointments/', appointments.AppointmentsView.as_view()),
    path('appointments-confirm/', appointments.AppointmentConfirmView.as_view()),
    path('appointments-cancel/', appointments.AppointmentCancelView.as_view()),
    path('appointments-edit/', appointments.AppointmentsView.as_view()),
    path("stats/appointments-by-specialty/", appointments.AppointmentsBySpecialtyView.as_view()),


    # Expedientes 
    path('records/', records.RecordsListView.as_view()),
    path('record/', records.RecordDetailView.as_view()),
    path('records-download/', records.RecordDownloadView.as_view()),

    # Reportes 
    path('reports-summary/', reports.ReportsSummaryView.as_view()),
    path('reports-kpis/', reports.ReportsKpisView.as_view()),
    
    #Colsutorio
    path('consultorios/all/', consultorios.ConsultoriosAll.as_view()),
    path('consultorios/', consultorios.ConsultoriosView.as_view()),
    path('consultorios/edit/', consultorios.ConsultoriosViewEdit.as_view()),
    path('consultorios/change-status/', consultorios.ConsultoriosChangeStatusView.as_view()),
]
