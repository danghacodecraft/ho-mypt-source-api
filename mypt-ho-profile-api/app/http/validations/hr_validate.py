from rest_framework.serializers import *
from app.core.helpers.utils import *


class EmpInDepartmentValidate(Serializer):
    childDepart = ListField(required=True)


class EmpInParentDepartmentValidate(Serializer):
    parentDepart = ListField(required=True)


class ContractValidate(Serializer):
    contract = CharField()


class EmpCodeValidate(Serializer):
    code = CharField()

    def validate_code(self, value):
        if len(value) != 8:
            raise ValidationError("Mã nhân viên phải đủ 8 số!")


class DateSearchValidate(Serializer):
    month = IntegerField()
    year = IntegerField()


class EmpFieldsListValidate(Serializer):
    email = ListField()
    fields = ListField()


class CodeFieldsListValidate(Serializer):
    code = ListField()
    fields = ListField()


class AddSafeCardValidate(Serializer):
    # certificate = CharField()
    empCode = CharField()
    # pictureCertificate = CharField()
    dateCertificate = DateField()
    expirationDate = DateField()
    trainingStartDate = DateField()
    trainingEndDate = DateField()
    # trainingGroup = CharField()
    # statusCertificate = CharField()


class EmpCodeSafeCardValidate(Serializer):
    # certificate = CharField()
    empCode = CharField(allow_null=True, allow_blank=True)

    def validate_empCode(self, value):
        if value == "" or value is None:
            raise ValidationError("Mã nhân viên không được để trống")
        if len(value) != 8:
            raise ValidationError("Mã nhân viên phải đủ 8 số!")


class DateCertificateSafeCardValidate(Serializer):
    dateCertificate = CharField(allow_null=True, allow_blank=True)

    def validate_dateCertificate(self, value):
        if is_null_or_empty(value):
            raise ValidationError("Ngày cấp thẻ ATLĐ không được để trống")
        if not check_input_format_date_2(value):
            raise ValidationError("Ngày cấp thẻ ATLĐ không đúng định dạng")


class ExpirationDateSafeCardValidate(Serializer):
    # expirationDate = DateField()
    expirationDate = CharField(allow_null=True, allow_blank=True)

    def validate_expirationDate(self, value):
        if is_null_or_empty(value):
            raise ValidationError("Ngày hết hạn ATLĐ không được để trống")
        if not check_input_format_date_2(value):
            raise ValidationError("Ngày hết hạn ATLĐ không đúng định dạng")


class TrainingStartDateSafeCardValidate(Serializer):
    # expirationDate = DateField()
    trainingStartDate = CharField(allow_null=True, allow_blank=True)

    def validate_trainingStartDate(self, value):
        if is_null_or_empty(value):
            raise ValidationError("Ngày bắt đầu đào tạo không được để trống")
        if not check_input_format_date_2(value):
            raise ValidationError("Ngày bắt đầu đào tạo không đúng định dạng")


class TrainingEndDateSafeCardValidate(Serializer):
    trainingEndDate = CharField(allow_null=True, allow_blank=True)

    def validate_trainingEndDate(self, value):
        if is_null_or_empty(value):
            raise ValidationError("Ngày kết thúc đào tạo không được để trống")
        if not check_input_format_date_2(value):
            raise ValidationError("Ngày kết thúc đào tạo không đúng định dạng")


class AddSafeCardValidate_new(Serializer):
    # certificate = CharField()
    empCode = CharField(required=True)
    # pictureCertificate = CharField()
    dateCertificate = DateField()
    expirationDate = DateField()
    trainingStartDate = DateField()
    trainingEndDate = DateField()

    # trainingGroup = CharField()
    # statusCertificate = CharField()
    def validate_empCode(self, value):
        if len(value) != 8:
            raise ValidationError("Mã nhân viên phải đủ 8 số!")

    def validate_dateCertificate(self, value):
        if not check_input_format_date(value):
            raise ValidationError("Ngày cấp thẻ ATLĐ không đúng định dạng")

    def validate_expirationDate(self, value):
        if is_null_or_empty(value):
            raise ValidationError("Vui lòng nhập ngày hết hạn ATLĐ")
        if not check_input_format_date(value):
            raise ValidationError("Ngày hết hạn ATLĐ không đúng định dạng")

    def validate_trainingStartDate(self, value):
        if is_null_or_empty(value):
            raise ValidationError("Vui lòng nhập ngày bắt đầu đào tạo")
        if not check_input_format_date(value):
            raise ValidationError("Ngày bắt đầu đào tạo không đúng định dạng")

    def validate_trainingEndDate(self, value):
        if is_null_or_empty(value):
            raise ValidationError("Vui lòng nhập ngày kết thúc đào tạo")
        if not check_input_format_date(value):
            raise ValidationError("Ngày kết thúc đào tạo không đúng định dạng")


class EmailValidate(Serializer):
    email = EmailField()


class ListCodeValidate(Serializer):
    code = ListField()


class IdValidate(Serializer):
    id = IntegerField()


class idValidate(Serializer):
    id = IntegerField()

