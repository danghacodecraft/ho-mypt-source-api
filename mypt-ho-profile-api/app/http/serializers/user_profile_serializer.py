from app.http.models.user_profile import UserProfile
from rest_framework.serializers import ModelSerializer

class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user_id', 'email', 'full_name', 'avatar_img']

    def get_avatar_from_email(email, time_now):
        link_avatar = ""
        try:
            queryset = UserProfile.objects.filter(email=email).values_list('avatar_img', flat=True)
            if len(queryset) > 0 :
                link_avatar = queryset[0]

        except Exception as ex:
            print("get_avartar_from_email >> {} >> Error/loi: {}".format(time_now, ex))
        return link_avatar
