from time import sleep
import requests
import logging
import ddddocr
import re

ocr = ddddocr.DdddOcr()

LOG_FORMAT = '%(asctime)s %(levelname)s\t %(thread)d %(lineno)d %(funcName)s\t\t%(message)s'
# logging.basicConfig(handlers=[logging.FileHandler('log.log', 'a', 'utf-8')],level=logging.INFO, format=LOG_FORMAT)
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

headers = {
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

class bugku():
    def __init__(self) -> None:
        self.session = requests.session()
        self.session.headers.update(headers)
        self.num = 10
        self.is_login = False

    def get_captcha(self):
        if self.num <=0:
            logging.warning('验证码重试次数太多')
            exit(0)
        url = 'https://ctf.bugku.com/captcha.html0.9004209313422487'
        res = self.session.get(url)
        if res.status_code==200:
            code = ocr.classification(res.content)
            c = ''.join(re.findall('\w',code))
            if len(c)==4:
                logging.info('验证码成功：'+c)
                # self.session.headers.update(res.headers)
                return c
            else:
                sleep(3)
                self.num -= 1
                self.get_captcha()
        else:
            sleep(3)
            self.num -= 1
            self.get_captcha()

    def login(self,username,password):
        if self.num <=0:
            logging.warning('登录重试次数太多')
            exit(0)
        login_url = 'https://ctf.bugku.com/login/check.html'
        code = self.get_captcha()
        data = {'username':username,'password':password,'vcode':code,'autologin':'1'}
        res = self.session.post(url=login_url,data=data,headers=headers)

        if '登录成功'in res.text:
            logging.info(f'{username} 登录成功:{res.text}')
            # self.session.headers.update(res.headers)
            self.is_login = True
        else:
            logging.error('登录失败：'+res.text)
            sleep(3)
            self.num -= 1
            self.login(username,password)

    def checkin(self,username,password):
        if self.is_login:
            response = self.session.get('https://ctf.bugku.com/user/checkin')
            print(response.text)
            #{"code":1,"msg":"签到成功","data":{"user_id":59654,"count":1,"coin":1},"url":"","wait":3}
            if '成功'in response.text:
                logging.info('签到成功：'+response.text)
            else:
                logging.error('失败')
        else:
            self.login(username,password)
            response = self.session.get('https://ctf.bugku.com/user/checkin')
            print(response.text)
            if '成功'in response.text:
                logging.info('签到成功：'+response.text)
            else:
                logging.error('失败')

if __name__ == '__main__':
    _bk = bugku()
    _bk.checkin('username','password')
