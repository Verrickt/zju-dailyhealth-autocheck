import requests
from util import *
from logger import *
from tgpush import *
class ZJULogin(object):
    """
    Attributes:
        sess: (requests.Session) 统一的session管理
    """
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
    }
    BASE_URL = "https://healthreport.zju.edu.cn/ncov/wap/default/index"
    LOGIN_URL = "https://zjuam.zju.edu.cn/cas/login?service=http%3A%2F%2Fservice.zju.edu.cn%2F"

    def __init__(self, config, delay_run=False):
        self.config = config
        self.delay_run = delay_run
        self.sess = requests.Session()

    def login(self):
        """Login to ZJU platform"""
        res = self.sess.get(self.LOGIN_URL)
        execution = re.search(
            'name="execution" value="(.*?)"', res.text).group(1)
        res = self.sess.get(
            url='https://zjuam.zju.edu.cn/cas/v2/getPubKey').json()
        n, e = res['modulus'], res['exponent']

        username = self.config['username']
        password = self.config['password']
        encrypt_password = self._rsa_encrypt(password, e, n)

        data = {
            'username': username,
            'password': encrypt_password,
            'execution': execution,
            '_eventId': 'submit',
            "authcode": ""
        }
        res = self.sess.post(url=self.LOGIN_URL, data=data)
        # check if login successfully
        if '用户名或密码错误' in res.content.decode():
            raise LoginError('登录失败，请核实账号密码重新登录')
        print("统一认证平台登录成功~")
        return self.sess

    def _rsa_encrypt(self, password_str, e_str, M_str):
        password_bytes = bytes(password_str, 'ascii')
        password_int = int.from_bytes(password_bytes, 'big')
        e_int = int(e_str, 16)
        M_int = int(M_str, 16)
        result_int = pow(password_int, e_int, M_int)
        return hex(result_int)[2:].rjust(128, '0')



