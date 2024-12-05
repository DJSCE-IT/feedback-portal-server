from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry

class BatchSerializer(serializers.ModelSerializer):
    
    label=serializers.JSONField(source='batch_name')
    value=serializers.JSONField(source='id')
    class Meta:
        model = Batch
        fields=["label","value","year"]
class SubjectPracSerializer(serializers.ModelSerializer):
    #sub_teacher_email = serializers.JSONField(source='subject.sub_teacher_email')
    batch_id = serializers.JSONField(source='batch.id')
    batch_name = serializers.JSONField(source='batch.batch_name')
    sub_prac_id=serializers.CharField(source='id')
    class Meta:
        model = SubjectPractical
        fields=['batch_id','sub_prac_id','batch_name','prac_teacher_email']

class SubjectTheoSerializer(serializers.ModelSerializer):
    batch_name=serializers.JSONField(source='batch.batch_name')
    batch_year=serializers.JSONField(source='batch.year')
    subject_name=serializers.CharField(source="subject.subject_name")

    class Meta:
        model = SubjectTheory
        fields=["subject_name","batch_name","batch_year","sub_teacher_email"]
class SubjectTheoYearSerializer(serializers.ModelSerializer):
    batch_year=serializers.JSONField(source='batch.year')
    subject_name=serializers.CharField(source="subject.subject_name")
    subject_id=serializers.CharField(source="subject.id")
    batch_name=serializers.JSONField(source='batch.batch_name')
    class Meta:
        model = SubjectTheory
        fields=["subject_name","batch_year","sub_teacher_email","id","subject_id","batch_name"]
class SubjectPracYearSerializer(serializers.ModelSerializer):
    batch_year=serializers.JSONField(source='batch.year')
    subject_name=serializers.JSONField(source='subject.subject_name')
    subject_id=serializers.CharField(source="subject.id")
    batch_name=serializers.JSONField(source='batch.batch_name')

    class Meta:
        model = SubjectPractical
        fields=["subject_name","batch_year","prac_teacher_email","id","subject_id","batch_name"]

class StudUserSerializer(serializers.ModelSerializer):
    name = serializers.JSONField(source='myuser.name')
    email = serializers.JSONField(source='myuser.email')
    age = serializers.JSONField(source='myuser.age')
    gender = serializers.JSONField(source='myuser.gender')
    sapId = serializers.JSONField(source='myuser.sapId')
    mobile = serializers.JSONField(source='myuser.mobile')
    year = serializers.JSONField(source='myuser.year')
    class Meta:
        model = User
        fields=['email','id',"name","age","gender","sapId","mobile","year"] 
        #fields="__all__"
class TeacherUserSerializer(serializers.ModelSerializer):
    name = serializers.JSONField(source='myuser.name')
    email = serializers.JSONField(source='myuser.email')
    age = serializers.JSONField(source='myuser.age')
    gender = serializers.JSONField(source='myuser.gender')
    mobile = serializers.JSONField(source='myuser.mobile')
    class Meta:
        model = User
        fields=['email','id',"name","age","gender","mobile","is_staff"] 
        #fields="__all__"

class UserTSerializer(serializers.ModelSerializer):
    name = serializers.JSONField(source='myuser.name')
    email = serializers.JSONField(source='myuser.email')
    class Meta:
        model = User
        fields=['email','id','is_staff',"name"] 
class UserTMTMSerializer(serializers.ModelSerializer):
    phone = serializers.JSONField(source='mobile')
    user_id = serializers.JSONField(source='user.id')
    class Meta:
        model = MyUser
        fields=['user_id','email','sapId','phone',"name"] 
class UserPermissionSerializer(serializers.ModelSerializer):
    name = serializers.JSONField(source='myuser.name')
    email = serializers.JSONField(source='myuser.email')
    canCreateBatch = serializers.JSONField(source='myuser.canCreateBatch')
    canCreateSubject = serializers.JSONField(source='myuser.canCreateSubject')
    canCreateFeedbackForm = serializers.JSONField(source='myuser.canCreateFeedbackForm')
    class Meta:
        model = User
        fields=['email','id',"name","canCreateBatch","canCreateSubject","canCreateFeedbackForm"] 

