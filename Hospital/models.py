from django.db import models
from django.urls import reverse
from django.db.models import query
from django.db.models.base import Model
from django.db.models.deletion import CASCADE
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator,RegexValidator

# Create your models here.


class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    ic_pp=models.CharField(verbose_name=('IC/Passport No.'),max_length=12,unique=True, validators=[MinLengthValidator(9)])
    date_of_birth = models.DateField(null=True, blank=True)
    residential_address = models.CharField(null=True, blank=True, max_length=100)
    postal_address = models.CharField(null=True, blank=True, max_length=100)
    email_address = models.EmailField(null=True, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,12}$',message="Phone number must be entered in the format: '+999999999'. Up to 12 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=12, blank=True,null=True)
    ethinicity_choices = (
        ('African','African'),
        ('American','American'),
        ('European','European'),
        ('Asian','Asian'),
    )
    ethnicity = models.CharField(max_length=10, choices=ethinicity_choices, )

    class Meta:
        ordering = ['first_name', 'last_name']

    def get_absolute_url(self):
        """Returns the url to access a detail record for this patient."""
        return reverse('patient-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.first_name} {self.last_name}--Ic/PP: {self.ic_pp}'


class PatientBreast(models.Model):
    Patient = models.ForeignKey('Patient', on_delete=models.CASCADE, null=True)
    Breast_Img = models.ImageField(upload_to='Hospital/BreastImages/')
    BREAST_SIDE=(
        ('L','Left'),
        ('R','Right'))
    VIEW_TYPE = (
        ('MLO', 'Mediolateral Oblique'),
        ('CC', 'Craniocaudal'),)
    BreastSide = models.CharField(max_length=1,choices=BREAST_SIDE,blank=True,default='L')
    ViewType = models.CharField(max_length=3,choices=VIEW_TYPE,blank=True,default='MLO')
    Density = models.IntegerField(choices=((1,'1'),(2,'2'),(3,'3'),(4,'4'),(5,'5')), blank=False,default=1)
    DateTaken=models.DateTimeField(auto_now_add=True, null=True)
    prediction=models.CharField(max_length=10,blank=True)
    predicted_img = models.ImageField(upload_to='Hospital/BreastImages/',null=True)
    seg_results=models.CharField(max_length=20,blank=True,null=True)

    class Meta:
        ordering = ['Patient', 'DateTaken']

    def get_absolute_url(self):
        """Returns the url to access a detail record for this PatientBreast."""
        return reverse('patientbreast-detail', args=[str(self.id)])

    def getBreastImageByID(id):
        return PatientBreast.objects.filter(PatientBreast.id==id)

    def __str__(self):
        """String for representing the Model object."""

        return f'{self.id},{self.DateTaken.strftime("%B %d %Y")},{self.Patient}'