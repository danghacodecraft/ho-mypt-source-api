from app.http.models.user_infos import UserInfos
from app.http.serializers.user_infos_serializer import UserInfosSerializer

class UserInfosHandler:
    def getAllUsers(self):
        userInfoQs = UserInfos.objects.all()
        userInfo_ser = UserInfosSerializer(userInfoQs, many=True)
        userInfosArr = userInfo_ser.data
        return userInfosArr

    def getUserByEmail(self, email):
        email = email.lower()
        print("chuan bi tim user theo email : " + email)
        usQs = UserInfos.objects.filter(email=email)[0:1]
        userInfo_ser = UserInfosSerializer(usQs, many=True)
        usersArr = userInfo_ser.data
        # print(usersArr)
        if len(usersArr) > 0:
            userInfoItem = usersArr[0]
            print(userInfoItem)
            return userInfoItem
        else:
            return None

    def getUserByUserId(self, userId):
        print("chuan bi tim user theo User ID : " + str(userId))
        usQs = UserInfos.objects.filter(user_id=userId)[0:1]
        userInfo_ser = UserInfosSerializer(usQs, many=True)
        usersArr = userInfo_ser.data
        # print(usersArr)
        if len(usersArr) > 0:
            userInfoItem = usersArr[0]
            print(userInfoItem)
            return userInfoItem
        else:
            return None

    def createUser(self, email, userInfo):
        newUser = UserInfos()
        newUser.email = email.lower()
        newUser.full_name = userInfo.get("fullName")
        newUser.app_language = userInfo.get("lang", "vi")

        if userInfo.get("hoDateLogin", None) is not None:
            newUser.ho_date_login = userInfo.get("hoDateLogin")

        newUser.unread_notify = 1
        newUser.is_deleted = 0
        resInsert = newUser.save()
        print(resInsert)
        newUserId = newUser.user_id
        print("new user id : " + str(newUserId))

        if int(newUserId) > 0:
            return {"resCreate": "SUCCESS", "userId": int(newUserId)}
        else:
            return {"resCreate": "FAILED"}

    def updateUserInfoByUserId(self, userId, userInfo = {}):
        # cach 1 :
        updatedFields = []
        usQs = UserInfos.objects.get(user_id=userId)
        if userInfo.get("fullName", None) is not None:
            usQs.full_name = userInfo.get("fullName")
            updatedFields.append("full_name")

        if userInfo.get("hoDateLogin", None) is not None:
            usQs.ho_date_login = userInfo.get("hoDateLogin")
            updatedFields.append("ho_date_login")

        if userInfo.get("hoDateLatestRefreshToken", None) is not None:
            usQs.ho_date_latest_refresh_token = userInfo.get("hoDateLatestRefreshToken")
            updatedFields.append("ho_date_latest_refresh_token")

        if userInfo.get("lang", None) is not None:
            usQs.app_language = userInfo.get("lang")
            updatedFields.append("app_language")

        resUpdate = usQs.save(update_fields=updatedFields)

        return resUpdate