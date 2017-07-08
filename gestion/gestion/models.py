from django.db import models


class Group(models.Model):
    """Groups Table. グループを表す。名前はグループ名(会社名)。"""
    name = models.CharField(max_length=30)

    def __repr__(self):
        return f"<Group (id='{self.id}' name='{self.name}')>"


class User(models.Model):
    """Users Table."""
    GENDER_CHOICES = (
        ('M', 'male'),
        ('F', 'female'), # ('O', 'other'),  Fitbit的に選べなさそうなので後で
    )
    AUTHORITY_CHOICES = (
        ('U', 'user'),
        ('A', 'admin'),
    )
    email = models.EmailField()
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    password = models.CharField(max_length=100)
    token = models.CharField(max_length=1024)
    authority = models.CharField(max_length=1, choices=AUTHORITY_CHOICES)
    icon = models.ImageField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __repr__(self):
        return f"<User (id='{self.id}' group='{self.group.name}' name='{self.first_name}')>"


class FitbitAccount(models.Model):
    """FitbitAccounts Table.
    ユーザ毎のFitbitアカウントデータを格納する。
    """
    fitbit_id = models.CharField(max_length=6)
    fitbit_access_token = models.CharField(max_length=1024)
    refresh_token = models.CharField(max_length=1024)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __repr__(self):
        return f"<FitbitAccount (id='{self.id}' fitbit_id='{self.fitbit_id}')>"


class Stress(models.Model):
    """Stress Table.
    ストレス計測ライブラリで算出したストレスを格納する。
    ユーザ毎に1日1行のデータが発生する。
    """
    date = models.DateField()
    stress = models.BooleanField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __repr__(self):
        return f"<Stress (id='{self.id}' stress='{self.stress}')>"


class AttendanceRecod(models.Model):
    """AttendanceRecods Table. 出退勤記録テーブル。"""
    begin = models.DateTimeField()
    end = models.DateTimeField(null=True)  # 退勤時にテーブルを更新するためにnullable
    user = models.ForeignKey(User, on_delete=models.CASCADE)
