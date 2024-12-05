from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError,HttpResponseNotFound,JsonResponse
from api.models import Subject,SubjectTheory,SubjectPractical,FeedbackForm,FeedbackInstance
from api.serializers import UserTMTMSerializer,FeedbackUserConnector,FeedbackFormSerializer,FeedbackUserFConnectorSerializer
from rest_framework.parsers import JSONParser
from django.contrib.auth.models import User,auth
from django.views.decorators.csrf import csrf_exempt
from api.decorators import *
# Create your views here.
@teacher_auth
def getFeedbackForms(request):
    res_data_sub={}
    try:
        feedbackInst=FeedbackInstance.objects.get(is_selected__in=[True])
        
        if request.current_teacher.is_superuser==True:
            feedData=FeedbackFormSerializer(FeedbackForm.objects.filter(instance=feedbackInst),many=True).data
        else:
            feedData=FeedbackFormSerializer(FeedbackForm.objects.filter(teacher=request.current_teacher,instance=feedbackInst),many=True).data
        res_data_sub["feedData"]=feedData
        return JsonResponse({"status_code":200,"data":res_data_sub},safe=False)
    except Exception as e:
        return JsonResponse({"status_code":400,"status_msg":"Error Occurred, Feedback instance does not exists"},safe=False)

    
@basic_auth
def getFilledFeedbackForms(request):
    feedConn=[]
    try:
        feedInst=FeedbackInstance.objects.get(is_selected__in=[True])
        feedConn=FeedbackUserFConnectorSerializer(FeedbackUserConnector.objects.filter(student=request.current_user,form__instance=feedInst,is_filled__in=[True]),many=True).data
    except:
        feedConn=[]
        return JsonResponse({"status_code": 400,"status_msg":"Bad Request"}, safe=False)
    return JsonResponse({"feedData":feedConn}, safe=False)

@basic_auth
def getUnfilledFeedbackForms(request):
    try:
        feedInst=FeedbackInstance.objects.get(is_selected__in=[True])
        feedConn=FeedbackUserFConnectorSerializer(FeedbackUserConnector.objects.filter(student=request.current_user,form__instance=feedInst,is_filled__in=[False]),many=True).data
    except:
        feedConn=[]
        return JsonResponse({"status_code": 400,"status_msg":"Bad"}, safe=False)
    return JsonResponse({"feedData":feedConn}, safe=False)
@csrf_exempt
@teacher_auth
def createFeedbackForm(request):
        data = JSONParser().parse(request)['data']
        da=None
        try:
            feedbackInst=FeedbackInstance.objects.get(is_selected__in=[True])
            if data["isTheo"]:
                try:
                    sub=Subject.objects.get(id=data["subject_id"])
                    subType=SubjectTheory.objects.filter(subject=sub)
                    if subType.exists():
                        da=FeedbackForm(teacher=User.objects.get(username=data["username"].lower()),year=int(data["year"]),subject=sub,is_theory=True,due_date=data["due_data"],instance=feedbackInst)
                        da.save()
                        
                    else:
                        return JsonResponse({"error": "Theory Subject does not exists"}, safe=False)

                except Exception as e:
                    print(e)
                    return JsonResponse({"error": "Theory Subject does not exists"}, safe=False)
            elif not data["isTheo"]:
                try:
                    sub=Subject.objects.get(id=data["subject_id"])                    
                    subType=SubjectPractical.objects.filter(subject=sub)
                    
                    if subType.exists():
                        da=FeedbackForm(teacher=User.objects.get(username=data["username"].lower()),year=int(data["year"]),subject=sub,is_theory=False,due_date=data["due_data"],instance=feedbackInst)
                        da.save()
                    else:
                        return JsonResponse({"error": "Practical Subject does not exists"}, safe=False)

                        
                except Exception as e:
                    print(e)
                    return JsonResponse({"error": "Practical Subject does not exists"}, safe=False)
        except:
            return JsonResponse({"status_code": 400,"status_msg":"Create Feedback Instance First"}, safe=False)
        batchList=[]
        if da==None:
            return JsonResponse({"status_code": 400,"status_msg":"Error"}, safe=False)
        
        for x in subType:
            batchList.append(x.batch.batch_name)
            student_data = UserTMTMSerializer(x.batch.student_email_mtm, many=True).data
            existing_emails = [stud["email"].lower() for stud in student_data]

            existing_users = User.objects.filter(username__in=existing_emails)
            existing_user_emails = set(user.username for user in existing_users)

            feedback_instances = []
            for stud in student_data:
                if stud["email"].lower() in existing_user_emails:
                    feedback_inst = FeedbackUserConnector(student=existing_users.get(username=stud["email"].lower()), form=da)
                    feedback_instances.append(feedback_inst)

            FeedbackUserConnector.objects.bulk_create(feedback_instances)
        da.batch_list=batchList
        da.save() 
        return JsonResponse({"status_code": 200,"status_msg":"Success","data":FeedbackFormSerializer(da).data}, safe=False)
@csrf_exempt
@teacher_auth
def updateFeedbackForm(request):
    data = JSONParser().parse(request)['data']
    try:
        form=FeedbackForm.objects.get(id=data["form_id"])
        form.due_date=data["due_date"]
        form.save()
        return JsonResponse({"status_code":200,"status_msg": "Successfully UpdatedForm","data":FeedbackFormSerializer(form).data}, safe=False)
    except Exception as e:
        print(e)
        return JsonResponse({"status_code":400,"status_msg": "Error occurred while updating form"}, safe=False)
    
@csrf_exempt
@teacher_auth
def deleteFeedbackForm(request):
    data = JSONParser().parse(request)['data']
    try:
        form=FeedbackForm.objects.get(id=data["form_id"])
        form.delete()
        return JsonResponse({"status_code":200,"status_msg": "Successfully Deleted Form"}, safe=False)
    except:
        return JsonResponse({"status_code":400,"status_msg": "Error occurred while deleting form"}, safe=False)
