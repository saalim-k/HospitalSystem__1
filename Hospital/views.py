#imports
import PIL.Image
from django.shortcuts import render
from .models import Patient,PatientBreast#,DeepLearningModels
from django.views import generic
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.views import View
from django.views.generic.edit import UpdateView
from django.urls import reverse
from django.urls import reverse_lazy
from tensorflow.keras.models import load_model
from django.shortcuts import get_object_or_404
import cv2
import numpy as np
import os
import segmentation_models as sm
from PIL import Image
import matplotlib.pyplot as plt
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

#global variables
BaseImageDir='C:/Users/moham/Desktop/HospitalSystem/'
segModel = load_model('C:/Users/moham/Desktop/MyDeepLearningProject/resnet34-usingIOU-1632716594.h5',compile=False)
predModel = load_model('C:/Users/moham/Desktop/MyDeepLearningProject/ModelCheckPoints/2BinaryNormCanc-64-32-2.h5',compile=False)

# Create your views here.

@login_required(login_url='/accounts/login/')
def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_patients = Patient.objects.all().count()
    num_mammograms=PatientBreast.objects.all().count()
    patients=Patient.objects.all()
    patientbreasts=PatientBreast.objects.all()
    num_visits = request.session.get('num_visits', 0)
    userId= request.session.get('user_id')
    request.session['num_visits'] = num_visits + 1
    context = {
        'num_visits': num_visits,
        'num_patients': num_patients,
        'userId':userId,
        'patients':patients,
        'patientbreasts':patientbreasts,
        'num_mammograms':num_mammograms,
    }
    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class PatientListView(LoginRequiredMixin,generic.ListView):
    model = Patient
    fields = '__all__'
    paginate_by = 5

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query is not None:
            object_list = Patient.objects.filter(ic_pp__contains=query)
            return object_list
        else:
            object_list=Patient.objects.all()
            return object_list


class PatientDetailView(LoginRequiredMixin,generic.DetailView):
    model = Patient

class PatientCreate(LoginRequiredMixin,generic.CreateView,SuccessMessageMixin):
    model=Patient
    fields = '__all__'
    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super(PatientCreate, self).get_form(form_class)
        form.fields['first_name'].widget.attrs ={'placeholder': 'David'}
        form.fields['last_name'].widget.attrs = {'placeholder': 'Bautista'}
        form.fields['ic_pp'].widget.attrs = {'placeholder': '123456789'}
        form.fields['date_of_birth'].widget.attrs = {'placeholder': '01/21/2000'}
        form.fields['residential_address'].widget.attrs = {'placeholder': 'Starz Valley'}
        form.fields['postal_address'].widget.attrs = {'placeholder': '71800'}
        form.fields['email_address'].widget.attrs = {'placeholder': 'daveB@abc.com'}
        form.fields['phone_number'].widget.attrs = {'placeholder': '+60111111111'}
        return form
    success_message = "%(first_name)s was created successfully"

class PatientUpdateView(LoginRequiredMixin,generic.UpdateView):
    model=Patient
    fields = '__all__'

class PatientDeleteView(LoginRequiredMixin,generic.DeleteView):
    model=Patient
    fields='__all__'
    success_url = reverse_lazy('patients')

class PatientBreastListView(LoginRequiredMixin,generic.ListView):
    model = PatientBreast
    paginate_by = 5

    def get_queryset(self):
        query = self.request.GET.get('r')
        if query is not None:
            object_list = PatientBreast.objects.filter(Patient__ic_pp__contains=query)
            return object_list
        else:
            object_list=PatientBreast.objects.all()
            return object_list

class PatientBreastCreate(LoginRequiredMixin,generic.CreateView):
    login_required = True
    model=PatientBreast
    fields = ['Patient','Breast_Img','BreastSide','ViewType','Density']

class PatientBreastDetailView(LoginRequiredMixin,generic.DetailView):
    model=PatientBreast

class PatientBreastUpdateView(LoginRequiredMixin,generic.UpdateView):
    model = PatientBreast
    fields= ['Patient','Breast_Img','BreastSide','ViewType','Density']

class PatientBreastDeleteView(LoginRequiredMixin,generic.DeleteView):
    model=PatientBreast
    fields='__all__'
    success_url = reverse_lazy('patientbreasts')

@login_required(login_url='/accounts/login/')
def predict(request,pk):
    patientbreast=PatientBreast.objects.get(pk=pk)
    myurl=patientbreast.Breast_Img.url
    img_array = cv2.imread(BaseImageDir + myurl)
    img_array_resized = cv2.resize(img_array, (250, 250))
    img_array_resized = np.array(img_array_resized)
    img_array_resized = np.expand_dims(img_array_resized, axis=0)
    prediction = predModel.predict(img_array_resized)
    prediction = np.argmax(prediction)
    if prediction==1:
        PatientBreast.objects.filter(pk=pk).update(prediction='Benign or Cancer')
    else:
        PatientBreast.objects.filter(pk=pk).update(prediction='Normal')
    patientbreast=PatientBreast.objects.get(pk=pk)
    context={'patientbreast':patientbreast,
             'prediction':prediction}
    return render(request, 'Hospital/patientbreast_detail.html', context=context)

@login_required(login_url='/accounts/login/')
def segment(request,pk):
    patientbreast=PatientBreast.objects.get(pk=pk)
    preprocess_input = sm.get_preprocessing('resnet34')
    myurl=patientbreast.Breast_Img.url
    img_array = cv2.imread(BaseImageDir + myurl)
    img_array_resized = cv2.resize(img_array, (512, 512))
    img_array_resized = np.expand_dims(img_array_resized, 0)
    img_array_resized = np.array(img_array_resized)
    img_array_resized=img_array_resized/255.0
    img_array_resized=preprocess_input(img_array_resized)
    prediction = segModel.predict(img_array_resized)
    predicted_img=np.argmax(prediction,axis=3)[0,:,:]
    predlabels=np.unique(predicted_img)
    print(str(predlabels))
    if str(predlabels)=='[0 1]':
        seg_res='Normal'
        PatientBreast.objects.filter(pk=pk).update(seg_results=seg_res)
    elif str(predlabels)=='[0 1 2]':
        seg_res="Benign"
        PatientBreast.objects.filter(pk=pk).update(seg_results=seg_res)
    elif str(predlabels)=='[0 1 3]':
        seg_res='Cancer'
        PatientBreast.objects.filter(pk=pk).update(seg_results=seg_res)
    else:
        seg_res='Unidentified'
        PatientBreast.objects.filter(pk=pk).update(seg_results=seg_res)
    predictedUrl=f'{myurl[1:-4]}_predicted.png'
    pred_image=plt.imsave(predictedUrl,predicted_img,cmap='gray')
    PatientBreast.objects.filter(pk=pk).update(predicted_img=predictedUrl[6:],seg_results=seg_res)
    patientbreast=PatientBreast.objects.get(pk=pk)
    context={'patientbreast':patientbreast,
             'prediction':prediction,
             'predicted_img':predicted_img,}
    return render(request, 'Hospital/patientbreast_detail.html', context=context)