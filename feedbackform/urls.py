from django.urls import path,re_path
from . import views

urlpatterns = [
    path('getFeedbackForms',views.getFeedbackForms),
    path('getFilledFeedbackForms',views.getFilledFeedbackForms),
    path('getUnfilledFeedbackForms',views.getUnfilledFeedbackForms),
    path('createFeedbackForm',views.createFeedbackForm),
    path('updateFeedbackForm',views.updateFeedbackForm),
    path('deleteFeedbackForm',views.deleteFeedbackForm),
]