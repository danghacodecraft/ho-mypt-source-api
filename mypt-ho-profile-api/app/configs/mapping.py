from django.conf import settings
from ..core.helpers.datetime_to_date import datetime_to_date
from ..http.serializers.hr_serializer import EmployeeSerializer

EMPLOYEE_HRIS_PATTERN = {
    "code": "emp_code",
    "fullName": "name",
    "birthDate": "birthday",
    "emailAddress": "email",
    "phoneNumber": "mobilePhone",
    "ipPhone": "idPhone",
    "plurality": "plurality",
    "placeOfBirth": "placeOfBirth",
    "gender": "sex",
    "startWorkingTime": "dateJoinCompany",
    "employeeLevel": "level",
    "address": "placeOfPermanent",
    "identityCardNumber": "cmnd",
    "identityCardTime": "date",
    "identityCardPlace": "issuedAt",
    "pitId": "mstcn",
    "pitDateIssued": "taxIdentificationDate",
    "pitPlaceIssued": "taxIdentificationPlace",
    "qualification": "degree",
    "placeWork": "workplace",
    "nationality": "nationality",
    "maritalStatus": "maritalStatus",
    "salaryInsurance": "socialInsuranceSalaryPay",
    "bankAccountNo": "accountNumber",
    "bankName": "bankName",
    "healthInsurance": "healthInsurance",
    "endWorkingTime": "dateQuitJob",
    "foxpayAccount": "foxpay",
    "comment": "comment",
    "organizationCode": "childDepart",
    "officerTitle": "officerTitle",
    "jobTitle": "jobTitle",
    "isActive": "statusWorking",
    "contractNumber": "contractCode",
    "contractType": "contractType",
    "contractTypeCode": "contractTypeCode",
    "contractStartTime": "contractBegin",
    "contractEndime": "contractEnd",
    "jobCode": "jobCode",
    "officerCode": "officerCode"
}

EMPLOYEE_HRIS_VALUE_PATTERN = {
    "email": lambda x : x.replace("stag_", "") if settings.APP_ENVIRONMENT != "production" else x,
    "birthday": datetime_to_date,
    "dateJoinCompany": datetime_to_date,
    "date": datetime_to_date,
    "taxIdentificationDate": datetime_to_date,
    "contractBegin": datetime_to_date,
    "contractEnd": datetime_to_date,
    "dateQuitJob": datetime_to_date,
    "statusWorking": lambda x : 1 if x else 0,
    "maritalStatus": EmployeeSerializer.marital_status_mapping,
    "sex": EmployeeSerializer.gender_mapping
}

EMPLOYEE_HRIS_QUALIFICATION_PATTERN = {
    "code": "emp_code",
    "qualificationId": "inside_id",
    "emailAddress": "email",
    "qualificationSchoolName": "organization_name",
    "qualificationFieldOfStudy": "field_of_study",
    "qualificationTypeOfTraining": "type_of_training",
    "qualificationGraduatedYear": "graduated_year",
    "qualificationRating": "ranked_academic",
    "qualificationNote": "note"
}

EMPLOYEE_HRIS_QUALIFICATION_VALUE_PATTERN = {
    "email": lambda x : x.replace("stag_", "") if settings.APP_ENVIRONMENT != "production" else x
}

EMPLOYEE_HRIS_CERTIFICATE_PATTERN = {
    "code": "emp_code",
    "emailAddress": "email",
    "certificateId": "inside_id",
    "certificateYear": "issued_year",
    "certificateSkillName": "skill_name",
    "certificateTrainingPlace": "training_organization",
    "certificateNote": "note",
    "certificateRating": "rate"
}

EMPLOYEE_HRIS_CERTIFICATE_VALUE_PATTERN = {
    "email": lambda x : x.replace("stag_", "") if settings.APP_ENVIRONMENT != "production" else x
}