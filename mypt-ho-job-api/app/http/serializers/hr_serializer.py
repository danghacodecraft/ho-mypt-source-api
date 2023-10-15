import re

from rest_framework import serializers
from ..models.hr import *
from ...configs.service_api_config import SERVICE_CONFIG
from ...core.helpers import helper, utils
from rest_framework.serializers import *
from app.configs import app_settings
import ast
from django.conf import settings as project_settings

from ...core.helpers.helper import call_api



MARITAL_STATUS_TYPES = (
    (0, 'Chưa kết hôn'),
    (1, 'Đã kết hôn'),
    (2, 'Đã ly hôn')
)


class EmployeeSerializer(Serializer):
    email = serializers.CharField(required=False, allow_null=True)
    birthday = serializers.DateField(format='%d/%m/%Y', required=False, allow_null=True)
    day = serializers.CharField(required=False, allow_null=True)
    month = serializers.CharField(required=False, allow_null=True)
    year = serializers.CharField(required=False, allow_null=True)
    mstcn = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    sex = serializers.CharField(required=False, allow_null=True)
    cmnd = serializers.CharField(required=False, allow_null=True)
    code = serializers.CharField(source='emp_code', required=False, allow_null=True)
    name = serializers.CharField(source='emp_name', required=False, allow_null=True)
    jobTitle = serializers.CharField(source='job_title', required=False, allow_null=True, allow_blank=True)
    childDepart = serializers.CharField(source='child_depart', required=False, allow_null=True)
    mobilePhone = serializers.CharField(source='mobile_phone', required=False, allow_null=True)
    dependentInfo = serializers.CharField(source='dependent_info', required=False, allow_null=True, allow_blank=True)
    contractType = serializers.CharField(source='contract_type', required=False, allow_null=True, allow_blank=True)
    contractCode = serializers.CharField(source='contract_code', required=False, allow_null=True, allow_blank=True)
    contractBegin = serializers.DateField(format='%d/%m/%Y', source='contract_begin', required=False, allow_null=True)
    contractEnd = serializers.DateField(format='%d/%m/%Y', source='contract_end', required=False, allow_null=True)
    accountNumber = serializers.CharField(source='account_number', required=False, allow_null=True)
    typeSalary = serializers.CharField(source='type_salary', required=False, allow_null=True)
    statusWorking = serializers.IntegerField(source='status_working', required=False, allow_null=True)
    dateJoinCompany = serializers.DateField(format='%d/%m/%Y', source='date_join_company', required=False,
                                            allow_null=True)
    dateQuitJob = serializers.DateField(format='%d/%m/%Y', source='date_quit_job', required=False, allow_null=True)
    updateTime = serializers.DateTimeField(source='update_time', required=False, allow_null=True)
    updateBy = serializers.CharField(source='update_by', required=False, allow_null=True)
    avatarImg = serializers.CharField(source='avatar_img', required=False, allow_null=True)
    idUser = serializers.CharField(source='id_user', required=False, allow_null=True)

    placeOfBirth = serializers.CharField(source='place_of_birth', required=False, allow_null=True, allow_blank=True)
    nationality = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    date = serializers.DateField(format='%d/%m/%Y', source='ngay_cap_cmnd', required=False, allow_null=True)
    issuedAt = serializers.CharField(source='noi_cap_cmnd', required=False, allow_null=True, allow_blank=True)
    placeOfPermanent = serializers.CharField(source='place_of_permanent', required=False, allow_null=True,
                                             allow_blank=True)
    degree = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    workplace = serializers.CharField(required=False, allow_null=True, max_length=255, allow_blank=True,
                                      error_messages={
                                          "max_length": "Vượt quá độ dài tối đa, nơi làm việc là mã tòa nhà/văn phòng"
                                      })
    level = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    socialInsuranceSalaryPay = serializers.CharField(source='social_insurance_salary_pay', required=False,
                                                     allow_null=True, allow_blank=True)
    placeToJoinSocialInsurance = serializers.CharField(source='place_to_join_social_insurance', required=False,
                                                       allow_null=True, allow_blank=True)
    taxIdentificationPlace = serializers.CharField(source='tax_identification_place', required=False, allow_null=True,
                                                   allow_blank=True)
    taxIdentificationDate = serializers.DateField(format='%d/%m/%Y',
                                                  source='tax_identification_date',
                                                  required=False,
                                                  allow_null=True)

    maritalStatus = serializers.ChoiceField(source='marital_status',
                                            choices=MARITAL_STATUS_TYPES,
                                            default=0,
                                            error_messages={
                                                'invalid_choice': 'Tình trạng hôn nhân chấp nhận các giá trị sau: Độc thân (0), Đã kết hôn (1), Đã ly hôn (2)'})
    bankName = serializers.CharField(source='bank_name', required=False, allow_null=True, allow_blank=True)
    healthInsurance = serializers.CharField(source='health_insurance', required=False, allow_null=True,
                                            allow_blank=True)
    socialInsurance = serializers.CharField(source='social_insurance', required=False, allow_null=True,
                                            allow_blank=True)

    foxpay = serializers.CharField(required=False, allow_null=True)
    fullChildDepart = serializers.SerializerMethodField()
    parentDepart = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):

        self.contracts_type = kwargs.pop('contracts_type', None)

        fields = kwargs.pop('fields', None)

        VN = kwargs.pop('VN', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if VN is not None:
            fields = []
            for key in VN:
                fields.append(key)
            existing = set(self.fields)
            allowed = set(fields)
            for field_name in fields:
                self.fields[VN[field_name]] = self.fields.pop(field_name)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def to_representation(self, instance):
        data = super(EmployeeSerializer, self).to_representation(instance)

        if "Giới tính" in data:
            sex = data["Giới tính"]
            if sex == "M":
                data.update({"Giới tính": "Nam"})
            elif sex == "F":
                data.update({"Giới tính": "Nữ"})
        return data

class AccountingSalarySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, source="luong_hoach_toan_id")
    email = serializers.CharField(required=False,
                                  allow_blank=True, allow_null=True)
    month = serializers.CharField(required=False,
                                  allow_blank=True, allow_null=True)
    monthSalary = serializers.CharField(required=False, source="luong_thang",
                                        allow_blank=True, allow_null=True)
    probationarySalary = serializers.CharField(required=False, source="luong_thu_viec",
                                               allow_blank=True, allow_null=True)
    vocationalTrainingSalary = serializers.CharField(required=False, source="luong_dao_tao_nghe",
                                                     allow_blank=True, allow_null=True)
    formulaSalary = serializers.CharField(required=False, source="luong_cong_thuc",
                                          allow_blank=True, allow_null=True)
    socialInsuranceSalaryPay = serializers.CharField(required=False, source="luong_dong_bhxh",
                                                     allow_blank=True, allow_null=True)
    healthInsurance = serializers.CharField(required=False, source="bhyt",
                                            allow_blank=True, allow_null=True)
    socialInsurance = serializers.CharField(required=False, source="bhxh",
                                            allow_blank=True, allow_null=True)
    accidentInsurance = serializers.CharField(required=False, source="bhtn",
                                              allow_blank=True, allow_null=True)
    expenseCD = serializers.CharField(required=False, source="kinh_phi_cd",
                                      allow_blank=True, allow_null=True)
    familyAllowances = serializers.CharField(required=False, source="giam_tru_gia_canh",
                                             allow_blank=True, allow_null=True)
    numberOfDependents = serializers.CharField(required=False, source="sl_nguoi_phu_thuoc",
                                               allow_blank=True, allow_null=True)
    reductionMinusNPT = serializers.CharField(required=False, source="muc_giam_tru_npt",
                                              allow_blank=True, allow_null=True)
    personalIncomeTax = serializers.CharField(required=False, source="thue_thu_nhap_ca_nhan",
                                              allow_blank=True, allow_null=True)
    otherOffsetAfterTax = serializers.CharField(required=False, source="bu_tru_khac_sau_thue",
                                                allow_blank=True, allow_null=True)
    taxRefundPersonalIncomeTax = serializers.CharField(required=False, source="truy_thu_hoan_thue_TNCN",
                                                       allow_blank=True, allow_null=True)
    arrearsHealthInsurance = serializers.CharField(required=False, source="truy_thu_BHYT",
                                                   allow_blank=True, allow_null=True)
    salaryAdvance = serializers.CharField(required=False, source="tam_ung",
                                          allow_blank=True, allow_null=True)
    refundAdvance = serializers.CharField(required=False, source="hoan_ung",
                                          allow_blank=True, allow_null=True)
    salaryReceived = serializers.CharField(required=False, source="luong_thuc_nhan",
                                           allow_blank=True, allow_null=True)
    formOfPayment = serializers.CharField(required=False, source="hinh_thuc_chi_tra",
                                          allow_blank=True, allow_null=True)
    updateTime = serializers.CharField(required=False, source="update_time",
                                       allow_blank=True, allow_null=True)
    updateBy = serializers.CharField(required=False, source="update_by",
                                     allow_blank=True, allow_null=True)

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def to_representation(self, instance):
        app_env = project_settings.APP_ENVIRONMENT
        employee = call_api(
            host=SERVICE_CONFIG["HO-PROFILE"][app_env],
            func=SERVICE_CONFIG["HO-PROFILE"]["get-emp-code-and-name-from-email"]["func"],
            method=SERVICE_CONFIG["HO-PROFILE"]["get-emp-code-and-name-from-email"]["method"],
            data={'email': instance.email}
        )
        # employee = Employee.objects.filter(email=instance.email).values('emp_name', 'emp_code')
        emp_name = ""
        emp_code = ""
        if employee is not None and len(employee) > 0:
            emp_name = employee[0]["emp_name"]
            emp_code = employee[0]["emp_code"]
        return {
            'emp_code': emp_code,
            'emp_name': emp_name,
            'email': instance.email,
            'thang': instance.month,
            'luong_thang': utils.decrypt_aes_salary(instance.luong_thang),
            'luong_thu_viec': utils.decrypt_aes_salary(instance.luong_thu_viec),
            'luong_dao_tao_nghe': utils.decrypt_aes_salary(instance.luong_dao_tao_nghe),
            'luong_cong_thuc': utils.decrypt_aes_salary(instance.luong_cong_thuc),
            'luong_dong_BHXH': utils.decrypt_aes_salary(instance.luong_dong_bhxh),
            'BHYT': utils.decrypt_aes_salary(instance.bhyt),
            'BHXH': utils.decrypt_aes_salary(instance.bhxh),
            'BHTN': utils.decrypt_aes_salary(instance.bhtn),
            'kinh_phi_CD': utils.decrypt_aes_salary(instance.kinh_phi_cd),
            'giam_tru_gia_canh': utils.decrypt_aes_salary(instance.giam_tru_gia_canh),
            'sl_nguoi_phu_thuoc': utils.decrypt_aes_salary(instance.sl_nguoi_phu_thuoc),
            'muc_giam_tru_NPT': utils.decrypt_aes_salary(instance.muc_giam_tru_npt),
            'thue_thu_nhap_ca_nhan': utils.decrypt_aes_salary(instance.thue_thu_nhap_ca_nhan),
            'bu_tru_khac_sau_thue': utils.decrypt_aes_salary(instance.bu_tru_khac_sau_thue),
            'truy_thu_hoan_thue_tncn': utils.decrypt_aes_salary(
                instance.truy_thu_hoan_thue_TNCN),
            'truy_thu_BHYT': utils.decrypt_aes_salary(instance.truy_thu_BHYT),
            'tam_ung': utils.decrypt_aes_salary(instance.tam_ung),
            'hoan_ung': utils.decrypt_aes_salary(instance.hoan_ung),
            'luong_thuc_nhan': utils.decrypt_aes_salary(instance.luong_thuc_nhan),
            'hinh_thu_chi_tra': instance.hinh_thuc_chi_tra
        }

    def validate_month(self, month):
        salary_month = self.context.get("salary_month", None)
        if month is None or month == '':
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "tháng rỗng"})

        if not helper.check_data_with_re("^(1[0-2]|0[1-9])-[0-9]{4}$", month):
            raise serializers.ValidationError({"type": "FORMAT", "err_msg": "lỗi định dạng tháng"})

        if salary_month and not month == salary_month:
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lỗi dữ liệu tháng không trùng với tháng lương"})

        return month

    def validate_email(self, email):
        if email is None or email == '':
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "email rỗng"})

        if not (helper.check_data_with_re("^phuongnam\.[a-zA-Z0-9]+[.]*[a-zA-Z0-9]*@fpt\.net$", email) \
                or helper.check_data_with_re("^[a-zA-Z0-9]+[.]*[a-zA-Z0-9]*@vienthongtin.com$", email)):
            raise serializers.ValidationError({"type": "FORMAT", "err_msg": "lỗi định dạng mail"})
        return email

    def validate_monthSalary(self, monthSalary):
        if monthSalary is None or monthSalary == '':
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lương tháng rỗng"})
        if not helper.is_digit(monthSalary):
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lỗi định dạng lương tháng"})
        return monthSalary

    def validate_probationarySalary(self, probationarySalary):
        if probationarySalary is None or probationarySalary == '':
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lương thử việc rỗng"})

        if not helper.is_digit(probationarySalary):
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lỗi định dạng lương thử việc"})
        return probationarySalary

    def validate_vocationalTrainingSalary(self, vocationalTrainingSalary):
        if vocationalTrainingSalary is None or vocationalTrainingSalary == '':
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lương đào tạo nghề rỗng"})

        if not helper.is_digit(vocationalTrainingSalary):
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lỗi định dạng lương đào tạo nghề"})
        return vocationalTrainingSalary

    def validate_formulaSalary(self, formulaSalary):
        if formulaSalary is None or formulaSalary == '':
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lương công thức rỗng"})

        if not helper.is_digit(formulaSalary):
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lỗi định dạng lương công thức"})
        return formulaSalary

    def validate_socialInsuranceSalaryPay(self, socialInsuranceSalaryPay):
        if socialInsuranceSalaryPay is None or socialInsuranceSalaryPay == '':
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lương đóng BHXH rỗng"})

        if not helper.is_digit(socialInsuranceSalaryPay):
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lỗi định dạng lương đóng BHXH"})
        return socialInsuranceSalaryPay

    def validate_healthInsurance(self, healthInsurance):
        if healthInsurance is None or healthInsurance == '':
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "BHYT rỗng"})
        if not helper.is_digit(healthInsurance):
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lỗi định dạng BHYT"})
        return healthInsurance

    def validate_socialInsurance(self, socialInsurance):
        if socialInsurance is None or socialInsurance == '':
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "BHXH rỗng"})
        if not helper.is_digit(socialInsurance):
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lỗi định dạng BHXH"})
        return socialInsurance

    def validate_accidentInsurance(self, accidentInsurance):
        if accidentInsurance is None or accidentInsurance == '':
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "BHTN rỗng"})
        if not helper.is_digit(accidentInsurance):
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lỗi định dạng BHTN"})
        return accidentInsurance

    def validate_expenseCD(self, expenseCD):
        if expenseCD is None or expenseCD == '':
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "kinh phí cd rỗng"})
        if not helper.is_digit(expenseCD):
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lỗi định dạng kinh phí cd"})
        return expenseCD

    def validate_familyAllowances(self, familyAllowances):
        if familyAllowances is None or familyAllowances == '':
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "giảm trừ gia cảnh rỗng"})
        if not helper.is_digit(familyAllowances):
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lỗi định dạng giảm trừ gia cảnh"})
        return familyAllowances

    def validate_numberOfDependents(self, numberOfDependents):
        if numberOfDependents is None or numberOfDependents == '':
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "số lượng người phụ thuộc rỗng"})
        if not helper.is_digit(numberOfDependents):
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lỗi định dạng số lượng người phụ thuộc"})
        return numberOfDependents

    def validate_reductionMinusNPT(self, reductionMinusNPT):
        if reductionMinusNPT is None or reductionMinusNPT == '':
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "mức giảm trừ ntp rỗng"})
        if not helper.is_digit(reductionMinusNPT):
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lỗi định dạng mức giảm trừ ntp"})
        return reductionMinusNPT

    def validate_personalIncomeTax(self, personalIncomeTax):
        if personalIncomeTax is None or personalIncomeTax == '':
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "thuế thu nhập cá nhân rỗng"})
        if not helper.is_digit(personalIncomeTax):
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lỗi định dạng thuế thu nhập cá nhân"})
        return personalIncomeTax

    def validate_otherOffsetAfterTax(self, otherOffsetAfterTax):
        if otherOffsetAfterTax is None or otherOffsetAfterTax == '':
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "bù trừ khác sau thuế rỗng"})
        if not helper.is_digit(otherOffsetAfterTax):
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lỗi định dạng bù trừ khác sau thuế"})
        return otherOffsetAfterTax

    def validate_taxRefundPersonalIncomeTax(self, taxRefundPersonalIncomeTax):
        if taxRefundPersonalIncomeTax is None or taxRefundPersonalIncomeTax == '':
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "truy thu hoàn thuế TNCN rỗng"})
        if not helper.is_digit(taxRefundPersonalIncomeTax):
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lỗi định dạng truy thu hoàn thuế TNCN"})
        return taxRefundPersonalIncomeTax

    def validate_arrearsHealthInsurance(self, arrearsHealthInsurance):
        if arrearsHealthInsurance is None or arrearsHealthInsurance == '':
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "truy thu BHYT rỗng"})
        if not helper.is_digit(arrearsHealthInsurance):
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lỗi định dạng truy thu BHYT"})
        return arrearsHealthInsurance

    def validate_salaryAdvance(self, salaryAdvance):
        if salaryAdvance is None or salaryAdvance == '':
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "tạm ứng rỗng"})
        if not helper.is_digit(salaryAdvance):
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lỗi định dạng tạm ứng"})
        return salaryAdvance

    def validate_refundAdvance(self, refundAdvance):
        if refundAdvance is None or refundAdvance == '':
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "hoàn ứng rỗng"})
        if not helper.is_digit(refundAdvance):
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lỗi định dạng hoàn ứng"})
        return refundAdvance

    def validate_salaryReceived(self, salaryReceived):
        if salaryReceived is None or salaryReceived == '':
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lương thực nhận rỗng"})
        if not helper.is_digit(salaryReceived):
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lỗi định dạng lương thực nhận"})
        return salaryReceived

    def validate_formOfPayment(self, formOfPayment):
        if formOfPayment is None or formOfPayment == '':
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "hình thức chi trả rỗng"})
        if not helper.is_digit(formOfPayment):
            raise serializers.ValidationError({"type": "FORMAT",
                                               "err_msg": "lỗi định dạng hình thức chi trả"})
        return formOfPayment

    def create(self, validated_data):
        validated_data["update_by"] = self.context.get("email")
        luong_thang = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                        validated_data.pop("luong_thang"))
        luong_thu_viec = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                           validated_data.pop("luong_thu_viec"))
        luong_dao_tao_nghe = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                               validated_data.pop("luong_dao_tao_nghe"))
        luong_cong_thuc = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                            validated_data.pop("luong_cong_thuc"))
        luong_dong_bhxh = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                            validated_data.pop("luong_dong_bhxh"))
        bhyt = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                 validated_data.pop("bhyt"))
        bhxh = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                 validated_data.pop("bhxh"))
        bhtn = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                 validated_data.pop("bhtn"))
        kinh_phi_cd = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                        validated_data.pop("kinh_phi_cd"))
        giam_tru_gia_canh = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                              validated_data.pop("giam_tru_gia_canh"))
        sl_nguoi_phu_thuoc = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                               validated_data.pop("sl_nguoi_phu_thuoc"))
        muc_giam_tru_npt = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                             validated_data.pop("muc_giam_tru_npt"))
        thue_thu_nhap_ca_nhan = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                                  validated_data.pop("thue_thu_nhap_ca_nhan"))
        bu_tru_khac_sau_thue = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                                 validated_data.pop("bu_tru_khac_sau_thue"))
        truy_thu_hoan_thue_TNCN = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                                    validated_data.pop("truy_thu_hoan_thue_TNCN"))
        truy_thu_BHYT = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                          validated_data.pop("truy_thu_BHYT"))
        tam_ung = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                    validated_data.pop("tam_ung"))
        hoan_ung = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                     validated_data.pop("hoan_ung"))
        luong_thuc_nhan = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                            validated_data.pop("luong_thuc_nhan"))

        accounting_salary = AccountingSalary.objects.create(**validated_data, luong_thang=luong_thang,
                                                            luong_thu_viec=luong_thu_viec,
                                                            luong_dao_tao_nghe=luong_dao_tao_nghe,
                                                            luong_cong_thuc=luong_cong_thuc,
                                                            luong_dong_bhxh=luong_dong_bhxh,
                                                            bhyt=bhyt, bhxh=bhxh, bhtn=bhtn,
                                                            kinh_phi_cd=kinh_phi_cd,
                                                            giam_tru_gia_canh=giam_tru_gia_canh,
                                                            sl_nguoi_phu_thuoc=sl_nguoi_phu_thuoc,
                                                            muc_giam_tru_npt=muc_giam_tru_npt,
                                                            thue_thu_nhap_ca_nhan=thue_thu_nhap_ca_nhan,
                                                            bu_tru_khac_sau_thue=bu_tru_khac_sau_thue,
                                                            truy_thu_hoan_thue_TNCN=truy_thu_hoan_thue_TNCN,
                                                            truy_thu_BHYT=truy_thu_BHYT, tam_ung=tam_ung,
                                                            hoan_ung=hoan_ung, luong_thuc_nhan=luong_thuc_nhan)
        return accounting_salary

    def update(self, instance, validated_data):
        if validated_data.get('email'):
            instance.email = validated_data.get('email')
        if validated_data.get('month'):
            instance.month = validated_data.get('month')
        if validated_data.get('luong_thang'):
            instance.luong_thang = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                                     validated_data.get('luong_thang'))
        if validated_data.get('luong_thu_viec'):
            instance.luong_thu_viec = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                                        validated_data.get('luong_thu_viec'))
        if validated_data.get('luong_dao_tao_nghe'):
            instance.luong_dao_tao_nghe = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                                            validated_data.get('luong_dao_tao_nghe'))
        if validated_data.get('luong_cong_thuc'):
            instance.luong_cong_thuc = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                                         validated_data.get('luong_cong_thuc'))
        if validated_data.get('luong_dong_bhxh'):
            instance.luong_dong_bhxh = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                                         validated_data.get('luong_dong_bhxh'))
        if validated_data.get('bhyt'):
            instance.bhyt = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                              validated_data.get('bhyt'))
        if validated_data.get('bhxh'):
            instance.bhxh = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                              validated_data.get('bhxh'))
        if validated_data.get('bhtn'):
            instance.bhtn = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                              validated_data.get('bhtn'))
        if validated_data.get('kinh_phi_cd'):
            instance.kinh_phi_cd = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                                     validated_data.get('kinh_phi_cd'))
        if validated_data.get('giam_tru_gia_canh'):
            instance.giam_tru_gia_canh = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                                           validated_data.get('giam_tru_gia_canh'))
        if validated_data.get('sl_nguoi_phu_thuoc'):
            instance.sl_nguoi_phu_thuoc = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                                            validated_data.get('sl_nguoi_phu_thuoc'))
        if validated_data.get('muc_giam_tru_npt'):
            instance.muc_giam_tru_npt = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                                          validated_data.get('muc_giam_tru_npt'))
        if validated_data.get('thue_thu_nhap_ca_nhan'):
            instance.thue_thu_nhap_ca_nhan = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                                               validated_data.get('thue_thu_nhap_ca_nhan'))
        if validated_data.get('bu_tru_khac_sau_thue'):
            instance.bu_tru_khac_sau_thue = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                                              validated_data.get('bu_tru_khac_sau_thue'))
        if validated_data.get('truy_thu_hoan_thue_TNCN'):
            instance.truy_thu_hoan_thue_TNCN = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                                                 validated_data.get('truy_thu_hoan_thue_TNCN'))
        if validated_data.get('truy_thu_BHYT'):
            instance.truy_thu_BHYT = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                                       validated_data.get('truy_thu_BHYT'))
        if validated_data.get('tam_ung'):
            instance.tam_ung = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                                 validated_data.get('tam_ung'))
        if validated_data.get('hoan_ung'):
            instance.hoan_ung = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                                  validated_data.get('hoan_ung'))
        if validated_data.get('luong_thuc_nhan'):
            instance.luong_thuc_nhan = utils.encrypt_aes(app_settings.SALARY_SECRET_KEY,
                                                         validated_data.get('luong_thuc_nhan'))
        if validated_data.get('hinh_thuc_chi_tra'):
            instance.hinh_thuc_chi_tra = validated_data.get('hinh_thuc_chi_tra')
        if validated_data.get('update_time'):
            instance.update_time = validated_data.get('update_time')
        update_by_email = self.context.get("email", None)
        print("email: ", update_by_email)
        if update_by_email is not None:
            instance.update_by = update_by_email

        instance.save()
        return instance

    class Meta:
        model = AccountingSalary
        fields = [
            "id", "email", "month", "monthSalary", "probationarySalary",
            "vocationalTrainingSalary", "formulaSalary", "socialInsuranceSalaryPay",
            "healthInsurance", "socialInsurance", "accidentInsurance", "expenseCD",
            "familyAllowances", "numberOfDependents", "reductionMinusNPT",
            "personalIncomeTax", "otherOffsetAfterTax", "taxRefundPersonalIncomeTax",
            "arrearsHealthInsurance", "salaryAdvance", "refundAdvance",
            "salaryReceived", "formOfPayment", "updateTime", "updateBy"
        ]


class HistorySalaryTypeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    email = serializers.CharField(required=False)
    month = serializers.CharField(required=False)
    typeSalary = serializers.CharField(required=False, source="type_salary")
    updateTime = serializers.DateTimeField(required=False, source="update_time")
    updateBy = serializers.CharField(required=False, source="update_by")
    region = EmployeeSerializer(many=True, fields=["childDepart"])

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        VN = kwargs.pop('VN', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if VN is not None:
            fields = []
            for key in VN:
                fields.append(key)
            existing = set(self.fields)
            allowed = set(fields)
            for field_name in fields:
                self.fields[VN[field_name]] = self.fields.pop(field_name)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = HistorySalaryType
        fields = [
            "id", "email", "month", "typeSalary", "updateTime", "updateBy", "region"
        ]


class SalaryDhSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = SalaryDh
        fields = [
            "luong_dh_id", "email", "month", "luong_cung", "ngay_cong",
            "luong_san_pham", "ngay_cong_thuc_te", "luong_ca_vu_tru_ES",
            "luong_ca_vu_ES", "luong_chat_luong", "clps", "cl_lap",
            "bao_hanh_chat_luong", "do_hai_long_KH", "phu_cap",
            "che_tai", "thu_chi_khac", "bu_tru_luong_thang_t_1",
            "khen_thuong", "cac_khoan_ho_tro_khac",
            "luong_san_pham_khac", "hoa_hong_ban_hang",
            "luong_thu_cuoc_khong_chuyen"
        ]


class SalaryIndoSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = SalaryIndo
        fields = [
            "luong_indo_id", "email", "month", "luong_cung",
            "ngay_cong", "luong_san_pham", "luong_bao_tri",
            "tong_ca_vu_bao_tri", "ngay_cong_thuc_te", "nsld",
            "luong_chat_luong", "phat_cl_phat_sinh",
            "roi_mang", "do_hai_long_KH", "ho_tro", "tien_gui_xe",
            "che_tai", "thu_chi_khac", "bu_tru_luong_thang_t_1",
            "khen_thuong", "cac_khoan_ho_tro_khac",
            "luong_thu_viec", "luong_san_pham_khac",
            "hoa_hong_ban_hang", "luong_thu_cuoc_khong_chuyen"
        ]


class SalaryABCDSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = SalaryABCD
        fields = [
            "luong_nhom_abcd_id", "email", "month",
            "luong_cung", "ngay_cong", "luong_kpis",
            "thu_chi_khac", "bu_tru_luong_thang_t_1",
            "khen_thuong", "cac_khoan_ho_tro_khac",
            "cac_khoan_bo_sung", "hoa_hong_ban_hang",
            "luong_thu_cuoc_khong_chuyen"
        ]


class SalaryTFSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = SalaryTF
        fields = [
            "luong_tf_id", "email", "month", "luong_cung",
            "ngay_cong", "luong_san_pham", "luong_tac_vu_TK_BT",
            "tong_tac_vu", "ngay_cong_thuc_te", "nsld",
            "luong_tac_vu_khac", "luong_kpis",
            "luong_chat_luong", "cl7n", "do_hai_long_KH",
            "roi_mang", "ho_tro_dia_ban", "che_tai",
            "thu_chi_khac", "bu_tru_luong_thang_t_1",
            "khen_thuong", "cac_khoan_ho_tro_khac",
            "luong_san_pham_khac", "hoa_hong_ban_hang",
            "luong_thu_cuoc_khong_chuyen"
        ]


class SalaryTKBTSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = SalaryTKBT
        fields = [
            "luong_tk_bt_id", "email", "month", "luong_cung",
            "ngay_cong", "luong_san_pham", "luong_tac_vu_TK_BT",
            "tong_tac_vu", "ngay_cong_thuc_te", "nsld",
            "luong_tac_vu_khac", "luong_kpis", "luong_chat_luong",
            "cl7n", "nha_tuyen", "roi_mang", "do_hai_long_KH",
            "che_tai", "thu_chi_khac", "bu_tru_luong_thang_t_1",
            "khen_thuong", "cac_khoan_ho_tro_khac",
            "luong_san_pham_khac", "hoa_hong_ban_hang",
            "luong_thu_cuoc_khong_chuyen", "luong_don_tru",
            "luong_bac_nghe", "he_so_tang_cuong", "so_pttb",
            "doanh_thu", "bt_kh_goi_cuoc_lon", "thuong_tk_bt_nhanh",
            "tra_ca_sai_hen", "thuong_cl7n_30n", "ghi_chu"
        ]


class SalaryFeeSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = SalaryFee
        fields = [
            "luong_thu_cuoc_id", "email", "month", "ty_le_thu_hoi",
            "thuc_thu", "luong_san_pham", "luong_theo_gia_tri_tien_thu",
            "luong_co_dinh", "thuong_phat", "chi_tieu",
            "thuong_phat_chi_tieu", "thuong_muc_3",
            "phat_khong_dat_chi_tieu", "thanh_toan_online",
            "roi_mang", "kpis_chi_nhanh", "thi_phan_bac", "luong_recare",
            "recare_tu_thu", "recare_thu_ho",
            "luong_recare_dao_han_ra_cuoc",
            "luong_thu_hoi_bill_bi_dong_ngay_20", "luong_kpdv",
            "thu_lao_thu_hoi_thiet_bi", "luong_thu_hoi_bill_cnqh",
            "luong_theo_chinh_sach", "luong_bk1_add_bill_tra_truoc_ngoai_cs",
            "kick_off", "cs_thu_hoi_bi_dong_dich_chuyen_httt_v5_t02", "ho_tro",
            "nhan_vien_moi", "nghi_thai_san", "che_tai", "thu_chi_khac",
            "bu_tru_luong_thang_t_1", "khen_thuong", "cac_khoan_ho_tro_khac",
            "luong_san_pham_khac", "hoa_hong_ban_hang"
        ]


class SalaryFTISerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = SalaryFTI
        fields = [
            "luong_fti_id", "email", "month", "luong_cung",
            "ngay_cong", "luong_san_pham", "luong_theo_au",
            "luong_trien_khai", "tong_tac_vu", "ngay_cong_thuc_te",
            "luong_tac_vu_khac", "luong_chat_luong", "luong_kpis",
            "phu_cap", "truc_su_kien", "ho_tro_dia_ban",
            "trach_nhiem", "che_tai", "thu_chi_khac",
            "bu_tru_luong_thang_t_1", "khen_thuong",
            "cac_khoan_ho_tro_khac", "luong_san_pham_khac",
            "hoa_hong_ban_hang", "luong_thu_cuoc_khong_chuyen"
        ]


class SalaryKeyIndoSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = SalaryKeyIndo
        fields = [
            "luong_key_indo_id", "email", "month", "luong_cung",
            "ngay_cong", "luong_san_pham", "thuong_nsld",
            "tong_cl_bao_tri", "ngay_cong_thuc_te", "nsld_ca_nhan",
            "thuong_chi_tieu_nhom", "nsld_nhom", "kpis", "cl_lap",
            "roi_mang", "do_hai_long_KH", "ho_tro", "tien_gui_xe",
            "dao_tao", "che_tai", "thu_chi_khac",
            "bu_tru_luong_thang_t_1", "khen_thuong",
            "cac_khoan_ho_tro_khac", "luong_san_pham_khac",
            "hoa_hong_ban_hang", "luong_thu_cuoc_khong_chuyen"
        ]


class SalaryTnOsSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = SalaryTnOs
        fields = [
            "luong_tn_os_id", "email", "month", "luong_cung",
            "ngay_cong", "luong_chat_luong",
            "nsld", "kpis", "cl_lap", "roi_mang",
            "do_hai_long_kh", "nhan_vien", "cldv",
            "che_tai", "thu_chi_khac", "bu_tru_luong_thang_t_1",
            "khen_thuong", "cac_khoan_ho_tro_khac",
            "cac_khoan_bo_sung", "hoa_hong_ban_hang",
            "luong_thu_cuoc_khong_chuyen"
        ]


class SalarySoSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = SalarySo
        fields = [
            "luong_so_id", "email", "month", "luong_cung", "ngay_cong",
            "luong_san_pham", "luong_tac_vu_bt", "tong_tac_vu",
            "ngay_cong_thuc_te", "nsld", "luong_tac_vu_khac",
            "luong_chat_luong", "kpis", "cl7n", "kh_roi_mang",
            "do_hai_long_kh", "ho_tro_kh_thanh_cong", "che_tai",
            "thu_chi_khac", "bu_tru_luong_thang_t_1", "khen_thuong",
            "cac_khoan_ho_tro_khac", "luong_san_pham_khac",
            "hoa_hong_ban_hang", "luong_thu_cuoc_khong_chuyen",
            "nha_ca", "khong_nhan_ca", "thuong_cl7n_30n"
        ]


class SalaryTestSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = SalaryTest
        fields = [
            "luong_test_id", "email", "month", "luong_cung", "ngay_cong",
            "luong_san_pham", "luong_tac_vu", "tong_tac_vu", "ngay_cong_thuc_te",
            "nsld", "luong_chat_luong", "kpis", "do_chinh_xac", "che_tai",
            "thu_chi_khac", "bu_tru_luong_thang_t_1", "khen_thuong",
            "cac_khoan_ho_tro_khac", "luong_san_pham_khac", "hoa_hong_ban_hang",
            "luong_thu_cuoc_khong_chuyen"
        ]


class SalaryDhTinSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = SalaryDhTin
        fields = [
            "luong_dh_tin_id", "email", "month", "luong_cung",
            "ngay_cong", "bac_dieu_hanh", "luong_san_pham",
            "ngay_cong_thuc_te", "luong_quy_mo_nhan_su",
            "so_ns_quan_ly", "luong_hieu_qua_nhan_su",
            "diem_nsld_trung_binh", "luong_chat_luong",
            "thuong_csat", "thuong_cem",
            "thuong_ty_le_clps_7n_sau_tkbt",
            "thuong_giu_chan_kh", "thuong_trien_khai_dung_hen",
            "thuong_bao_tri_dung_hen", "thuong_bao_tri_dut_diem",
            "phu_cap", "thu_nhap_khac", "che_tai", "thu_chi_khac",
            "bu_tru_luong_thang_t_1", "khen_thuong",
            "cac_khoan_ho_tro_khac", "luong_san_pham_khac",
            "hoa_hong_ban_hang", "luong_thu_cuoc_khong_chuyen",
            "ghi_chu_bu_tru_khac"
        ]


class SalaryTfTinSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = SalaryTfTin
        fields = [
            "luong_tf_tin_id", "email", "month", "luong_cung", "ngay_cong",
            "luong_san_pham", "luong_tac_vu_TK_BT", "tong_tac_vu",
            "ngay_cong_thuc_te", "nsld", "thuong_nsld",
            "phu_cap_ngoai_gio_lam_viec", "luong_goi_cuoc_cao",
            "luong_tac_vu_khac", "luong_kpis", "thuong_csat", "thuong_cem",
            "thuong_trien_khai_dung_hen", "thuong_bao_tri_dung_hen",
            "luong_chat_luong", "cl7n", "nha_tuyen", "kh_roi_mang",
            "ty_le_clps_block", "phu_cap_di_chuyen", "che_tai", "thu_nhap_khac",
            "thi_dua", "cac_khoan_thu_nhap_khac", "thu_chi_khac",
            "bu_tru_luong_thang_t_1", "khen_thuong", "cac_khoan_ho_tro_khac",
            "luong_san_pham_khac", "hoa_hong_ban_hang",
            "luong_thu_cuoc_khong_chuyen", "ghi_chu_bu_tru_khac"
        ]


class SalaryTkbtTinSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = SalaryTkbtTin
        fields = [
            "luong_tkbt_tin_id", "email", "month", "luong_cung", "ngay_cong",
            "luong_san_pham", "luong_nang_suat", "ngay_cong_thuc_te",
            "tong_diem_nsld", "nsld", "thuong_nsld", "phu_cap_ngoai_gio_lam_viec",
            "luong_goi_cuoc_cao", "luong_tac_vu_khac", "luong_kpis",
            "thuong_csat", "thuong_cem", "thuong_trien_khai_dung_hen",
            "thuong_bao_tri_dung_hen", "luong_chat_luong", "cl7n",
            "nha_tuyen", "kh_roi_mang", "ty_le_clps_block", "che_tai",
            "thu_nhap_khac", "thi_dua", "cac_khoan_thu_nhap_khac",
            "thu_chi_khac", "bu_tru_luong_thang_t_1", "khen_thuong",
            "cac_khoan_phu_cap_khac", "luong_san_pham_khac",
            "hoa_hong_ban_hang", "luong_thu_cuoc_khong_chuyen",
            "luong_don_tru", "ghi_chu_bu_tru_khac"
        ]


class SalaryInfSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = SalaryInf
        fields = [
            "luong_inf_id", "email", "month", "luong_cung", "ngay_cong",
            "luong_san_pham", "luong_vhht", "luong_ptht", "luong_nang_suat",
            "thanh_tich_dac_biet", "phu_cap", "container", "swap",
            "tien_gui_xe", "che_tai", "thu_chi_khac", "bu_tru_luong_thang_t_1",
            "khen_thuong", "cac_khoan_ho_tro_khac", "luong_san_pham_khac",
            "hoa_hong_ban_hang", "luong_thu_cuoc_khong_chuyen"
        ]


class InheritedSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class FromDateToDateSerializer(InheritedSerializer):
    tu_ngay = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y"])
    den_ngay = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y"])

    def validate(self, data):
        if data['tu_ngay'] > data['den_ngay']:
            raise ValidationError("tu_ngay không được lớn hơn den_ngay")
        return data


class WorkingScheduleSerializer(InheritedSerializer):
    thang_nam = serializers.CharField()
    thang = serializers.IntegerField()
    vung = serializers.CharField()
    chi_nhanh = serializers.CharField()
    phong_ban = serializers.CharField()
    MNV = serializers.CharField()
    ho_va_ten = serializers.CharField()
    # email = serializers.CharField()
    vi_tri = serializers.CharField()
    account = serializers.CharField(required=False)
    tu_ngay = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y"])
    den_ngay = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y"])
    ghi_chu1 = serializers.CharField(required=False)
    ghi_chu2 = serializers.CharField(required=False)
    schedule_info = serializers.CharField(required=False)

    class Meta:
        model = WorkingSchedule
        fields = ['_all__']

    def __init__(self, *args, **kwargs):
        super(WorkingScheduleSerializer, self).__init__(*args, **kwargs)  # call the super()
        for field in self.fields:  # iterate over the serializer fields
            self.fields[field].error_messages['required'] = 'Thiếu trường %s' % field  # set the custom error message
            self.fields[field].error_messages['blank'] = 'Trường %s không được để trống' % field
            self.fields[field].error_messages['invalid'] = 'Trường %s vui lòng điền đúng định dạng' % field

            if field == 'MNV':
                self.fields[field].error_messages['required'] = '%s không tồn tại' % field

    def validate_thang_nam(self, thang_nam):
        pattern = re.compile("\AT\d{2}.\d{4}$")
        is_valid_thang_nam = pattern.match(thang_nam)
        if not is_valid_thang_nam:
            raise ValidationError("Thang_nam bị sai format")
        thang = int(thang_nam[1:3])
        if thang not in range(1, 13):
            raise ValidationError("Thang_nam bị sai format")
        return thang_nam

    def validate_thang(self, thang):
        if thang not in range(1, 13):
            raise ValidationError("Trường thang phải trong khoảng 01 -> 12")
        return thang

    def validate_MNV(self, MNV):
        pattern1 = re.compile("\A'[0-9]{8}$")
        pattern2 = re.compile("\A[0-9]{8}$")
        is_valid_mnv1 = pattern1.match(MNV)
        is_valid_mnv2 = pattern2.match(MNV)
        if not is_valid_mnv1 and not is_valid_mnv2:
            raise ValidationError("MNV không đúng định dạng")
        return MNV[1:] if is_valid_mnv1 else MNV

    # def validate_email(self, email):
    #     if not email.endswith('@vienthongtin.com') and not (email.startswith('phuongnam.') and email.endswith('@fpt.net')):
    #         raise ValidationError("Email nhân viên không đúng định dạng")
    #     return email

    def validate(self, data):
        if data['tu_ngay'] > data['den_ngay']:
            raise ValidationError("tu_ngay không được lớn hơn den_ngay")
        return data

    # def validate_schedule_info(self, schedule_info):
    #     schedule_info_dict = ast.literal_eval(schedule_info)
    #     schedule_info_keys = schedule_info_dict.keys()
    #     for key_item in schedule_info_keys:
    #         if schedule_info_dict[key_item] != 0 and schedule_info_dict[key_item] != 1:
    #             raise ValueError("Bảng tháng sai giá trị")
    #     return schedule_info

    def create(self, validated_data):
        return WorkingSchedule.objects.create(**validated_data)

    def to_representation(self, data):
        dict_schedule = ast.literal_eval(data.schedule_info)
        return {
            "thang_nam": data.thang_nam,
            "thang": str(data.thang) if data.thang > 9 else "0" + str(data.thang),
            "vung": data.vung,
            "chi_nhanh": data.chi_nhanh,
            "phong_ban": data.phong_ban,
            "MNV": data.MNV,
            "ho_va_ten": data.ho_va_ten,
            # "email": data.email,
            "vi_tri": data.vi_tri,
            "account": data.account,
            # "tu_ngay": data.tu_ngay,
            # "den_ngay": data.den_ngay,
            "ghi_chu1": data.ghi_chu1,
            "ghi_chu2": data.ghi_chu2,
            **dict_schedule,
        }


class ExportWorkingScheduleSerializer(WorkingScheduleSerializer):
    def to_representation(self, data):
        dict_schedule = ast.literal_eval(data.schedule_info)
        return {
            "thang_nam": data.thang_nam,
            "thang": str(data.thang) if data.thang > 9 else "0" + str(data.thang),
            "vung": data.vung,
            "chi_nhanh": data.chi_nhanh,
            "phong_ban": data.phong_ban,
            "MNV": f"{data.MNV}",
            "ho_va_ten": data.ho_va_ten,
            # "email": data.email,
            "vi_tri": data.vi_tri,
            "account": data.account,
            # "tu_ngay": data.tu_ngay,
            # "den_ngay": data.den_ngay,
            "ghi_chu1": data.ghi_chu1,
            "ghi_chu2": data.ghi_chu2,
            **dict_schedule,
        }


class BranchSearchValidate(InheritedSerializer):
    branch = serializers.ChoiceField(choices=['PNC', 'TIN'])


class MonthYearSearchValidate(InheritedSerializer):
    month = serializers.IntegerField()
    year = serializers.IntegerField()
    branch = serializers.ChoiceField(choices=['PNC', 'TIN'])

    def validate_month(self, month):
        if month not in range(1, 13):
            raise ValidationError("Giá trị tháng không đúng")
        return month

    def validate_year(self, year):
        if len(str(year)) != 4:
            raise ValidationError("Giá trị năm không đúng")
        return year


class SalaryValidate(Serializer):
    monthStart = CharField()
    monthEnd = CharField()
    year = CharField()

    # def validate(self, data):

    #     if data['start'] > data['finish']:
    #         raise ValidationError("monthEnd must occur after monthStart")
    #     return data

    def validate_monthStart(self, value):
        if len(value) != 2:
            raise ValidationError("Tháng bắt đầu không đúng")
        if int(value) < 1 or int(value) > 12:
            raise ValidationError("Tháng sai định dạng")

    def validate_monthEnd(self, value):
        if len(value) != 2:
            raise ValidationError("Tháng bắt đầu không đúng")
        if int(value) < 1 or int(value) > 12:
            raise ValidationError("Tháng sai định dạng")

    def validate_year(self, value):
        if len(value) != 4:
            raise ValidationError("Năm không đúng")


class EmpInDepartmentValidate(Serializer):
    childDepart = ListField(required=True)


class SalaryTypeValidate(Serializer):
    salaryType = CharField()


class EmpCodeValidate(Serializer):
    code = CharField()

    def validate_code(self, value):
        if len(value) != 8:
            raise ValidationError("Mã nhân viên phải đủ 8 số!")


class WorkingScheduleToBISerializer(WorkingScheduleSerializer):
    def to_representation(self, data):
        dict_schedule = ast.literal_eval(data.schedule_info)
        month = str(data.thang) if data.thang > 9 else "0" + str(data.thang)
        list_data = []
        for k, v in dict_schedule.items():
            k = k.strip()
            day = k if int(k) > 9 else "0" + k
            list_data.append({"date": day + "/" + month + "/" + data.thang_nam[4:], "number": str(v)})
        return {
            "emp_code": f"{data.MNV}",
            "name": data.ho_va_ten,
            "job_postion": data.vi_tri,
            "month_year": data.thang_nam,
            "month": str(data.thang) if data.thang > 9 else "0" + str(data.thang),
            "description": data.ghi_chu1,
            "description1": data.ghi_chu2,
            "level_3": data.chi_nhanh,
            "level_4": data.phong_ban,
            # "account": data.account,
            # "tu_ngay": data.tu_ngay,
            # "den_ngay": data.den_ngay,

            "list_data": list_data,
        }