import os
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseServerError,
    HttpResponseNotFound,
)
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from api.models import *
from django.contrib.auth.hashers import make_password
from rest_framework.parsers import JSONParser
from .serializers import *
from django.contrib.auth.models import User, auth
from django.conf import settings
import pyotp
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from .decorators import basic_auth, superuser_auth, teacher_auth
from django.views.decorators.http import require_http_methods


import datetime
import string
import random


# Create your views here.


def checkAuthorization(auth):
    if auth != "null":
        get_token = auth.split(" ")[1]
        try:
            token = AccessToken(get_token)
            if token:
                return True
            else:
                return False
        except Exception:
            return False


@csrf_exempt
def sendReminder(request):
    if request.headers["Authorization"] and checkAuthorization(
        request.headers["Authorization"]
    ):
        if request.method == "POST":
            data = JSONParser().parse(request)["data"]
            try:
                form = FeedbackForm.objects.get(id=data["form_id"])
                feed = FeedbackUserConnector.objects.filter(
                    form=form, is_filled__in=[False]
                )
                emailList = []
                if feed.exists():
                    for stud in feed:
                        # link=f"http://localhost:3000/resetPassword/"+data["email"]+"/"+otp
                        emailList.append(stud.student.email)
                    subject = "REMINDER: Fill the feedback form - Feedback Portal"
                    email_from = settings.EMAIL_HOST_USER
                    msg = EmailMultiAlternatives(
                        subject=subject, from_email=email_from, to=emailList
                    )
                    args = {}
                    args["dj_logo"] = "{}".format(os.environ.get("DJ_LOGO"))
                    args["subject_name"] = "{}".format(form.subject.subject_name)
                    args["teacher_name"] = "{}".format(form.teacher.myuser.name)
                    if form.is_theory:
                        args["subject_type"] = "{}".format("Theory")
                    else:
                        args["subject_type"] = "{}".format("Practical")

                    args["url"] = "{0}/feedBackForm/{1}".format(
                        os.environ.get("FRONT_END_LINK"), data["form_id"]
                    )
                    args["mail"] = "{}".format(os.environ.get("EMAIL_HOST_USER"))
                    html_template = get_template("api/SendReminder.html").render(args)
                    msg.attach_alternative(html_template, "text/html")
                    msg.send()
                    return JsonResponse(
                        {"status_code": 200, "status_msg": "Success"}, safe=False
                    )
            except Exception as e:
                return JsonResponse(
                    {"status_code": 400, "status_msg": e.message}, safe=False
                )
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def saveFeedbackFormResult(request):
    if request.headers["Authorization"] and checkAuthorization(
        request.headers["Authorization"]
    ):
        if request.method == "POST":
            data = JSONParser().parse(request)["data"]
            # teacher = User.objects.filter(username=data['teacher_username'])
            try:
                student = User.objects.get(username=data["student_username"].lower())
                try:
                    feedform = FeedbackForm.objects.get(id=data["form_id"])
                    try:
                        feedformConn = FeedbackUserConnector.objects.get(
                            form=feedform, student=student
                        )
                        feedformConn.user_feedback = data["form_field"]
                        feedformConn.is_filled = True
                        feedformConn.save()
                        return JsonResponse(
                            {"status_code": 200, "status_msg": "Success"}, safe=False
                        )
                    except Exception as e:
                        print(e)
                        return JsonResponse(
                            {
                                "status_code": 505,
                                "status_msg": "Feedback form does not exists for the current user",
                            }
                        )

                except Exception as e:
                    print(e)
                    return JsonResponse(
                        {
                            "status_code": 505,
                            "status_msg": "Feedback form does not exists",
                        },
                        safe=False,
                    )
            except Exception as e:
                print(e)
                return JsonResponse(
                    {"status_code": 505, "status_msg": "User does not exists"},
                    safe=False,
                )
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def getSDashDataForm(request):
    if request.headers["Authorization"] and checkAuthorization(
        request.headers["Authorization"]
    ):
        if request.method == "GET":
            form_id = request.GET.get("form_id", "")
            user_id = request.GET.get("user_id", "")
            try:
                user = User.objects.get(username=user_id.lower())
                try:
                    feed = FeedbackForm.objects.get(id=form_id)
                    try:
                        feedInst = FeedbackUserConnector.objects.get(
                            student=user, form=feed
                        )
                        if feedInst.is_filled == True:
                            return JsonResponse(
                                {
                                    "status": 400,
                                    "status_msg": "Feedback form already filled",
                                },
                                safe=False,
                            )
                        sub = feed.subject.subject_name
                        teacher = feed.teacher.myuser.name
                        teacher_email = feed.teacher.email
                        date = feed.due_date
                        is_alive = feed.is_alive
                        is_theory = feed.is_theory
                        year = feed.year
                        subject_id = feed.subject.id
                        resData = {
                            "sub": sub,
                            "teacher": teacher,
                            "teacher_email": teacher_email,
                            "date": date,
                            "is_alive": is_alive,
                            "is_theory": is_theory,
                            "year": year,
                            "subject_id": subject_id,
                        }
                        return JsonResponse(
                            {"status": 200, "data": resData}, safe=False
                        )
                    except Exception as e:
                        print(e)
                        return JsonResponse(
                            {
                                "status": 400,
                                "status_msg": "You can not fill this form,you are not in this batch",
                            },
                            safe=False,
                        )
                except Exception as e:
                    print(e)
                    return JsonResponse(
                        {"status": 400, "status_msg": "Feedback Form does not exists"},
                        safe=False,
                    )
            except Exception as e:
                print(e)
                return JsonResponse(
                    {"status_code": 505, "status_msg": "User does not exists"},
                    safe=False,
                )
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def getSDashData(request):
    if request.headers["Authorization"] and checkAuthorization(
        request.headers["Authorization"]
    ):
        if request.method == "GET":
            username = request.GET.get("username", "")
            try:
                usr = User.objects.get(username=username.lower())
                try:
                    feedInst = FeedbackInstance.objects.get(is_selected__in=[True])
                    feedConn = FeedbackUserFConnectorSerializer(
                        FeedbackUserConnector.objects.filter(
                            student=usr, form__instance=feedInst, is_filled__in=[False]
                        ),
                        many=True,
                    ).data
                except:
                    feedConn = []
            except Exception as e:
                print(e)
                return JsonResponse(
                    {"status_code": 505, "status_msg": "User does not exists"},
                    safe=False,
                )
            return JsonResponse({"feedData": feedConn}, safe=False)
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def getSDashDataFilled(request):
    if request.headers["Authorization"] and checkAuthorization(
        request.headers["Authorization"]
    ):
        if request.method == "GET":
            username = request.GET.get("username", "")
            try:
                usr = User.objects.get(username=username.lower())
                try:
                    feedInst = FeedbackInstance.objects.get(is_selected__in=[True])
                    feedDataFilled = FeedbackUserFConnectorSerializer(
                        FeedbackUserConnector.objects.filter(
                            student=usr, form__instance=feedInst, is_filled__in=[True]
                        ),
                        many=True,
                    ).data
                except:
                    feedDataFilled = []
            except Exception as e:
                print(e)
                return JsonResponse(
                    {"status_code": 505, "status_msg": "User does not exists"},
                    safe=False,
                )
            return JsonResponse({"feedDataFilled": feedDataFilled}, safe=False)
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def delBatch(request):
    if request.headers["Authorization"] and checkAuthorization(
        request.headers["Authorization"]
    ):
        if request.method == "POST":
            data = JSONParser().parse(request)["data"]
            try:
                feedInst = FeedbackInstance.objects.get(is_selected__in=[True])
            except:
                return JsonResponse(
                    {
                        "status_code": 400,
                        "status_msg": "Create Feedback Instance First",
                    },
                    safe=False,
                )
            bac = Batch.objects.filter(
                batch_division=data["batch_division"],
                year=data["year"],
                instance=feedInst,
            )
            if bac.exists:
                bac.delete()
                return JsonResponse(
                    {"status_code": 200, "status_msg": "Deleted Successfully"},
                    safe=False,
                )
            else:
                return JsonResponse(
                    {"status_code": 400, "status_msg": "Batch does not exists"},
                    safe=False,
                )
        elif request.method == "GET":
            return HttpResponseBadRequest()
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def getuserslist(request):
    if request.headers["Authorization"] and checkAuthorization(
        request.headers["Authorization"]
    ):
        if request.method == "GET":
            username = request.GET.get("username", "")
            try:
                User.objects.get(username=username.lower(), is_superuser__in=[True])
                alluser = UserPermissionSerializer(
                    User.objects.filter(is_staff__in=[True]), many=True
                ).data
                return JsonResponse({"status_code": 200, "data": alluser}, safe=False)
            except Exception as e:
                print(e)
                return JsonResponse(
                    {"status_code": 400, "status_msg": "User is not authorized"},
                    safe=False,
                )
        elif request.method == "POST":
            data = JSONParser().parse(request)["data"]
            try:
                User.objects.get(
                    username=data["username"].lower(), is_superuser__in=[True]
                )
                for x in data["permission_data"]:
                    try:
                        userr = User.objects.get(id=x)
                        myuserr = MyUser.objects.get(user=userr)
                        try:
                            myuserr.canCreateBatch = data["permission_data"][x][
                                "canCreateBatch"
                            ]
                            myuserr.canCreateFeedbackForm = data["permission_data"][x][
                                "canCreateFeedbackForm"
                            ]
                            myuserr.canCreateSubject = data["permission_data"][x][
                                "canCreateSubject"
                            ]
                            myuserr.save()
                        except Exception as e:
                            print(e)
                            return JsonResponse(
                                {"status_code": 400, "status_msg": "Error occurred"},
                                safe=False,
                            )
                    except Exception as e:
                        print(e)
                        return JsonResponse(
                            {"status_code": 505, "status_msg": "User does not exists"},
                            safe=False,
                        )
                return JsonResponse(
                    {
                        "status_code": 200,
                        "status_msg": "Permission updated successfully",
                    },
                    safe=False,
                )
            except Exception as e:
                print(e)
                return JsonResponse(
                    {"status_code": 505, "status_msg": "User does not exists"},
                    safe=False,
                )
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def bacUpdate(request):
    if request.headers["Authorization"] and checkAuthorization(
        request.headers["Authorization"]
    ):
        if request.method == "POST":
            data = JSONParser().parse(request)["data"]
            try:
                feedInst = FeedbackInstance.objects.get(is_selected__in=[True])
                existingDifferentMail = []
                checkYearBatch = Batch.objects.filter(instance=feedInst)
                if checkYearBatch.exists():

                    for studarry in data["allStudents"]:
                        for xx in checkYearBatch:
                            for xxx in xx.student_email_mtm.all():
                                if studarry["email"].lower() == xxx.email.lower():
                                    existingDifferentMail.append(
                                        "This mail {} exists in {} year, {} division, {} batch".format(
                                            studarry["email"].lower(),
                                            xx.year,
                                            xx.batch_division,
                                            xx.batch_name,
                                        )
                                    )
                if len(existingDifferentMail) > 0:
                    return JsonResponse(
                        {
                            "status_code": 401,
                            "status_msg": "Same user exists in different year or division",
                            "sameMail": existingDifferentMail,
                        },
                        safe=False,
                    )
                for x in data["newfinbacNameId"]:
                    for key, value in x.items():
                        try:
                            bacId = Batch.objects.get(instance=feedInst, id=value)
                            bacId.batch_name = key
                            emailList = set()
                            for ubac in data["excelData"][key]:
                                if "user_id" in ubac:
                                    try:
                                        u = User.objects.get(id=ubac["user_id"])
                                        myu = MyUser.objects.get(user=u)
                                        emailList.add(myu)
                                    except Exception as e:
                                        print(e)
                                else:
                                    try:
                                        u = User(
                                            username=ubac["email"].lower(),
                                            email=ubac["email"].lower(),
                                            password=make_password("pass@123"),
                                        )
                                        u.save()
                                        myu = MyUser(
                                            user=u,
                                            sapId=ubac["sapId"],
                                            email=ubac["email"].lower(),
                                            mobile=ubac["phone"],
                                            name=ubac["name"],
                                        )
                                        myu.save()
                                        emailList.add(myu)
                                    except Exception as e:
                                        try:
                                            u = User.objects.get(
                                                username=ubac["email"].lower(),
                                                email=ubac["email"],
                                            )

                                            myu = MyUser.objects.get(user=u)
                                            myu.sapId = ubac["sapId"]
                                            myu.email = ubac["email"].lower()
                                            myu.mobile = ubac["phone"]
                                            myu.name = ubac["name"]
                                            myu.save()
                                            emailList.add(myu)
                                        except Exception as e:
                                            print(e)
                                            return JsonResponse(
                                                {
                                                    "status_code": 400,
                                                    "status_msg": "Error occurred saving {} to db".format(
                                                        ubac["email"]
                                                    ),
                                                },
                                                safe=False,
                                            )
                            bacId.student_email_mtm.set(emailList)
                            bacId.save()
                        except Exception as e:
                            emailList = set()
                            newBatch = Batch(
                                instance=feedInst,
                                batch_name=key,
                                batch_division=data["div_name"],
                                year=data["year"],
                            )
                            newBatch.save()
                            for ubac in data["excelData"][key]:
                                if "user_id" in ubac:
                                    try:
                                        u = User.objects.get(id=ubac["user_id"])
                                        myu = MyUser.objects.get(user=u)
                                        emailList.add(myu)
                                    except Exception as e:
                                        print(e)
                                else:
                                    try:
                                        u = User(
                                            username=ubac["email"].lower(),
                                            email=ubac["email"].lower(),
                                            password=make_password("pass@123"),
                                            first_name=ubac["name"],
                                            is_staff=True,
                                        )
                                        u.save()
                                        myu = MyUser(
                                            user=u,
                                            sapId=ubac["sapId"],
                                            email=ubac["email"].lower(),
                                            mobile=ubac["phone"],
                                            name=ubac["name"],
                                        )
                                        myu.save()
                                        emailList.add(myu)
                                    except Exception as e:
                                        return JsonResponse(
                                            {
                                                "status_code": 400,
                                                "status_msg": "Error Occured, {} exists".format(
                                                    ubac["email"]
                                                ),
                                            },
                                            safe=False,
                                        )
                            newBatch.student_email_mtm.set(emailList)
                            newBatch.save()
                return JsonResponse(
                    {"status_code": 200, "status_msg": "Updated Successfully"},
                    safe=False,
                )

            except:
                return JsonResponse(
                    {
                        "status_code": 400,
                        "status_msg": "Create Feedback Instance First",
                    },
                    safe=False,
                )
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def bac(request):
    if request.headers["Authorization"] and checkAuthorization(
        request.headers["Authorization"]
    ):
        if request.method == "POST":
            data = JSONParser().parse(request)["data"]
            try:
                feedInst = FeedbackInstance.objects.get(is_selected__in=[True])
                existingDifferentMail = []
                checkYearBatch = Batch.objects.filter(instance=feedInst)
                if checkYearBatch.exists():
                    for studarry in data["allStudents"]:
                        for xx in checkYearBatch:
                            for xxx in xx.student_email_mtm.all():
                                if studarry["Email"].lower() == xxx.email.lower():
                                    existingDifferentMail.append(
                                        "This mail {} exists in {} year, {} division, {} batch".format(
                                            studarry["Email"].lower(),
                                            xx.year,
                                            xx.batch_division,
                                            xx.batch_name,
                                        )
                                    )
                if len(existingDifferentMail) > 0:
                    return JsonResponse(
                        {
                            "status_code": 401,
                            "status_msg": "Same user exists in different year or division",
                            "sameMail": existingDifferentMail,
                        },
                        safe=False,
                    )
                for batch in data["excelData"]:
                    batch = batch.upper()
                    checkBatch = Batch.objects.filter(
                        instance=feedInst,
                        batch_name=batch,
                        year=data["year"],
                        batch_division=data["div_name"].upper(),
                    )
                    if checkBatch.exists():
                        # if batch exists
                        return JsonResponse(
                            {"status_code": 400, "status_msg": "Batch already exists"},
                            safe=False,
                        )
                    emailList = []
                    emailList_mtm = set()
                    for x in data["excelData"]["{0}".format(batch)]:
                        try:
                            checkUser = User.objects.get(
                                email=x["Email"].lower(), username=x["Email"].lower()
                            )

                            # user already exists
                            checkUser.name = x["Name"]
                            myUser = MyUser.objects.get(user=checkUser)
                            myUser.name = x["Name"]
                            myUser.sapId = x["SapID"]
                            myUser.mobile = x["Phone"]
                            myUser.year = data["year"]
                            checkUser.save()
                            myUser.save()
                        except Exception as e:

                            # creating new user
                            user = User(
                                first_name=x["Name"],
                                username=x["Email"].lower(),
                                email=x["Email"].lower(),
                                password=make_password("pass@123"),
                            )
                            myUser = MyUser(
                                user=user,
                                name=x["Name"],
                                sapId=x["SapID"],
                                email=x["Email"].lower(),
                                mobile=x["Phone"],
                                year=data["year"],
                                isActivated=False,
                                isVerified=False,
                                canCreateBatch=False,
                                canCreateSubject=False,
                                canCreateFeedbackForm=False,
                            )
                            user.save()
                            myUser.save()
                        emailList.append(
                            {
                                "email": x["Email"].lower(),
                                "sapId": x["SapID"],
                                "name": x["Name"],
                                "phone": x["Phone"],
                            }
                        )
                        emailList_mtm.add(myUser)
                    if not checkBatch.exists():
                        # if batch does not exists create a new batch
                        try:
                            batch_instance = Batch(
                                instance=feedInst,
                                batch_name=batch,
                                year=data["year"],
                                batch_division=data["div_name"].upper(),
                            )
                            batch_instance.save()
                            batch_instance.student_email_mtm.set(emailList_mtm)
                            batch_instance.save()
                        except:
                            return JsonResponse(
                                {"status_code": 400, "status_msg": "Error occured"},
                                safe=False,
                            )

                return JsonResponse(
                    {"status_code": 200, "status_msg": "Success"}, safe=False
                )
            except Exception as e:
                print(e)
                return JsonResponse(
                    {
                        "status_code": 400,
                        "status_msg": "Create Feedback Instance First",
                    },
                    safe=False,
                )

        else:
            return HttpResponseBadRequest()
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def getBatches(request):
    if request.headers["Authorization"] and checkAuthorization(
        request.headers["Authorization"]
    ):
        if request.method == "GET":
            subb = {}
            ###Response-Format####
            # subb={
            #   1: {
            #    "D":
            #        {
            #            "year":"1",
            #            "batch_div":"D",
            #            "students_list":{
            # "D1":{

            # }
            # }

            #        },
            #    "C":
            #        {
            # "year":"1",
            # "batch_div":"C",
            # "students_list":[]
            #        },
            #    },
            # }

            # data_batch_div = Batch.objects.order_by('batch_division').values('batch_division').distinct()
            ##data=BatchSerializer(data,many=True).data
            ##print(data_batch_div)
            # div_list=[]
            # for x in data_batch_div:
            #    #print(x["batch_division"])
            #    div_list.append(x["batch_division"])
            try:
                inst = FeedbackInstance.objects.get(is_selected__in=[True])
                data = Batch.objects.filter(instance=inst)
            except:
                data = []
            # print(data)
            for x in data:
                if x.year not in subb:
                    subb[x.year] = {}
                if x.batch_division not in subb[x.year]:
                    subb[x.year][x.batch_division] = {
                        "year": x.year,
                        "batch_div": x.batch_division,
                        "students_list": {x.batch_name: []},
                        "total_student_count": 0,
                        "batch_name_id": {},
                    }
                try:
                    subb[x.year][x.batch_division]["students_list"][x.batch_name] = (
                        UserTMTMSerializer(x.student_email_mtm.all(), many=True).data
                    )
                    subb[x.year][x.batch_division]["batch_name_id"][x.batch_name] = x.id
                    subb[x.year][x.batch_division]["total_student_count"] += len(
                        subb[x.year][x.batch_division]["students_list"][x.batch_name]
                    )
                except Exception as e:
                    print(e)
            # print(subb)
            res_data = []
            for x in subb:
                for y in subb[x]:
                    # print(subb[x][y])
                    res_data.append(subb[x][y])

            # res_dict = {}
            # for data_inst in data:
            #    temp_dic = {
            #        'batch_name': data_inst.batch_name
            #    }
            #    if data_inst.year in res_dict:
            #        res_dict[data_inst.year].append(temp_dic)
            #    else:
            #        res_dict[data_inst.year] = [temp_dic]
            return JsonResponse(
                {"status_code": 200, "status_msg": "Success", "batchData": res_data},
                safe=False,
            )

    else:
        return HttpResponseBadRequest()


