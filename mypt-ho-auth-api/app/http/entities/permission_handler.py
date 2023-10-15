from app.http.serializers.ho_permission_serializer import *
from app.http.serializers.ho_permission_group_serializer import *
from app.http.serializers.ho_user_permission_serializer import *

from app.http.models.ho_permission import *
from app.http.models.ho_permission_group import *
from app.http.models.ho_user_permission import *

from django.db import connection

class PermissionHandler:
    def __init__(self):
        pass

    # API nay se lay ra cac permission cua userId nay, va tap hop cac child_depart de gui qua mypt-ho-profile de lay parent_depart & branch
    def getAllPermissionsByUser(self, userId):
        query = "SELECT user_per.permission_code, per_group.permission_group_code, user_per.child_depart, has_depart_right FROM " + HoUserPermission._meta.db_table + " AS user_per INNER JOIN " + HoPermission._meta.db_table + " AS per ON user_per.permission_id = per.permission_id INNER JOIN " + HoPermissionGroup._meta.db_table + " AS per_group ON per.permission_group_id = per_group.permission_group_id WHERE user_per.user_id = " + str(userId) + " AND per.is_deleted = 0 AND per_group.is_deleted = 0"
        cursor = connection.cursor()
        cursor.execute(query)
        userPerRows = cursor.fetchall()
        persData = {}
        collectedChildDeparts = []
        print(userPerRows)
        for userPerRow in userPerRows:
            perCode = userPerRow[0]
            hasDepartRight = int(userPerRow[3])
            persData[perCode] = {
                "group_code": userPerRow[1],
                "has_depart_right": hasDepartRight,
                "child_depart_rights": {},
                "branch_rights": {
                    "TIN": [],
                    "PNC": []
                },
                "specificChildDeparts": []
            }

            # phan tach child_depart
            if hasDepartRight == 1:
                childDepartStr = userPerRow[2].strip()
                if childDepartStr != "":
                    childDepartArrs = childDepartStr.split(",")
                    for childDepartItem in childDepartArrs:
                        # Neu child_depart la ALL / ALLTIN / ALLPNC
                        if childDepartItem == "ALL":
                            persData[perCode]["branch_rights"] = {
                                "TIN": ["ALL"],
                                "PNC": ["ALL"]
                            }
                        elif childDepartItem == "ALLTIN":
                            persData[perCode]["branch_rights"]["TIN"] = ["ALL"]
                        elif childDepartItem == "ALLPNC":
                            persData[perCode]["branch_rights"]["PNC"] = ["ALL"]
                        else:
                            persData[perCode]["specificChildDeparts"].append(childDepartItem)
                            if childDepartItem not in collectedChildDeparts:
                                collectedChildDeparts.append(childDepartItem)
            else:
                persData[perCode]["child_depart_rights"] = None
                persData[perCode]["branch_rights"] = None


        return {
            "persData": persData,
            "collectedSpecificChildDeparts": collectedChildDeparts
        }
