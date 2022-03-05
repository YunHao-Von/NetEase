from abc import abstractclassmethod, ABCMeta
import re
import requests
import json
import sys

class DataSpider():
    def __init__(self,init_ID = 5038805378 ):
        self.init_id = init_ID
        self.login_url='http://localhost:3000/login/cellphone?phone=13086647572&password=wnj123456'
        self.connect =  requests.Session() 
    def get_playlist_id_from_usersid(self,user_id):
        user_playlist_url='http://localhost:3000/user/playlist?uid='+str(user_id)  # 获取当前用户的歌单
        try:
            play_list_web = self.connect.get(url=user_playlist_url)
            play_list_web = json.loads(play_list_web.text)
            assert play_list_web['code'] == 200
            playlist_id = list()  # 本列表存储用户的所有歌单的ID
            for playlist_ in play_list_web['playlist'] :
                playlist_id.append(playlist_['id'])
            return playlist_id
        except:
            print("获取user_id="+str(user_id)+"的歌单id列表失败")
            return list()
    def get_songsids_from_playlistid(self,playlist_one_id):
        """通过一个歌单的ID来获得歌单中的所有歌曲的ID
        :param playlist_one_id:一个歌单的ID
        :return songs_id_list:包含了本歌单中歌曲的id"""
        playlist_details_url = "http://localhost:3000/playlist/detail?id=" + str(playlist_one_id)
        try:
            playlist_details_web = self.connect.get(url = playlist_details_url)
            playlist_details_web = json.loads(playlist_details_web.text)
            assert playlist_details_web['code'] == 200
            songsid_list = list()
            for song_info in playlist_details_web['playlist']['tracks']:
                songsid_list.append(song_info['id'])
            return songsid_list
        except:
            print("获取playlist_id="+str(playlist_one_id)+"的歌单中的歌曲id列表失败")
            return list()
    
    def get_userids_from_songid(self,song_id):
        comments_url = "http://localhost:3000/comment/music?id="+str(song_id)+"&limit=100"
        try:
            comments_web = self.connect.get(url = comments_url)
            comments_web = json.loads(comments_web.text)
            assert comments_web['code'] == 200
            comments = comments_web['comments']
            other_user_id = list()
            for user in comments:
                other_user_id.append(user['user']['userId'])
            return other_user_id
        except:
            print("获取song_id="+str(song_id)+"的歌曲中的评论用户id列表失败")
            return list()
    
    @abstractclassmethod
    def userid_spider_fit(self):
        pass

    @abstractclassmethod
    def usersongs_spider_fit(self):
        pass


class User_spider(DataSpider):
    def __init__(self, init_ID=5038805378):
        """初始
        化函数，确保已经成功登陆"""
        super().__init__(init_ID)
        try:
            uid=self.init_id  # 初始化一个用户id(这里是作者本人的)
            login_url='http://localhost:3000/login/cellphone?phone=13086647572&password=wnj123456'  # 模拟登陆IP
            self.connect= requests.Session()  # 准备Session
            login_data=self.connect.get(url=login_url)  # 登陆后拿到用户数据
            login_data = json.loads(login_data.text)
            assert login_data['code'] == 200
        except:
            print("用户登陆失败")
            sys.exit()
    
    def userid_spider_fit(self,user_id):
        playlist_id_list = self.get_playlist_id_from_usersid(user_id)
        songs_list = list()
        usersid_list = list()
        for playlist_id in playlist_id_list:
            temp_songs_list = self.get_songsids_from_playlistid(playlist_id)
            songs_list.extend(temp_songs_list)
        for song_id in songs_list:
            temp_usersid_list = self.get_userids_from_songid(song_id)
            usersid_list.extend(temp_usersid_list)
        return usersid_list
    
    def usersongs_spider_fit(self,user_id):
        playlist_id_list = self.get_playlist_id_from_usersid(user_id)
        songs_list = list()
        for playlist_id in playlist_id_list:
            temp_songs_list = self.get_songsids_from_playlistid(playlist_id)
            songs_list.extend(temp_songs_list)
        songs_list = list(set(songs_list))
        return songs_list