@csrf_exempt
def generateSecretCode(request):
    if request.headers["Authorization"] and checkAuthorization(
        request.headers["Authorization"]
    ):
        if request.method == "POST":
            data = JSONParser().parse(request)["data"]
            try:
                User.objects.get(
                    username=data["username"].lower(), is_superuser__in=[True]
                )
                MetaInfo.objects.all().delete()
                code = id_generator()
                try:
                    MetaInfo(secret_code=code).save()
                except Exception as e:
                    print(e)
                    return JsonResponse(
                        {"status_code": 400, "status_msg": e, "secret_code": code},
                        safe=False,
                    )
                return JsonResponse(
                    {
                        "status_code": 200,
                        "status_msg": "Successful",
                        "secret_code": code,
                    },
                    safe=False,
                )
            except:
                return JsonResponse(
                    {"status_code": 400, "status_msg": "User does not have rights"},
                    safe=False,
                )
        elif request.method == "GET":
            username = request.GET.get("username", "")
            try:
                User.objects.get(username=username.lower(), is_superuser__in=[True])
                secret_code = MetaInfo.objects.filter()
                if secret_code.exists():
                    secret_code = secret_code[0].secret_code
                else:
                    secret_code = ""
                return JsonResponse(
                    {
                        "status_code": 200,
                        "status_msg": "Successful",
                        "secret_code": secret_code,
                    },
                    safe=False,
                )
            except:
                return JsonResponse(
                    {"status_code": 400, "status_msg": "User does not have rights"},
                    safe=False,
                )
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def createNewInst(request):
    if request.headers["Authorization"] and checkAuthorization(
        request.headers["Authorization"]
    ):
        if request.method == "POST":
            data = JSONParser().parse(request)["data"]
            try:
                User.objects.get(
                    username=data["username"].lower(), is_superuser__in=[True]
                )
                if data["isSelectedInst"] == True:
                    da = FeedbackInstance.objects.filter(is_selected__in=[True])
                    if da.exists():
                        for x in da:

                            x.is_selected = False
                            x.save()
                daa = FeedbackInstance.objects.filter(is_latest__in=[True])
                if daa.exists():
                    for x in daa:
                        x.is_latest = False
                        x.save()

                feedInst = FeedbackInstance(
                    instance_name=data["instName"],
                    is_selected=data["isSelectedInst"],
                    is_latest=data["isLatest"],
                )
                feedInst.save()
                return JsonResponse(
                    {"status_code": 200, "status_msg": "Successful"}, safe=False
                )
            except Exception as e:
                print(e)
                return JsonResponse(
                    {"status_code": 400, "status_msg": "User does not have rights"},
                    safe=False,
                )
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def tsettings(request):
    if request.headers["Authorization"] and checkAuthorization(
        request.headers["Authorization"]
    ):
        if request.method == "GET":
            username = request.GET.get("username", "")
            try:
                User.objects.get(username=username.lower(), is_superuser__in=[True])
                inst = FeedbackInst(
                    FeedbackInstance.objects.all().order_by("-is_selected"), many=True
                ).data
                secret_code = MetaInfo.objects.filter()
                if secret_code.exists():
                    secret_code = secret_code[0].secret_code
                else:
                    secret_code = ""
                return JsonResponse(
                    {
                        "inst": inst,
                        "secret_code": secret_code,
                        "status_code": 200,
                        "status_msg": "Success",
                    },
                    safe=False,
                )
            except:
                inst = []
                return JsonResponse(
                    {
                        "inst": inst,
                        "secret_code": "",
                        "status_code": 400,
                        "status_msg": "User do not have access",
                    },
                    safe=False,
                )
        elif request.method == "POST":
            data = JSONParser().parse(request)["data"]
            try:
                User.objects.filter(
                    username=data["username"].lower(), is_superuser__in=[True]
                )
                try:
                    dt = FeedbackInstance.objects.all()
                    for d in dt:
                        d.is_selected = False
                        d.save()
                    inst = FeedbackInstance.objects.get(
                        id=int(data["selectedInst"]["value"])
                    )
                    inst.is_selected = True
                    inst.save()
                    return JsonResponse(
                        {"status_code": 200, "status_msg": "Successful"}, safe=False
                    )
                except Exception as e:
                    print(e)
                    return JsonResponse(
                        {"status_code": 400, "status_msg": "Error Occured"}, safe=False
                    )
            except:
                return JsonResponse(
                    {"status_code": 400, "status_msg": "User is not authorized"},
                    safe=False,
                )
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def getTUsers1(request, username=""):
    if request.headers["Authorization"] and checkAuthorization(
        request.headers["Authorization"]
    ):
        if request.method == "GET":
            ###Response-Format####
            # sub={
            #    "1":{"SA":{
            #        "sub_name":"SA",
            # "theo_bac":[],
            # "prac_bac":[],
            # "year":1
            #    }
            #    }
            # }
            resp = {}
            try:
                selectedInstance = FeedbackInstance.objects.get(is_selected__in=[True])
                subb = {}
                try:
                    user = User.objects.get(username=username.lower())
                    try:
                        for subject in Subject.objects.filter(
                            instance=selectedInstance
                        ):
                            subTheo = SubjectTheory.objects.filter(
                                batch__instance=selectedInstance, subject=subject
                            )
                            subPrac = SubjectPractical.objects.filter(
                                batch__instance=selectedInstance, subject=subject
                            )
                            for theo in subTheo:
                                sub_teacher_email = theo.sub_teacher_email
                                if (
                                    str(user.id) in sub_teacher_email
                                    or user.is_superuser
                                ):
                                    sub_name = subject.subject_name
                                    sub_id = subject.id
                                    batch_yr = theo.batch.year
                                    if sub_id not in subb:
                                        subb[sub_id] = {
                                            "sub_name": sub_name,
                                            "theo_bac": [],
                                            "prac_bac": [],
                                            "year": batch_yr,
                                        }
                                    subb[sub_id]["theo_bac"].append(
                                        theo.batch.batch_name
                                    )
                            for prac in subPrac:
                                prac_teacher_email = prac.prac_teacher_email
                                if (
                                    str(user.id) in prac_teacher_email
                                    or user.is_superuser
                                ):
                                    sub_id = subject.id
                                    sub_name = subject.subject_name
                                    batch_yr = prac.batch.year
                                    if sub_id not in subb:
                                        subb[sub_id] = {
                                            "sub_name": sub_name,
                                            "theo_bac": [],
                                            "prac_bac": [],
                                            "year": batch_yr,
                                        }
                                    subb[sub_id]["prac_bac"].append(
                                        prac.batch.batch_name
                                    )
                        resp["my_batches"] = subb
                        return JsonResponse(
                            {"status_code": 200, "data": resp}, safe=False
                        )
                    except Exception as e:
                        print(e)
                        return JsonResponse(
                            {"status_code": 400, "status_msg": "Error Occured"},
                            safe=False,
                        )
                except:
                    return JsonResponse(
                        {"status_code": 400, "status_msg": "User does not exists"},
                        safe=False,
                    )
            except:
                return JsonResponse(
                    {"status_code": 400, "status_msg": "No feedback instance"},
                    safe=False,
                )
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def getTUsers(request, username=""):
    if request.headers["Authorization"] and checkAuthorization(
        request.headers["Authorization"]
    ):
        if request.method == "GET":
            ###Response-Format####
            # sub={
            #    "1":{"SA":{
            #        "sub_name":"SA",
            #        "theo_bac":[],
            #        "prac_bac":[],
            #        "year":1
            #    }
            #    }
            # }
            resp = {}
            try:
                lastestInstance = FeedbackInstance.objects.get(is_selected__in=[True])

                resp["teachers"] = UserTSerializer(
                    User.objects.filter(is_staff__in=[True], is_superuser__in=[False]),
                    many=True,
                ).data
                batc = Batch.objects.filter(instance=lastestInstance)
                if batc.exists():
                    resp["batches"] = BatchSerializer(batc, many=True).data
                else:
                    resp["batches"] = []

            except Exception as e:
                print(e)
                resp["batches"] = []
                resp["teachers"] = []

            return JsonResponse(resp, safe=False)
        elif request.method == "POST":
            data = JSONParser().parse(request)["data"]
            try:
                lastestInstance = FeedbackInstance.objects.get(is_selected__in=[True])
                inst_sub = Subject(
                    subject_name=data["subject_name"], instance=lastestInstance
                )
                inst_sub.save()
                for x in data["batch"]:
                    if x != "":
                        try:
                            bac = Batch.objects.get(id=int(x), instance=lastestInstance)
                            inst_theo = SubjectTheory(
                                subject=inst_sub,
                                batch=bac,
                                sub_teacher_email=data["theory_teachers"],
                            )
                            inst_prac = SubjectPractical(
                                subject=inst_sub,
                                batch=bac,
                                prac_teacher_email=data["prac_teachers"],
                            )
                            inst_theo.save()
                            inst_prac.save()
                        except Exception as e:
                            print(e)
                return JsonResponse(
                    {"status_code": 200, "status_msg": "Success"}, safe=False
                )
            except:
                return JsonResponse(
                    {
                        "status_code": 400,
                        "status_msg": "Create Feedback instance first",
                    },
                    safe=False,
                )

    else:
        return HttpResponseBadRequest()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


