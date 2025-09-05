import os
import logging
from dotenv import load_dotenv

import requests
import json


class APIData:
    def __init__(self) -> None:
        """
        Creates an instance of APIData to handle authentication and data fetching 
        from the IGDB API.

        Attributes:
            TOKEN_URL (str): The URL for obtaining OAuth2 tokens from Twitch.
            api_url (str): The URL for the IGDB API last fetched from.
            data (dict): A dictionary to store fetched data from the IGDB API.
        """
        self.TOKEN_URL = "https://id.twitch.tv/oauth2/token"
        self.api_url = ""
        self.data = {}
    def __repr__(self):
        return f"APIData(data={self.data})"
    def __str__(self):
        return json.dumps(self.data, indent=4)
    def authenticate(self, client_id: str, client_secret: str) -> dict | None:
        """
        Tries to authenticate with the IGDB API using the provided client ID 
        and client secret.

        Args:
            client_id (str): The client ID from Twitch Developer for the IGDB API.
            client_secret (str): The client secret from Twitch Developer for the 
                IGDB API.

        Returns:
            Authentication data if successful, otherwise returns None.
        """
        try:
            # Make the authentication request
            response = requests.post(
                url=self.TOKEN_URL,
                params={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "grant_type": "client_credentials"
                }
            )

            auth_data = response.json()
            return auth_data
        except Exception as e:
            logging.error(f"An error occurd when trying to authenticate: {e}")
            return None
    def api_fetch(self, url: str, client_id: str, access_token: str, 
                  data_fields: list[str] | None = None, 
                  data_limit: int | None = None) -> None:
        """
        Fetches data from the IGDB API using the provided URL,
        client ID, access token, and optional data fields and limit.  
        Stores the fetched data in the instance variable `data`.

        Args:
            url (str): The IGDB API endpoint URL. (Should be in the format
                "https://api.igdb.com/v4/{endpoint}")
            client_id (str): The client ID from Twitch Developer for the IGDB API.
            access_token (str): The access token obtained from authentication.
            data_fields (list[str] | None): Optional list of fields to fetch from the
                API.
            data_limit (int | None): Optional limit on the number of records to fetch.
        """
        try:
            # Construct the data query
            data_query = f"fields {",".join(data_fields)};" if data_fields \
                else "fields id;"
            data_query += f" limit {data_limit};" if data_limit else " limit 10;"
            
            # Make the API request
            response = requests.post(
                url=url, 
                **{"headers": {"Client-ID": client_id, 
                               "Authorization": f"Bearer {access_token}"}, 
                               "data": data_query})
            
            self.api_url = url
            self.data = response.json()
        except Exception as e:
            logging.error(f"An error occurd when trying to fetch data: {e}")


def main() -> int:
    logging.basicConfig(
        level=logging.INFO, 
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s")

    logger = logging.getLogger(__name__)
    logger.info("Hello from %s", __name__)

    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    my_data = APIData()
    auth = my_data.authenticate(client_id, client_secret)
    if auth:
        logger.info("Authentication successful")
        my_data.api_fetch("https://api.igdb.com/v4/games", 
                          client_id, auth["access_token"], 
                          ["name", "rating", "release_dates"], 5)
        if my_data.data:
            logger.info("Data fetch successful")
            print(my_data)

    return 0

if __name__ == "__main__":
    exit_code = main()
    if exit_code == 0:
        logging.info("Exited program with exit_code: 0")
    else:
        logging.info(f"Exited program with exit_code: {exit_code}")