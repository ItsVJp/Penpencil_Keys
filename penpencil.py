import asyncio
import base64
import urllib.parse
import httpx
import re


# Developer @Its_Vj_p
async def get_pssh_kid(mpd_url: str, headers: dict = {}, cookies: dict = {}):
    """
    Get pssh, kid from mpd url
    headers: Headers if needed
    """
    pssh = ""
    kid = ""
    for i in range(3):
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(mpd_url, headers=headers, cookies=cookies)
                mpd_res = res.text
        except Exception as e:
            print("Error fetching MPD:", e)
            continue
        try:
            matches = re.finditer("<cenc:pssh>(.*)</cenc:pssh>", mpd_res)
            pssh = next(matches).group(1)
            kid = re.findall(r'default_KID="([\S]+)"', mpd_res)[0].replace("-", "")
        except Exception as e:
            print("Error extracting PSSH or KID:", e)
            continue
        else:
            break
    return pssh, kid
    
class Penpencil:
    otp_url = "https://api.penpencil.xyz/v1/videos/get-otp?key="
    penpencil_bearer = 'Your_token''

    headers = {
        "Host": "api.penpencil.xyz",
        "content-type": "application/json",
        "authorization": f"Bearer {penpencil_bearer}",
        "client-version": "11",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; PACM00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.98 Mobile Safari/537.36",
        "client-type": "MOBILE",
        "accept-encoding": "gzip",
    }

    @classmethod
    def get_otp_key(cls, kid: str):
        f = (
            base64.b64encode(
                bytes(
                    [
                        (
                            ord(kid[i])
                            ^ ord(
                                cls.penpencil_bearer[
                                    i % (len(cls.penpencil_bearer) - 1)
                                ]
                            )
                        )
                        for i in range(0, len(kid))
                    ]
                )
            )
        ).decode("utf-8")
        return f

    @classmethod
    def get_key(cls, otp: str):
        a = base64.b64decode(otp)
        b = len(a)
        c = [int(a[i]) for i in range(0, b)]
        d = "".join(
            [
                chr(
                    (c[j])
                    ^ ord(
                        cls.penpencil_bearer[
                            j % (len(cls.penpencil_bearer) - 1)
                        ]
                    )
                )
                for j in range(0, b)
            ]
        )
        return d

    @classmethod
    async def get_keys(cls, kid: str):
        otp_key = cls.get_otp_key(kid)
        keys = []
        for i in range(3):
            try:
                async with httpx.AsyncClient(headers=cls.headers) as client:
                    resp = await client.get(f"{cls.otp_url}{otp_key}")
                    otp_dict = resp.json()
            except Exception as e:
                print("Error fetching OTP:", e)
                continue
            try:
                otp = otp_dict["data"]["otp"]
                key = cls.get_key(otp)
                keys = [f"{kid}:{key}"]
            except Exception as e:
                print("Error extracting key:", e)
                continue
            else:
                break
        return keys

    @classmethod
    async def get_mpd_title(cls, url: str):
       
        mpd_url = url        
        return mpd_url

    @classmethod
    async def get_mpd_keys_title(cls, url: str, keys: list = []):
        mpd_url = await cls.get_mpd_title(url)
        if keys:
            return mpd_url
        if mpd_url:
            pssh, kid = await get_pssh_kid(mpd_url)
            print("PSSH:", pssh)
            print("KID:", kid)
            
            keys = await cls.get_keys(kid)
            print("Keys:", keys)
        return mpd_url, keys

async def main():
    url = input("Developer @Its_Vj_p \nEnter the MPD URL: ")
    mpd_url, keys = await Penpencil.get_mpd_keys_title(url)
    print("MPD URL:", mpd_url)
    print("Keys:", keys)
    

asyncio.run(main())