@csrf_exempt
def login(request):
    if request.method == "POST":
        data = JSONParser().parse(request)["data"]
        username = data["username"].lower()
        password = data["password"]
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            try:
                # Block of code that throws exception
                auth.login(request, user)
            except Exception as e:
                print(e)
                return JsonResponse({"error": "Error Occurred"}, safe=False)
            try:
                userr = User.objects.get(username=username)
                # print(userr)
                isActi = False
                isVeri = False
                try:
                    myUser = MyUser.objects.get(user=userr)
                    token = get_tokens_for_user(user=userr)
                    if myUser.isActivated:
                        isActi = True
                        if myUser.isVerified:
                            isVeri = True
                    if userr.is_staff == True and userr.is_superuser == True:
                        return JsonResponse(
                            {
                                "userRole": "admin",
                                "token": token,
                                "auth": True,
                                "isActivated": isActi,
                                "isVerified": isVeri,
                                "exist": 1,
                                "is_staff": 1,
                                "is_superstaff": 1,
                                "email": myUser.email,
                                "name": myUser.name,
                                "canCreateBatch": myUser.canCreateBatch,
                                "canCreateSubject": myUser.canCreateSubject,
                                "canCreateFeedbackForm": myUser.canCreateFeedbackForm,
                            },
                            safe=False,
                        )
                    elif userr.is_staff == True and userr.is_superuser == False:
                        return JsonResponse(
                            {
                                "userRole": "teacher",
                                "token": token,
                                "auth": True,
                                "isActivated": isActi,
                                "isVerified": isVeri,
                                "exist": 1,
                                "is_staff": 1,
                                "is_superstaff": 0,
                                "email": myUser.email,
                                "name": myUser.name,
                                "canCreateBatch": myUser.canCreateBatch,
                                "canCreateSubject": myUser.canCreateSubject,
                                "canCreateFeedbackForm": myUser.canCreateFeedbackForm,
                            },
                            safe=False,
                        )
                    else:
                        return JsonResponse(
                            {
                                "userRole": "student",
                                "token": token,
                                "auth": True,
                                "isActivated": isActi,
                                "isVerified": isVeri,
                                "exist": 1,
                                "is_staff": 0,
                                "is_superstaff": 0,
                                "email": myUser.email,
                                "name": myUser.name,
                                "sapId": myUser.sapId,
                                "age": myUser.age,
                                "gender": myUser.gender,
                                "isActivated": myUser.isActivated,
                                "isVerified": myUser.isVerified,
                                "mobile": myUser.mobile,
                                "year": myUser.year,
                            },
                            safe=False,
                        )
                except:
                    return JsonResponse(
                        {"status_code": 505, "status_msg": "User does not exists"},
                        safe=False,
                    )
            except:
                return JsonResponse(
                    {"status_code": 505, "status_msg": "User does not exists"},
                    safe=False,
                )
        else:
            return JsonResponse({"exist": 0}, safe=False)


