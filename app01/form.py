from django import forms
from django.forms import widgets
from django.forms import ValidationError
from app01 import models
import re


def mobile_validate(value):
    mobile_re = re.compile(r'^(13[0-9]|15[012356789]|17[678]|18[0-9]|14[57])[0-9]{8}$')
    if not mobile_re.match(value):
        raise ValidationError('手机号码格式错误')


class RegForm(forms.Form):
    username = forms.CharField(
        label='用户名',
        max_length=16,
        widget=widgets.TextInput(attrs={'class':'form-control'}),
        error_messages={
            'required': '不能为空',
        }
    )
    password = forms.CharField(
        label='密码',
        min_length=6,
        widget=widgets.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={
            'required':'不能为空',
            'invalid': '格式错误',
            'min_length': '密码最短为6位'
        }
    )
    r_password = forms.CharField(
        label='确认密码',
        min_length=6,
        widget=widgets.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={
            'required':'不能为空',
            'invalid': '格式错误',
            'min_length': '密码最短为6位'
        }
    )
    phone = forms.CharField(
        label='手机号码',
        validators=[mobile_validate, ],
        error_messages={'required': '手机不能为空'},
        widget=widgets.TextInput(attrs={'class': "form-control"}),
    )

    email = forms.EmailField(
        label='邮箱',
        widget=widgets.EmailInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
        }
    )
    sex = forms.fields.ChoiceField(
        choices=((1, "男"), (2, "女")),
        label="性别",
        initial=1,
        widget=forms.widgets.Select()
    )

    def clean(self):
        password = self.cleaned_data.get('password')
        rel_password = self.cleaned_data.get("r_password")
        if rel_password and password != rel_password:
            self.add_error("r_password", ValidationError('两次密码不一致'))
        else:
            return self.cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        rep = models.UserInfo.objects.filter(username=username)
        if rep:
            self.add_error("username", ValidationError('此用户已被注册'))
        else:
            return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        rep = models.UserInfo.objects.filter(email=email)
        if rep:
            self.add_error("email", ValidationError('此邮箱已被注册'))
        else:
            return email
