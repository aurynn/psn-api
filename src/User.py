import requests
from urllib.parse import urljoin

class User:

    oauth = None
    refresh_token = None

    USERS_URL = 'https://us-prof.np.community.playstation.net/userProfile/v1/users/'

    def __init__(self, tokens):
        self.oauth = tokens['oauth']
        self.refresh_token = tokens['refresh']

    def me(self):
        header = {
            'Authorization': 'Bearer '+self.oauth
        }
        endpoint = '?fields=npId,onlineId,avatarUrls,plus,aboutMe,languagesUsed,trophySummary(@default,progress,earnedTrophies),isOfficiallyVerified,personalDetail(@default,profilePictureUrls),personalDetailSharing,personalDetailSharingRequestMessageFlag,primaryOnlineStatus,presences(@titleInfo,hasBroadcastData),friendRelation,requestMessageFlag,blocking,mutualFriendsCount,following,followerCount,friendsCount,followingUsersCount&avatarSizes=m,xl&profilePictureSizes=m,xl&languagesUsedLanguageSet=set3&psVitaTitleIcon=circled&titleIconSize=s'
        
        url = urljoin(self.USERS_URL, "me/profile2")
        url = urljoin(url, endpoint)
        
        response = requests.get(url=url,headers=header)

        return response.json()