# @csrf_exempt
# def createAdmin(request):
#    if request.method == 'POST':
#        data = JSONParser().parse(request)['data']
#        username = data['username']
#        password = data['password']
#        email = data['email'].lower()
#        user = User.objects.create_user(
#            username=username, password=password, email=email)
#        user.is_staff = True
#        user.save()
#        return JsonResponse({"exist": 1}, safe=False)
@csrf_exempt
def getFeedbackForm(request):
    if request.method == "GET":
        feedback_arr = [
            "Ability to understand student's difficulties and willingness to help them",
            "Commitment to academic work in the class",
            "Regularity and Punctuality",
            "Interaction in the class",
            "Coverage of syllabus",
            "Commitment to academic work in the clas",
            "Effective communication of subject matter",
            "Management of lecture & class cuntrol",
            "Overall abllty to malntaln sanctity of Teaching - Learning process",
        ]
        faculty_teacher = "faculty_teacher_ABC"
        subject = "SUB_ABC"
        res_data = {
            "feedback_arr": feedback_arr,
            "faculty_teacher": faculty_teacher,
            "subject": subject,
        }
        return JsonResponse({"res_data": res_data}, safe=False)


# @csrf_exempt
# def createSuperAdmin(request):
#    if request.method == 'POST':
#        data = JSONParser().parse(request)['data']
#        username = data['username']
#        password = data['password']
#        email = data['email'].lower()
#        user = User.objects.create_user(
#            username=username, password=password, email=email)
#        user.is_staff = True
#        user.is_superuser = True
#        user.save()
#        return JsonResponse({"exist": 1}, safe=False)

