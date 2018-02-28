# -*- coding:utf-8 -*-
__author__ = 'zhangyue'

from django import forms

from .validators import jpg_validator, poster_image_size_validator
from .models import PreUser, ApplicationQuestion, ApplicationOption, Source, \
    PreUserTrack, Contract, PreUserContract, Poster
from .models import PREUSER_GENDER_CHOICES, PREUSER_GRADE_CHOICES, PREUSER_LEVEL_CHOICES, CONTRACT_PERIOD_CHOICES
from .utils import get_referral_user_name_with_user


# 管理者添加的preuser表
class PreuserCreateForm(forms.ModelForm):
    name = forms.CharField(label='姓名',
                           widget=forms.TextInput(attrs={'placeholder': '姓名 (必填)'}))
    mobile = forms.CharField(label='电话', widget=forms.TextInput(attrs={'placeholder': '电话 (必填)'}),
                             error_messages={'unique': u'该电话已存在'})
    gender = forms.ChoiceField(choices=PREUSER_GENDER_CHOICES, label='性别', widget=forms.RadioSelect, required=False)
    wx = forms.CharField(label='微信号', widget=forms.TextInput(attrs={'placeholder': '微信号'}), required=False)

    class Meta:
        model = PreUser
        fields = ['name', "mobile", "gender", "province", "city", "wx"]


# 管理者更新的preuser表
class PreuserUpdateAdminForm(PreuserCreateForm):
    grade = forms.ChoiceField(choices=PREUSER_GRADE_CHOICES, label='意向', required=False)
    source = forms.ModelChoiceField(queryset=Source.objects.filter(is_show=True), label='来源', required=False)

    referral_user_id = forms.CharField(required=False,
                                       widget=forms.TextInput(attrs={'onchange': 'get_referral_user_name();'}),
                                       help_text="", label="转介人id")

    def __init__(self, *args, **kwargs):
        super(PreuserUpdateAdminForm, self).__init__(*args, **kwargs)
        referral_user_name = u"无"
        if self.instance.referral_user_id:
            self.initial['referral_user_id'] = self.instance.referral_user_id
            referral_user_name = get_referral_user_name_with_user(self.instance.referral_user.id)
            if not referral_user_name:
                referral_user_name = u"无"
        self.fields[
            'referral_user_id'].help_text = u"(转介人：<text id='referral_user_name'>" + referral_user_name + u"</text>)"

    class Meta:
        model = PreUser
        fields = ['name', "mobile", "gender", "grade", "wx", "birthday", "province", "city", "address", 'source',
                  "referral_user_id", "email", "job", "hobby", "married", "children", "job_info", "family"]


# 用户自己更新的preuser表
class PreuserUpdateUserForm(PreuserCreateForm):
    birthday = forms.DateField(label='出生日期', help_text='格式：2017-01-01', error_messages={'invalid': u'日期格式不正确'})

    class Meta:
        model = PreUser
        fields = ['name', "mobile", "gender", "wx", "birthday", "province", "city", "address", ]


class PreuserSearchForm(forms.ModelForm):
    level = forms.ChoiceField(choices=PREUSER_LEVEL_CHOICES, label='级别', required=False)
    grade = forms.ChoiceField(choices=PREUSER_GRADE_CHOICES,label='意愿',required=False)
    name = forms.CharField(label='姓名', required=False)
    mobile = forms.CharField(label='电话', required=False)
    source_name = forms.CharField(label='报名来源', required=False)
    referral_name = forms.CharField(required=False, label="转介人姓名")

    class Meta:
        model = PreUser
        fields = ['level', 'grade','name', "mobile", 'source_name', 'referral_name', "province", "city", ]


# ===source===
class SourceForm(forms.ModelForm):
    class Meta:
        model = Source
        fields = ['name', 'reg_name', 'is_show', 'is_poster']


# ===preuser track===
class PreuserTrackForm(forms.ModelForm):
    class Meta:
        model = PreUserTrack
        fields = ['tracked_at', 'info']


# ===application question======
class ApplicationQuestionCreateForm(forms.ModelForm):
    class Meta:
        model = ApplicationQuestion
        fields = ['name', "order_by", "input_type"]


class ApplicationOptionCreateForm(forms.ModelForm):
    class Meta:
        model = ApplicationOption
        fields = ['name', "order_by"]


# =====contract======
class ContractForm(forms.ModelForm):
    period = forms.ChoiceField(choices=CONTRACT_PERIOD_CHOICES, label="周期")

    class Meta:
        model = Contract
        fields = ['name', "period", "duration", "price"]


# ===== preuser contract======
class PreuserContractForm(forms.ModelForm):
    class Meta:
        model = PreUserContract
        fields = ['contract', "price", "paid_at", "study_at", "info"]


# ====== poster ======

class PosterCreateForm(forms.ModelForm):
    photo = forms.ImageField(validators=[jpg_validator, poster_image_size_validator])

    class Meta:
        model = Poster
        fields = ["photo"]


class PosterUpdateForm(forms.ModelForm):
    qrcode_width = forms.IntegerField(min_value=1, label='二维码宽度')
    qrcode_height = forms.IntegerField(min_value=1, label='二维码高度')

    class Meta:
        model = Poster
        fields = ["qrcode_width", "qrcode_height", "qrcode_pos_x", "qrcode_pos_y", "qrcode_color", "is_show"]
