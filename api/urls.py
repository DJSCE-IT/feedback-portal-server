from django.urls import path,re_path
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    # path('api/subjects/',include()),
    # path('api/getBatchSap/<int:year>/<str:batch_name>',views.getBatchSap),
    # path('api/getSubjects',views.getSubjects),
     
    #path('api/storeFeedbackForm',views.storeFeedbackForm),
    #path('api/getFeedbackFormForStudent',views.getFeedbackFormForStudent),
    #path('api/getAliveFeedbackForms',views.getAliveFeedbackForm),
    #path('api/getExpiredFeedbackForms',views.getExpiredFeedbackForm),
    #path('api/updateAliveStatus',views.updateAliveStatus),
    #path('api/submitFeedbackByStudent',views.submitFeedbackByStudent),
    #path('api/addTheorySubject',views.addTheorySubject),
    #path('api/addPractical',views.addPracticalSubject),
    #path('api/getStudentSubmissionCount',views.getStudentSubmissionCount),
    #path('api/createSuperAdmin',views.createSuperAdmin),


    
    #  Final working:
    path('api/sendOtp',views.sendOtp),
    path('api/verifyOtp',views.verifyOtp),
    path('api/createTeacher',views.createTeacher),
    path('api/resetPasswordMail',views.resetPasswordMail),
    path('api/getPass',views.getPass),
    path('api/resetPassword',views.resetPassword),
    path('api/getAllTeacherMails',views.getAllStaffEmails),
    path('api/saveFeedbackFormResult',views.saveFeedbackFormResult),
    path('api/getSDashData',views.getSDashData), #/tSubject GET req
    path('api/getSDashDataFilled',views.getSDashDataFilled), #/tSubject GET req
    path('api/getSDashDataForm',views.getSDashDataForm), #/tSubject GET req per form
    path('api/gettUsersBac/<str:username>',views.getTUsers), #/tSubject GET req
    path('api/gettUsers/<str:username>',views.getTUsers1), #/tSubject GET req
    path('api/getFeedbackForm',views.getFeedbackForm),
    path('api/getFeedbackData',views.getFeedbackData),
    path('api/sendReminder',views.sendReminder),
    path('api/getProfile',views.getProfile),
    path('api/saveProfile',views.saveProfile),
    path('api/bac',views.bac),
    path('api/bacUpdate',views.bacUpdate),
    path('api/getuserslist',views.getuserslist),
    path('api/delBatch',views.delBatch),
    path('api/tSettings',views.tsettings),
    #path('api/addToBatch',views.addToBatch),
    path('api/getBatches',views.getBatches), #/tBatch GET req
    path('api/login',views.login),
    path('api/createFeedbackForm',views.createFeedbackForm),
    path('api/updateFeedbackform',views.updateFeedbackform),
    path('api/getYrBatches',views.getYrBatches),
    path('api/getYearBatches',views.getYearBatches),
    path('api/deleteFeedbackform',views.deleteFeedbackform),
    path('api/createNewInst',views.createNewInst),
    path('api/generateSecretCode',views.generateSecretCode),
    #path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/getallsubjects", views.get_all_subjects),
    path("api/deletesubject/<int:subject_id>/", views.delete_subject, name="delete_subject"),
    path("",views.welcomeView),
    path("api/test",views.test),
]