# @csrf_exempt
# def createStudent(request):
#     if request.method == 'POST' :
#         data=JSONParser().parse(request)['data']
#         username = data['username']
#         password = data['password']
#         email = data['email']
#         user = User.objects.create_user(username=username,password=password,email=email)
#         user.save()
#         return JsonResponse({"exist":1},safe=False)


@csrf_exempt
def saveProfile(request):
    if request.headers["Authorization"] and checkAuthorization(
        request.headers["Authorization"]
    ):
        if request.method == "POST":
            data = JSONParser().parse(request)["data"]
            data = data["user"]
            try:
                user = User.objects.get(id=data["id"])
                myuser = MyUser.objects.get(user=user)
                myuser.name = data["name"]
                myuser.gender = data["gender"]
                myuser.mobile = data["mobile"]
                myuser.age = data["age"]
                myuser.isVerified = True
                if not "is_staff" in data:
                    myuser.sapId = data["sapId"]
                myuser.save()
            except Exception as e:
                print(e)
                return JsonResponse(
                    {"status_code": 400, "status_msg": "User does not exists"},
                    safe=False,
                )
            return JsonResponse(
                {"status_code": 200, "status_msg": "Saved Successfully"}, safe=False
            )
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def getProfile(request):
    if request.headers["Authorization"] and checkAuthorization(
        request.headers["Authorization"]
    ):
        if request.method == "GET":
            user_id = request.GET.get("user_id", "")
            try:
                user = User.objects.get(username=user_id.lower())
                if not user.is_staff:
                    userData = StudUserSerializer(user, many=False).data
                else:
                    userData = TeacherUserSerializer(user, many=False).data
                return JsonResponse({"data": userData}, safe=False)
            except Exception as e:
                print(e)
                return HttpResponseNotFound(e)
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def getFeedbackData(request):
    if request.headers["Authorization"] and checkAuthorization(
        request.headers["Authorization"]
    ):
        if request.method == "GET":
            form_id = request.GET.get("form_id", "")
            feedbacres = []
            sugg = []
            isfilled = []
            try:
                form = FeedbackForm.objects.get(id=form_id)
                formsData = FeedbackUserFteacherConnectorSerializer(
                    FeedbackUserConnector.objects.filter(form=form), many=True
                ).data
                for data in formsData:
                    if data["is_filled"]:
                        feedbacres.append(data["user_feedback"]["feedback_form_result"])
                        sugg.append(data["user_feedback"]["suggestion"])
                    isfilled.append(
                        {"isfilled": data["is_filled"], "student": data["student_name"]}
                    )
            except Exception as e:
                print(e)
                return JsonResponse({"error": e}, safe=False)
        return JsonResponse(
            {
                "feedbacres": feedbacres,
                "sugg": sugg,
                "isfilled": isfilled,
                "isTheory": form.is_theory,
                "isActive": form.is_alive,
                "subject_name": form.subject.subject_name,
                "year": form.year,
                "date": form.due_date,
                "batch_list": form.batch_list,
                "teacher": form.teacher.myuser.name,
            },
            safe=False,
        )
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def sendOtp(request):
    if request.method == "POST":
        if request.headers["Authorization"] and checkAuthorization(
            request.headers["Authorization"]
        ):
            data = JSONParser().parse(request)["data"]
            email = data["email"].lower()
            user = User.objects.get(email=email)
            if user is not None:
                otp = pyotp.random_base32()
                otp = pyotp.TOTP(otp).now()
                otpp = Otp.objects.filter(LoginUser=user)
                if otpp is not None:
                    Otp.objects.filter(LoginUser=user).delete()
                Otp.objects.create(
                    Otp=otp,
                    LoginUser=user,
                    timeOfGeneration=datetime.datetime.now(datetime.timezone.utc),
                )
                subject = "OTP for account activation - Feedback Portal Login"
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [
                    email,
                ]
                msg = EmailMultiAlternatives(
                    subject=subject, from_email=email_from, to=recipient_list
                )
                args = {}
                args["name"] = "{}".format(user.first_name)
                print(user.first_name)
                args["otp"] = "{}".format(otp)
                args["dj_logo"] = "{}".format(os.environ.get("DJ_LOGO"))
                args["mail"] = "{}".format(os.environ.get("EMAIL_HOST_USER"))

                try:
                    html_template = get_template("api/SendOTP.html").render(args)
                    msg.attach_alternative(html_template, "text/html")
                    msg.send()
                    return JsonResponse({"Otp sent to": email}, safe=False)
                except Exception as e:
                    print(e)
                    return JsonResponse({"Otp failed to sent to": email}, safe=False)
                # send_mail(subject, message, email_from, recipient_list)
            else:
                return JsonResponse({"User does not exist": email}, safe=False)
        else:
            return JsonResponse({"error": "Invalid Authorization"}, safe=False)