class FeedbackInst(serializers.ModelSerializer):
    label=serializers.CharField(source="instance_name")
    value=serializers.CharField(source="id")
    selected=serializers.BooleanField(source="is_selected")
    class Meta:
        model = FeedbackInstance
        fields=["label","value","is_selected","is_latest","selected"]
    def to_representation(self, data):
        data = super(FeedbackInst, self).to_representation(data)
        data['label'] = "{} {}".format(data["label"],"(Latest)") if data.get('is_latest') == True else data["label"]
        return data
        
class OtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Otp
        fields='__all__'

class FeedbackFormSerializer(serializers.ModelSerializer):
    subject_name = serializers.JSONField(source='subject.subject_name')
    is_selected = serializers.SerializerMethodField()

    def get_is_selected(self, obj):
        if obj.instance:
            return obj.instance.is_selected
        return False

    class Meta:
        model = FeedbackForm
        fields = ["id", "subject_name", "is_alive", "is_theory", "year", "due_date", "batch_list", "is_selected"]

class FeedbackUserConnectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackUserConnector
        fields='__all__'
class FeedbackUserFConnectorSerializer(serializers.ModelSerializer):
    student = serializers.JSONField(source='student.username')
    student_name = serializers.JSONField(source='student.myuser.name')
    teacher_name = serializers.JSONField(source='form.teacher.myuser.name')
    teacher_email = serializers.JSONField(source='form.teacher.username')
    subject = serializers.JSONField(source='form.subject.subject_name')
    due_date = serializers.JSONField(source='form.due_date')
    year = serializers.JSONField(source='form.year')
    is_theory = serializers.JSONField(source='form.is_theory')
    is_alive = serializers.JSONField(source='form.is_alive')
    subject_id = serializers.JSONField(source='form.subject.id')
    form_id = serializers.JSONField(source='form.id')
    class Meta:
        model = FeedbackUserConnector
        fields=["student","is_filled","user_feedback","teacher_name","subject","due_date","year","is_theory","is_alive","teacher_email","subject_id","form_id","student_name"]
class FeedbackUserFteacherConnectorSerializer(serializers.ModelSerializer):
    student_name = serializers.JSONField(source='student.myuser.name')
    class Meta:
        model = FeedbackUserConnector
        fields=["is_filled","user_feedback","student_name"]

class SubjectTheorySerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.subject_name")
    batch_id = serializers.PrimaryKeyRelatedField(source="batch", read_only=True)
    batch_name = serializers.JSONField(source="batch.batch_name")
    batch_year = serializers.JSONField(source="batch.year")
    sub_teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = SubjectTheory
        fields = [
            "id",
            "subject_name",
            "batch_id",
            "batch_name",
            "batch_year",
            "sub_teacher_name",
        ]

    def get_sub_teacher_name(self, obj):
        teacher_ids = obj.sub_teacher_email
        teachers = MyUser.objects.filter(user_id__in=teacher_ids)
        teacher_names = [teacher.name for teacher in teachers]
        return teacher_names

class SubjectPracticalSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.subject_name")
    batch_id = serializers.PrimaryKeyRelatedField(source="batch", read_only=True)
    batch_name = serializers.JSONField(source="batch.batch_name")
    batch_year = serializers.JSONField(source="batch.year")
    prac_teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = SubjectPractical
        fields = [
            "id",
            "subject_name",
            "batch_id",
            "batch_name",
            "batch_year",
            "prac_teacher_name",
        ]

    def get_prac_teacher_name(self, obj):
        teacher_ids = obj.prac_teacher_email
        teachers = MyUser.objects.filter(user_id__in=teacher_ids)
        teacher_names = [teacher.name for teacher in teachers]
        return teacher_names

class SubjectSerializer(serializers.ModelSerializer):
    instance_name = serializers.CharField(source="instance.name", read_only=True)
    is_selected = serializers.BooleanField(source="instance.is_selected", read_only=True)
    theory_subject = serializers.SerializerMethodField()
    practical_subject = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['id', 'subject_name', 'instance_name', 'is_selected', 'theory_subject', 'practical_subject']

    def get_theory_subject(self, obj):
        # Fetch and serialize the related theory subjects for the current subject
        theory_subjects = obj.subjecttheory_set.all()
        serializer = SubjectTheorySerializer(theory_subjects, many=True)
        return serializer.data

    def get_practical_subject(self, obj):
        # Fetch and serialize the related practical subjects for the current subject
        practical_subjects = obj.subjectpractical_set.all()
        serializer = SubjectPracticalSerializer(practical_subjects, many=True)
        return serializer.data