class HealthCheckInHelper(ZJULogin):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
    }

    REDIRECT_URL = "https://zjuam.zju.edu.cn/cas/login?service=https%3A%2F%2Fhealthreport.zju.edu.cn%2Fa_zju%2Fapi%2Fsso%2Findex%3Fredirect%3Dhttps%253A%252F%252Fhealthreport.zju.edu.cn%252Fncov%252Fwap%252Fdefault%252Findex%26from%3Dwap"

    def __init__(self,config,delay_run=False):
        super().__init__(config, delay_run=delay_run)

    def get_geo_info(self, location: dict):
        params = (
            ('key', '729923f88542d91590470f613adb27b5'),
            ('s', 'rsv3'),
            ('language', 'zh_cn'),
            ('location', '{lng},{lat}'.format(lng=location.get("lng"), lat=location.get("lat"))),
            ('extensions', 'base'),
            ('callback', 'jsonp_607701_'),
            ('platform', 'JS'),
            ('logversion', '2.0'),
            ('appname', 'https://healthreport.zju.edu.cn/ncov/wap/default/index'),
            ('csid', '63157A4E-D820-44E1-B032-A77418183A4C'),
            ('sdkversion', '1.4.16'),
        )

        response = self.sess.get('https://restapi.amap.com/v3/geocode/regeo', headers=self.headers, params=params, )
        return take_out_json(response.text)

    def fill_geo_info(self, geo_info: dict):
        formatted_address = geo_info.get("regeocode").get("formatted_address")
        address_component = geo_info.get("regeocode").get("addressComponent")
        if not formatted_address or not address_component: return

        # 获得id和uid参数
        res = self.sess.get(self.BASE_URL, headers=self.headers)
        #html = res.content.decode()
        #new_info_tmp = json.loads(re.findall(r'def = ({[^\n]+})', html)[0])
        #new_id = new_info_tmp['id']
        #new_uid = new_info_tmp['uid']
        # 拼凑geo信息
        lng, lat = address_component.get("streetNumber").get("location").split(",")
        geo_api_info_dict = {"type": "complete", "info": "SUCCESS", "status": 1, "cEa": "jsonp_859544_",
                             "position": {"Q": lat, "R": lng, "lng": lng, "lat": lat},
                             "message": "Get ipLocation success.Get address success.", "location_type": "ip",
                             "accuracy": "null", "isConverted": "true", "addressComponent": address_component,
                             "formattedAddress": formatted_address, "roads": [], "crosses": [], "pois": []}

        data = {
            'sfymqjczrj': '0',
            'zjdfgj': '',
            'sfyrjjh': '0',
            'cfgj': '',
            'tjgj': '',
            'nrjrq': '0',
            'rjka': '',
            'jnmddsheng': '',
            'jnmddshi': '',
            'jnmddqu': '',
            'jnmddxiangxi': '',
            'rjjtfs': '',
            'rjjtfs1': '',
            'rjjtgjbc': '',
            'jnjtfs': '',
            'jnjtfs1': '',
            'jnjtgjbc': '',
            # 是否确认信息属实
            'sfqrxxss': '1',
            'sfqtyyqjwdg': '0',
            'sffrqjwdg': '0',
            'sfhsjc': '',
            'zgfx14rfh': '0',
            'zgfx14rfhdd': '',
            'sfyxjzxgym': '1',
            # 是否不宜接种人群
            'sfbyjzrq': '5',
            'jzxgymqk': '2',
            'tw': '0',
            'sfcxtz': '0',
            'sfjcbh': '0',
            'sfcxzysx': '0',
            'qksm': '',
            'sfyyjc': '0',
            'jcjgqr': '0',
            'remark': '',
            # 浙江省杭州市西湖区三墩镇西湖国家广告产业园西湖广告大厦
            # '\u6D59\u6C5F\u7701\u676D\u5DDE\u5E02\u897F\u6E56\u533A\u4E09\u58A9\u9547\u897F\u6E56\u56FD\u5BB6\u5E7F\u544A\u4EA7\u4E1A\u56ED\u897F\u6E56\u5E7F\u544A\u5927\u53A6',
            'address': formatted_address,
            # {"type":"complete","info":"SUCCESS","status":1,"cEa":"jsonp_859544_","position":{"Q":30.30678,"R":120.06375000000003,"lng":120.06375,"lat":30.30678},"message":"Get ipLocation success.Get address success.","location_type":"ip","accuracy":null,"isConverted":true,"addressComponent":{"citycode":"0571","adcode":"330106","businessAreas":[],"neighborhoodType":"","neighborhood":"","building":"","buildingType":"","street":"西园三路","streetNumber":"1号","country":"中国","province":"浙江省","city":"杭州市","district":"西湖区","township":"三墩镇"},"formattedAddress":"浙江省杭州市西湖区三墩镇西湖国家广告产业园西湖广告大厦","roads":[],"crosses":[],"pois":[]}
            # '{"type":"complete","info":"SUCCESS","status":1,"cEa":"jsonp_859544_","position":{"Q":30.30678,"R":120.06375000000003,"lng":120.06375,"lat":30.30678},"message":"Get ipLocation success.Get address success.","location_type":"ip","accuracy":null,"isConverted":true,"addressComponent":{"citycode":"0571","adcode":"330106","businessAreas":[],"neighborhoodType":"","neighborhood":"","building":"","buildingType":"","street":"\u897F\u56ED\u4E09\u8DEF","streetNumber":"1\u53F7","country":"\u4E2D\u56FD","province":"\u6D59\u6C5F\u7701","city":"\u676D\u5DDE\u5E02","district":"\u897F\u6E56\u533A","township":"\u4E09\u58A9\u9547"},"formattedAddress":"\u6D59\u6C5F\u7701\u676D\u5DDE\u5E02\u897F\u6E56\u533A\u4E09\u58A9\u9547\u897F\u6E56\u56FD\u5BB6\u5E7F\u544A\u4EA7\u4E1A\u56ED\u897F\u6E56\u5E7F\u544A\u5927\u53A6","roads":[],"crosses":[],"pois":[]}',
            'geo_api_info': geo_api_info_dict,
            # 浙江省 杭州市 西湖区
            # '\u6D59\u6C5F\u7701 \u676D\u5DDE\u5E02 \u897F\u6E56\u533A'
            'area': "{} {} {}".format(address_component.get("province"), address_component.get("city"),
                                      address_component.get("district")),
            # 浙江省
            # '\u6D59\u6C5F\u7701'
            'province': address_component.get("province"),
            # 杭州市
            # '\u676D\u5DDE\u5E02'
            'city': address_component.get("city"),
            # 是否在校
            'sfzx': '1',
            'sfjcwhry': '0',
            'sfjchbry': '0',
            'sfcyglq': '0',
            'gllx': '',
            'glksrq': '',
            'jcbhlx': '',
            'jcbhrq': '',
            'bztcyy': '',
            'sftjhb': '0',
            'sftjwh': '0',
            'ismoved': '0',
            # 👇-----12.1日修改-----👇
            'sfjcqz': '0',
            'jcqzrq': '',
            # 👆-----12.1日修改-----👆
            'jrsfqzys': '',
            'jrsfqzfy': '',
            'sfyqjzgc': '',
            # 是否申领杭州健康码
            'sfsqhzjkk': '1',
            # 杭州健康吗颜色，1:绿色 2:红色 3:黄色
            'sqhzjkkys': '1',
            'gwszgzcs': '',
            'szgj': '',
            'fxyy': '',
            'jcjg': '',
            # uid每个用户不一致
            # 'uid': new_uid,
            # id每个用户不一致
            # 'id': new_id,
            # 下列原来参数都是12.1新版没有的
            # 日期
            'date': get_date(),
            'created': round(time.time()),
            'szsqsfybl': '0',
            'sfygtjzzfj': '0',
            'gtjzzfjsj': '',
            'zgfx14rfhsj': '',
            'jcqzrq': '',
            'gwszdd': '',
            'szgjcs': '',
            # 'jrdqtlqk[]': 0,
            # 'jrdqjcqk[]': 0,
        }
        response = self.sess.post('https://healthreport.zju.edu.cn/ncov/wap/default/save', data=data,
                                  headers=self.headers)
        return response.json()

    def run(self):
        print("正在为{}健康打卡".format(self.config["username"]))
        if self.delay_run:
            # 确保定时脚本执行时间不太一致
            time.sleep(random.randint(0, 10))
        # 拿到Cookies和headers
        try:
            self.login()
            # 拿取eai-sess的cookies信息
            self.sess.get(self.REDIRECT_URL)
            # 由于IP定位放到服务器上运行后会是服务器的IP定位
            lng= self.config["point"]['lng']
            lat= self.config["point"]['lat']
            location = {'info': 'LOCATE_SUCCESS', 'status': 1, 'lng': lng, 'lat': lat}
            geo_info = self.get_geo_info(location)
            print(geo_info)
            res = self.fill_geo_info(geo_info)
            print(res)
            post_tg(self.config['push']['telegram'],'浙江大学每日健康打卡 V1.3 '+ " \n\n 签到结果: " + res.get("m")) 
        except requests.exceptions.ConnectionError as err:
            # reraise as KubeException, but log stacktrace.
            #调用tg推送模块
            post_tg(self.config['push']['telegram'],'统一认证平台登录失败,请检查服务器网络状态')