@csrf_exempt
def verifyOtp(request):
    if request.method == "POST":
        data = JSONParser().parse(request)["data"]
        email = data["email"].lower()
        otp = data["otp"]
        try:
            user = User.objects.get(email=email)
        except Exception as e:
            return JsonResponse({"User does not exist": email}, safe=False)
        try:
            otpp = Otp.objects.filter(LoginUser=user).order_by("-timeOfGeneration")[0]
        except Exception as e:
            return JsonResponse({"Otp not sent": email}, safe=False)
        if otpp is not None:
            if otpp.Otp == otp:
                minutes = (
                    datetime.datetime.now(datetime.timezone.utc) - otpp.timeOfGeneration
                ).seconds / 60
                if minutes < 5:
                    myUser = MyUser.objects.get(user=user)
                    myUser.isActivated = True
                    myUser.save()
                    return JsonResponse(
                        {
                            "status": 200,
                            "status_msg": "Otp verified",
                            "Otp verified": email,
                            "email": myUser.email,
                            "name": myUser.name,
                            "sapId": myUser.sapId,
                            "age": myUser.age,
                            "gender": myUser.gender,
                            "isActivated": myUser.isActivated,
                            "isVerified": myUser.isVerified,
                            "mobile": myUser.mobile,
                            "year": myUser.year,
                        },
                        safe=False,
                    )
                else:
                    Otp.objects.filter(LoginUser=user).delete()
                    return JsonResponse(
                        {
                            "status": 201,
                            "status_msg": "Otp expired",
                            "Otp expired": email,
                        },
                        safe=False,
                    )
            else:
                return JsonResponse(
                    {
                        "status": 202,
                        "status_msg": "Otp incorrect",
                        "Otp incorrect": email,
                    },
                    safe=False,
                )
        else:
            return JsonResponse(
                {"status": 400, "status_msg": "Otp not sent", "Otp not sent": email},
                safe=False,
            )


@csrf_exempt
def createTeacher(request):
    if request.method == "POST":
        data = JSONParser().parse(request)["data"]
        secret_code = MetaInfo.objects.filter()
        if secret_code.exists():
            secret_code = secret_code[0].secret_code
            if data["secret_key"] == secret_code:
                try:
                    User.objects.get(username=data["email"].lower())
                    MyUser.objects.get(email=data["email"].lower())
                except Exception as e:
                    print(e)
                    try:
                        user = User(
                            username=data["email"].lower(),
                            email=data["email"].lower(),
                            password=make_password(data["password"]),
                            first_name=data["first_name"],
                            last_name=data["last_name"],
                            is_staff=True,
                        )
                        myUser = MyUser(
                            user=user,
                            name="{} {}".format(data["first_name"], data["last_name"]),
                            email=data["email"].lower(),
                            isActivated=True,
                            canCreateBatch=False,
                            canCreateSubject=True,
                            canCreateFeedbackForm=True,
                        )
                        user.save()
                        myUser.save()
                    except Exception as err:
                        print(err)
                        return JsonResponse(
                            {"status": 400, "status_msg": "Error Occured"}, safe=False
                        )
                    return JsonResponse(
                        {"status": 200, "status_msg": "Successfull Registration"},
                        safe=False,
                    )
            else:
                return JsonResponse(
                    {"status": 400, "status_msg": "Invalid Secret Key"}, safe=False
                )
        else:
            return JsonResponse(
                {
                    "status": 400,
                    "status_msg": "Secret Key is not yet generated contact your administrator",
                },
                safe=False,
            )


# @csrf_exempt
# def createTeacher(request):
#    if request.method == 'POST':
#        if request.headers['Authorization'] and checkAuthorization(request.headers['Authorization']):
#            data = JSONParser().parse(request)['data']
#            username = data['email']
#            supername = data['supername']
#            superpassword = data['superpassword']
#            user = User.objects.filter(username=username)
#            if user.exists():
#                return JsonResponse({"exist": 1}, safe=False)
#            superuser = auth.authenticate(
#                username=supername, password=superpassword)
#            if superuser is not None:
#                superuser = User.objects.get(username=supername)
#                if superuser.is_superuser:
#                    password = data['password']
#                    email = data['email']
#                    name = data['name']
#                    user = User.objects.create_user(
#                        username=username, password=password, email=email)
#                    user.is_staff = True
#                    user.save()
#                    MyUser.objects.create(user=user, email=email, name=name)
#                    return JsonResponse({"exist": 1}, safe=False)
#                else:
#                    return JsonResponse({"error": "Not a superuser"}, safe=False)
#        else:
#            return JsonResponse({"error": "Invalid Authorization"}, safe=False)


