import tweepy


class Twitter:
    def __init__(self):
        auth = tweepy.OAuthHandler("HgrXzpH5fqfvosL6vSm9aYZqX", "yKXBs1vBUJSQWOVNMSktGkOKBFiKUPQidCVLYLemOXa3fG3Ws7")
        auth.set_access_token("3295534592-IiBIJWqSQqKMZKVCEL04RwRgWaXAnB6TMb8VHyi",
                              "M1Gn67DBn5pcK5rGcExFi1PAT8mQpTjXwj15DefXebABW")
        self.api = tweepy.API(auth)

    def check_credentials(self):
        """Checks the user credentials

            check the user credentials, prints out the result,
            if the function finds an error it quits the program
        """
        try:
            self.api.verify_credentials()
            print('Authentication OK')
        except KeyError:
            print('Error during authentication')
            sys.exit()

    def post(self, summery, url):
        """posts a status with the inputted strings

        the summery gives a brief overview of the article, the url link to the article

        Args:
            summery (str): description of article
            url (str): external link to article

        Returns: None
        """

        return self.api.update_status(f"{summery} \n {url}")

    def country_info(self, codes):
        """ gets the woeid from twitter

            the summery gives a brief overview of the article, the url link to the article

            Args:
                codes (list): all_woeid to get trends from

            Returns:
                a list of WOEID data points
        """
        country = []
        all_woeid = self.api.available_trends()
        for code in codes:
            for location in all_woeid:
                if code == location.get("countryCode"):
                    country.append({"countryAbbreviated": code, "countryId": location.get("woeid")})
                    break
        return country
