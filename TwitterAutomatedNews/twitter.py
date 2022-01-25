class Twitter:
    def __init__(self):
        auth = tweepy.OAuthHandler("HgrXzpH5fqfvosL6vSm9aYZqX", "yKXBs1vBUJSQWOVNMSktGkOKBFiKUPQidCVLYLemOXa3fG3Ws7")
        auth.set_access_token("3295534592-IiBIJWqSQqKMZKVCEL04RwRgWaXAnB6TMb8VHyi",
                              "M1Gn67DBn5pcK5rGcExFi1PAT8mQpTjXwj15DefXebABW")
        self.api = tweepy.API(auth)

    def check_credentials(self):
        try:
            self.api.verify_credentials()
            print('Authentication OK')
        except KeyError:
            print('Error during authentication')
            sys.exit()

    def post(self, summery, url):
        return self.api.update_status(f"{summery} \n {url}")

    def country_info(self, codes):
        country = []
        countries = self.api.available_trends()
        for i in range(len(codes)):
            for j in range(len(countries)):
                if codes[i] == countries[j].get("countryCode"):
                    country.append({"countryAbbreviated": codes[i], "countryId": countries[j].get("woeid")})
                    break
        return country