@csrf_exempt
def deleteFeedbackform(request):
    if request.headers["Authorization"] and checkAuthorization(
        request.headers["Authorization"]
    ):
        if request.method == "POST":
            data = JSONParser().parse(request)["data"]
            try:
                form = FeedbackForm.objects.get(id=data["form_id"])
                form.delete()
                return JsonResponse(
                    {"status_code": 200, "status_msg": "Successfully Deleted Form"},
                    safe=False,
                )
            except:
                return JsonResponse(
                    {
                        "status_code": 400,
                        "status_msg": "Error occurred while deleting form",
                    },
                    safe=False,
                )
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def updateFeedbackform(request):
    if request.headers["Authorization"] and checkAuthorization(
        request.headers["Authorization"]
    ):
        if request.method == "POST":
            data = JSONParser().parse(request)["data"]
            try:
                form = FeedbackForm.objects.get(id=data["form_id"])
                form.due_date = data["due_date"]
                form.save()
                return JsonResponse(
                    {
                        "status_code": 200,
                        "status_msg": "Successfully UpdatedForm",
                        "form": FeedbackFormSerializer(form).data,
                    },
                    safe=False,
                )
            except Exception as e:
                print(e)
                return JsonResponse(
                    {
                        "status_code": 400,
                        "status_msg": "Error occurred while updating form",
                    },
                    safe=False,
                )
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def getYrBatches(request):
    if request.headers["Authorization"] and checkAuthorization(
        request.headers["Authorization"]
    ):
        if request.method == "GET":
            res_data_sub = {
                "getYrBatches": {
                    1: {"theo": [], "prac": []},
                    2: {"theo": [], "prac": []},
                    3: {"theo": [], "prac": []},
                    4: {"theo": [], "prac": []},
                }
            }
            try:
                userr = User.objects.get(
                    username=request.GET.get("username", "").lower()
                )
                try:
                    feedbackInst = FeedbackInstance.objects.get(is_selected__in=[True])

                    for x in range(1, 5):
                        subTInst = SubjectTheory.objects.filter(
                            batch__year=x, batch__instance=feedbackInst
                        )
                        if subTInst.exists():
                            data = SubjectTheoYearSerializer(subTInst, many=True).data
                            for y in data:
                                if (str(userr.id) in y["sub_teacher_email"]) or (
                                    userr.is_superuser == True
                                ):
                                    isNameInResData = False
                                    for xx in res_data_sub["getYrBatches"][x]["theo"]:
                                        if y["subject_name"] == xx["label"]:
                                            isNameInResData = True
                                            break
                                    if not isNameInResData:
                                        res_data_sub["getYrBatches"][x]["theo"].append(
                                            {
                                                "label": y["subject_name"],
                                                "value": str(y["subject_id"]) + "Theo",
                                                "theo": True,
                                                "batch_name": y["batch_name"],
                                            }
                                        )
                            data3 = SubjectPracYearSerializer(
                                SubjectPractical.objects.filter(
                                    batch__year=x, batch__instance=feedbackInst
                                ),
                                many=True,
                            ).data
                            for y in data3:
                                if str(userr.id) in y["prac_teacher_email"] or (
                                    userr.is_superuser == True
                                ):
                                    isNameInResData = False
                                    for xx in res_data_sub["getYrBatches"][x]["prac"]:
                                        if y["subject_name"] == xx["label"]:
                                            isNameInResData = True
                                            break
                                    if not isNameInResData:
                                        res_data_sub["getYrBatches"][x]["prac"].append(
                                            {
                                                "label": y["subject_name"],
                                                "value": str(y["subject_id"]) + "Prac",
                                                "theo": False,
                                                "batch_name": y["batch_name"],
                                            }
                                        )
                    return JsonResponse(
                        {"status_code": 200, "data": res_data_sub}, safe=False
                    )
                except Exception as e:
                    return JsonResponse(
                        {
                            "status_code": 400,
                            "status_msg": "Error Occurred, Feedback instance does not exists",
                        },
                        safe=False,
                    )
            except Exception as e:
                return JsonResponse(
                    {"status_code": 400, "status_msg": "User does not exists"},
                    safe=False,
                )
    else:
        return HttpResponseBadRequest()


@csrf_exempt
@teacher_auth
def getYearBatches(request):

    if request.method == "GET":

        user = request.current_teacher

        res_data_sub = {
            "getYrBatches": {
                1: {"theo": [], "prac": []},
                2: {"theo": [], "prac": []},
                3: {"theo": [], "prac": []},
                4: {"theo": [], "prac": []},
            }
        }

        try:
            feedback_inst = FeedbackInstance.objects.get(is_selected__in=[True])
        except FeedbackInstance.DoesNotExist:
            return JsonResponse(
                {
                    "status_code": 400,
                    "status_msg": "Error Occurred, Feedback instance does not exist",
                },
                safe=False,
            )

        for year in range(1, 5):
            subject_theory_dict = {}
            subject_pracs_dict = {}

            sub_t_inst = SubjectTheory.objects.filter(
                batch__year=year, batch__instance=feedback_inst
            )
            if sub_t_inst.exists():
                sub_theory_data = SubjectTheoYearSerializer(
                    sub_t_inst, many=True
                ).data
                for subject in sub_theory_data:
                    if (
                        str(user.id) in subject["sub_teacher_email"]
                        or user.is_superuser
                    ):
                        # Append subject to dictionary using subject name as key
                        subject_id = subject["subject_id"]
                        if subject_id not in subject_theory_dict:
                            subject_theory_dict[subject_id] = {
                                "label": subject["subject_name"],
                                "theo": True,
                                "batches": set(),
                            }
                        subject_theory_dict[subject_id]["batches"].add(
                            subject["batch_name"]
                        )

            sub_p_inst = SubjectPractical.objects.filter(
                batch__year=year, batch__instance=feedback_inst
            )
            if sub_p_inst.exists():
                sub_practical_data = SubjectPracYearSerializer(
                    sub_p_inst, many=True
                ).data
                for subject in sub_practical_data:
                    if (
                        str(user.id) in subject["prac_teacher_email"]
                        or user.is_superuser
                    ):
                        subject_id = subject["subject_id"]
                        if subject_id not in subject_pracs_dict:
                            subject_pracs_dict[subject_id] = {
                                "label": subject["subject_name"],
                                "theo": False,
                                "batches": set(),
                            }
                        subject_pracs_dict[subject_id]["batches"].add(
                            subject["batch_name"]
                        )

            for subject_id, subject_data in subject_theory_dict.items():
                res_data_sub["getYrBatches"][year]["theo"].append(
                    {
                        "label": f"{subject_data['label']} - {', '.join(sorted(subject_data['batches']))}",
                        "value": f"{subject_id} Theo",
                        "theo": subject_data["theo"],
                        "batch_name": ", ".join(sorted(subject_data["batches"])),
                    }
                )
            for subject_id, subject_data in subject_pracs_dict.items():
                res_data_sub["getYrBatches"][year]["prac"].append(
                    {
                        "label": f"{subject_data['label']} - {', '.join(sorted(subject_data['batches']))}",
                        "value": f"{subject_id} Prac",
                        "theo": subject_data["theo"],
                        "batch_name": ", ".join(sorted(subject_data["batches"])),
                    }
                )

        return JsonResponse({"status_code": 200, "data": res_data_sub}, safe=False)
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def createFeedbackForm(request):
    if request.headers["Authorization"] and checkAuthorization(
        request.headers["Authorization"]
    ):
        if request.method == "GET":
            res_data_sub = {}
            try:
                userr = User.objects.get(
                    username=request.GET.get("username", "").lower()
                )
                try:
                    feedbackInst = FeedbackInstance.objects.get(is_selected__in=[True])

                    if userr.is_superuser == True:
                        feedData = FeedbackFormSerializer(
                            FeedbackForm.objects.filter(instance=feedbackInst),
                            many=True,
                        ).data
                    else:
                        feedData = FeedbackFormSerializer(
                            FeedbackForm.objects.filter(teacher=userr), many=True
                        ).data
                    res_data_sub["feedData"] = feedData
                    return JsonResponse(
                        {"status_code": 200, "data": res_data_sub}, safe=False
                    )
                except Exception as e:
                    return JsonResponse(
                        {
                            "status_code": 400,
                            "status_msg": "Error Occurred, Feedback instance does not exists",
                        },
                        safe=False,
                    )
            except Exception as e:
                return JsonResponse(
                    {"status_code": 400, "status_msg": "User does not exists"},
                    safe=False,
                )

        elif request.method == "POST":
            data = JSONParser().parse(request)["data"]
            try:
                feedbackInst = FeedbackInstance.objects.get(is_selected__in=[True])
                if data["isTheo"]:
                    # data1=SubjectTheoYearSerializer(SubjectTheory.objects.filter(id=data["subject_id"]),many=True).data
                    # print(sub)
                    try:
                        sub = Subject.objects.get(id=data["subject_id"])
                        subTheo = SubjectTheory.objects.filter(subject=sub)
                        if subTheo.exists():
                            da = FeedbackForm(
                                teacher=User.objects.get(
                                    username=data["username"].lower()
                                ),
                                year=int(data["year"]),
                                subject=sub,
                                is_theory=True,
                                due_date=data["due_data"],
                                instance=feedbackInst,
                            )
                            da.save()
                            batchList = []
                            for x in subTheo:
                                batchList.append(x.batch.batch_name)
                                for stud in UserTMTMSerializer(
                                    x.batch.student_email_mtm, many=True
                                ).data:
                                    user = User.objects.filter(
                                        username=stud["email"].lower()
                                    )
                                    if user.exists():
                                        feedbackInst = FeedbackUserConnector(
                                            student=user[0], form=da
                                        )
                                        feedbackInst.save()
                            da.batch_list = batchList
                            da.save()
                    except Exception as e:
                        print(e)
                        return JsonResponse(
                            {"error": "Theory Subject does not exists"}, safe=False
                        )
                elif not data["isTheo"]:
                    try:
                        sub = Subject.objects.get(id=data["subject_id"])
                        subPrac = SubjectPractical.objects.filter(subject=sub)

                        if subPrac.exists():
                            da = FeedbackForm(
                                teacher=User.objects.get(
                                    username=data["username"].lower()
                                ),
                                year=int(data["year"]),
                                subject=sub,
                                is_theory=False,
                                due_date=data["due_data"],
                                instance=feedbackInst,
                            )
                            da.save()
                            batchList = []
                            for x in subPrac:
                                batchList.append(x.batch.batch_name)
                                for stud in UserTMTMSerializer(
                                    x.batch.student_email_mtm, many=True
                                ).data:
                                    user = User.objects.filter(
                                        username=stud["email"].lower()
                                    )
                                    if user.exists():
                                        try:
                                            feedbackInst = FeedbackUserConnector(
                                                student=user[0], form=da
                                            )
                                            feedbackInst.save()
                                        except Exception as e:
                                            print(e)
                            da.batch_list = (batchList,)
                            da.save()
                    except Exception as e:
                        print(e)
                        return JsonResponse(
                            {"error": "Practical Subject does not exists"}, safe=False
                        )
            except:
                return JsonResponse(
                    {
                        "status_code": 400,
                        "status_msg": "Create Feedback Instance First",
                    },
                    safe=False,
                )

            return JsonResponse(
                {"status_code": 200, "status_msg": "Success"}, safe=False
            )
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def getPass(request):
    if request.method == "GET":
        email = request.GET.get("email", "")
        token = request.GET.get("token", "")
        try:
            myuser = MyUser.objects.get(email=email)
            if myuser.passChangeToken == token:
                return JsonResponse(
                    {"status": 200, "status_msg": "Success"}, safe=False
                )
            else:
                return JsonResponse({"status": 404, "status_msg": "Error"}, safe=False)

        except Exception as e:
            print(e)
            return HttpResponseNotFound(e)


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


