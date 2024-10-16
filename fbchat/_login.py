import requests

from ._utils import parse_cookies_to_map, randStr


class Login:
    def __init__(self, session: requests.Session) -> None:
        self.__session__ = session
        self.deviceId = self.adId = self.secureFamilyDeviceId = (
            f"{randStr(8)}-{randStr(4)}-{randStr(4)}-{randStr(4)}-{randStr(12)}"
        )
        self.machineId = randStr(24)

        self.headers = {}
        self.headers["Host"] = "b-graph.facebook.com"
        self.headers["Content-Type"] = "application/x-www-form-urlencoded"
        self.headers["X-Fb-Connection-Type"] = "unknown"
        self.headers["User-Agent"] = (
            "Dalvik/2.1.0 (Linux; U; Android 7.1.2; SM-G988N Build/NRD90M) [FBAN/FB4A;FBAV/340.0.0.27.113;FBPN/com.facebook.katana;FBLC/vi_VN;FBBV/324485361;FBCR/Viettel Mobile;FBMF/samsung;FBBD/samsung;FBDV/SM-G988N;FBSV/7.1.2;FBCA/x86:armeabi-v7a;FBDM/{density=1.0,width=540,height=960};FB_FW/1;FBRV/0;]"
        )
        self.headers["X-Fb-Connection-Quality"] = "EXCELLENT"
        self.headers["Authorization"] = "OAuth null"
        self.headers["X-Fb-Friendly-Name"] = "authenticate"
        self.headers["Accept-Encoding"] = "gzip, deflate"
        self.headers["X-Fb-Server-Cluster"] = "True"

        self.dataForm = {}
        self.dataForm["adid"] = self.adId
        self.dataForm["device_id"] = self.deviceId
        self.dataForm["family_device_id"] = self.deviceId
        self.dataForm["secure_family_device_id"] = self.secureFamilyDeviceId
        self.dataForm["machine_id"] = self.machineId
        self.dataForm["advertiser_id"] = self.adId
        self.dataForm["format"] = "json"
        self.dataForm["generate_analytics_claim"] = "1"
        self.dataForm["community_id"] = ""
        self.dataForm["cpl"] = "true"
        self.dataForm["try_num"] = "1"
        self.dataForm["credentials_type"] = "password"
        self.dataForm["fb4a_shared_phone_cpl_experiment"] = (
            "fb4a_shared_phone_nonce_cpl_at_risk_v3"
        )
        self.dataForm["fb4a_shared_phone_cpl_group"] = "enable_v3_at_risk"
        self.dataForm["enroll_misauth"] = "false"
        self.dataForm["generate_session_cookies"] = "1"
        self.dataForm["error_detail_type"] = "button_with_disabled"
        self.dataForm["source"] = "login"
        self.dataForm["jazoest"] = "22421"
        self.dataForm["meta_inf_fbmeta"] = ""
        self.dataForm["encrypted_msisdn"] = ""
        self.dataForm["currently_logged_in_userid"] = "0"
        self.dataForm["locale"] = "vi_VN"
        self.dataForm["client_country_code"] = "VN"
        self.dataForm["fb_api_req_friendly_name"] = "authenticate"
        self.dataForm["fb_api_caller_class"] = "Fb4aAuthHandler"
        self.dataForm["api_key"] = "882a8490361da98702bf97a021ddc14d"
        self.dataForm["access_token"] = "350685531728|62f8ce9f74b12f84c123cc23437a4a32"

    def by_cookies(self, cookies: str) -> None:
        self.__session__.cookies.update(parse_cookies_to_map(cookies))

    def by_user_pass(self, email: str, password: str) -> None:
        self.dataForm["email"] = email
        self.dataForm["password"] = password

        response = self.__session__.post(
            "https://b-graph.facebook.com/auth/login",
            headers=self.headers,
            data=self.dataForm,
        )

        dataJson = response.json()
        if dataJson.get("error") is not None:
            if dataJson["error"]["error_subcode"] == 1348162:
                self.dataForm["password"] = input("Enter 2FA code: ")
                self.dataForm["try_num"] = "2"
                response = self.__session__.post(
                    "https://b-graph.facebook.com/auth/login",
                    headers=self.headers,
                    data=self.dataForm,
                )
                dataJson = response.json()
                if dataJson.get("error") is not None:
                    raise Exception(dataJson["error"]["message"])
            else:
                raise Exception(dataJson["error"]["message"])
        else:
            cookies = response.json()["session_cookies"]
            cookies_map = {}
            for ck in cookies:
                cookies_map[ck["name"]] = ck["value"]

            self.__session__.cookies.update(cookies_map)

    def by_user_pass_2fa(self, email: str, password: str, twoFactorCode: str) -> None:
        self.__session__.post(
            "https://b-graph.facebook.com/auth/login",
            data={
                "email": email,
                "pass": password,
                "m_ts": "0",
                "li": "0",
                "try_number": "0",
                "unrecognized_tries": "0",
                "login_try_number": "0",
                "prefill_contact_point": email,
                "prefill_source": "browser_onload",
                "prefill_type": "contact_point",
                "first_contact_point": "",
                "first_prefill_source": "",
                "first_prefill_type": "",
                "had_cp_prefilled": "false",
                "had_password_prefilled": "false",
                "is_smart_lock": "false",
                "bi_xrwh": "0",
                "bi_xrwh_rc": "",
            },
        )

    def is_logged_in(self) -> bool:
        response = self.__session__.get(
            "https://www.facebook.com/login/", allow_redirects=True
        )
        return response.url == "https://www.facebook.com/home.php"
