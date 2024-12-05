from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class MyUser(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField(primary_key=True,unique=True)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=50,blank=True)
    sapId = models.CharField(max_length=50,blank=True)
    mobile = models.IntegerField(blank=True,null=True)
    year = models.IntegerField(blank=True,null=True)
    isActivated = models.BooleanField(default=False)
    passChangeToken = models.CharField(max_length=50,blank=True,null=True)
    isVerified = models.BooleanField(default=False)
    canCreateBatch =models.BooleanField(default=False)
    canCreateSubject =models.BooleanField(default=True)
    canCreateFeedbackForm =models.BooleanField(default=True)

class FeedbackInstance(models.Model):
    instance_name = models.CharField(max_length=200,null=True, blank=True)
    is_latest=models.BooleanField(default=False)
    is_selected=models.BooleanField(default=False)
    def __str__(self):
        return "{0} {1}".format(self.instance_name,self.is_selected)
class MetaInfo(models.Model):
    secret_code = models.CharField(max_length=200,null=True,blank=True)
    def __str__(self):
        return "{0} {1}".format(self.id,self.secret_code)

class Batch(models.Model):
    batch_name = models.CharField(max_length=200)
    batch_division = models.CharField(max_length=10)
    year=models.IntegerField()
    student_email = models.JSONField(blank=True)
    student_email_mtm = models.ManyToManyField(MyUser)
    instance=models.ForeignKey(FeedbackInstance,on_delete=models.CASCADE,null=True, blank=True)
    # student_sapId = models.JSONField(null=True, blank=True)
    def __str__(self):
        return "{0} year {1} batch".format(self.year,self.batch_name)



    
class Subject(models.Model):
    subject_name=models.CharField(max_length=200)
    instance=models.ForeignKey(FeedbackInstance,on_delete=models.CASCADE,null=True, blank=True)
    def __str__(self):
        return "{0} subject_name || instance => {1}".format(self.subject_name,self.instance)

class SubjectTheory(models.Model):
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE)
    batch=models.ForeignKey(Batch,on_delete=models.CASCADE)
    sub_teacher_email = models.JSONField()    
    def __str__(self):
        return "{0} id {1} subname".format(self.id,self.subject.subject_name)

class SubjectPractical(models.Model):
    subject=models.ForeignKey(Subject,on_delete=models.CASCADE)
    batch=models.ForeignKey(Batch,on_delete=models.CASCADE)
    prac_teacher_email = models.JSONField()   
    def __str__(self):
        return "{0} id {1} prac-subname".format(self.id,self.subject.subject_name)

class FeedbackForm(models.Model):
    form_field = models.JSONField(null=True, blank=True) # can store feedback questions
    teacher=models.ForeignKey(User,on_delete=models.CASCADE)
    subject=models.ForeignKey(Subject,on_delete=models.CASCADE)
    instance=models.ForeignKey(FeedbackInstance,on_delete=models.CASCADE,null=True, blank=True)
    due_date=models.DateTimeField()
    year=models.IntegerField()
    batch_list=models.JSONField(null=True, blank=True)
    # connector=models.ForeignKey(FeedbackUserConnector,on_delete=models.CASCADE)
    is_theory = models.BooleanField(default=True)
    is_alive = models.BooleanField(default=True)
    def __str__(self):
        return "{0}".format(self.id)

class FeedbackUserConnector(models.Model):
    student=models.ForeignKey(User,on_delete=models.CASCADE)
    is_filled=models.BooleanField(default=False)
    user_feedback=models.JSONField(null=True, blank=True) # to store feedback user data
    form=models.ForeignKey(FeedbackForm,on_delete=models.CASCADE)
    def __str__(self):
        return "{0}-> id || {1}->Student".format(self.id,self.student.email)

class Otp(models.Model):
    Otp = models.CharField(max_length=100)
    timeOfGeneration = models.DateTimeField(auto_now_add=True)
    LoginUser = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return "{0}-> id || {1}->Student || {2}=> OTP".format(self.id,self.LoginUser.email,self.Otp)