@csrf_exempt
def resetPasswordMail(request):
    if request.method == "POST":
        data = JSONParser().parse(request)["data"]
        try:
            user = User.objects.get(email=data["email"].lower())
            try:
                myuser = MyUser.objects.get(user=user)
                otp = pyotp.random_base32()
                otp = pyotp.TOTP(otp).now()
                myuser.passChangeToken = otp
                myuser.save()
                subject = "Your Forget Password Link - Feedback Portal"
                # link=f"http://localhost:3000/resetPassword/"+data["email"]+"/"+otp
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [
                    data["email"].lower(),
                ]
                msg = EmailMultiAlternatives(
                    subject=subject, from_email=email_from, to=recipient_list
                )
                args = {}
                args["dj_logo"] = "{}".format(os.environ.get("DJ_LOGO"))
                args["name"] = "{}".format(user.first_name)
                args["url"] = "{0}/resetPassword/{1}/{2}".format(
                    os.environ.get("FRONT_END_LINK"), data["email"].lower(), otp
                )
                args["mail"] = "{}".format(os.environ.get("EMAIL_HOST_USER"))
                html_template = get_template("api/ChangePassword.html").render(args)
                msg.attach_alternative(html_template, "text/html")
                msg.send()
                # send_mail(subject, message, email_from, recipient_list)
                return JsonResponse({"data": ""}, safe=False)
            except Exception as e:
                print(e)
                return HttpResponseNotFound()
        except Exception as e:
            print(e)
            return HttpResponseNotFound()


@csrf_exempt
def resetPassword(request):
    if request.method == "POST":
        data = JSONParser().parse(request)["data"]
        try:
            user = User.objects.get(email=data["email"].lower())
            user.set_password(data["newPassword"])
            user.save()
            try:
                myUser = MyUser.objects.get(email=data["email"].lower())
                myUser.passChangeToken = ""
                myUser.isActivated = True
                myUser.save()
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)
            return HttpResponseNotFound()
        return JsonResponse(
            {
                "data": "OK",
                "email": myUser.email,
                "name": myUser.name,
                "sapId": myUser.sapId,
                "age": myUser.age,
                "gender": myUser.gender,
                "isActivated": myUser.isActivated,
                "isVerified": myUser.isVerified,
                "mobile": myUser.mobile,
                "year": myUser.year,
            },
            safe=False,
        )


@csrf_exempt
def getAllStaffEmails(request):
    if request.method == "GET":
        if request.headers["Authorization"] and checkAuthorization(
            request.headers["Authorization"]
        ):
            staff = User.objects.all()
            res_data = []
            for s in staff:
                if s.is_staff == True and s.is_superuser == False:
                    res_data.append(s.email)
            return JsonResponse({"data": res_data}, safe=False)
        else:
            return JsonResponse({"data": "Unauthorized"}, safe=False)


@basic_auth
@teacher_auth
def get_all_subjects(request):
    selectedInstance = FeedbackInstance.objects.get(is_selected__in=[True])
    subjects = Subject.objects.filter(instance=selectedInstance).order_by("-id")

    serializer = SubjectSerializer(subjects, many=True)

    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
@require_http_methods(["DELETE"])
@basic_auth
@teacher_auth
def delete_subject(request, subject_id):
    try:
        subject = Subject.objects.get(pk=subject_id)
    except Subject.DoesNotExist:
        return JsonResponse({"message": "Subject does not exist"}, status=404)

    subject.delete()

    return JsonResponse({"message": "Subject deleted successfully"}, status=200)


def welcomeView(request):
    return HttpResponse("<h1>Welcome to feedback portal</h1>")


@superuser_auth
def test(request):
    return HttpResponse("<h1>Welcome to feedback portal server side</h1>")
