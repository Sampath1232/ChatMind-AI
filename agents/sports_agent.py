import os
import requests

from dotenv import load_dotenv

load_dotenv()


class SportsAgent:

    def __init__(self):

        self.api_key = os.getenv(
            "CRIC_API_KEY"
        )

    def get_ipl_score(self):

        try:

            if not self.api_key:

                return (
                    "Cricket API key not configured."
                )

            url = (
                "https://api.cricapi.com/v1/matches"
            )

            params = {

                "apikey": self.api_key,

                "offset": 0
            }

            response = requests.get(

                url,

                params=params,

                timeout=10
            )

            if response.status_code != 200:

                return (
                    f"API Error: "
                    f"{response.status_code}"
                )

            data = response.json()

            matches = data.get(
                "data",
                []
            )

            if not matches:

                return (
                    "No cricket matches found."
                )

            ipl_keywords = [

                "ipl",
                "indian premier league",
                "mumbai indians",
                "royal challengers",
                "chennai super kings",
                "kolkata knight riders",
                "sunrisers hyderabad",
                "rajasthan royals",
                "delhi capitals",
                "punjab kings",
                "gujarat titans",
                "lucknow super giants",

                "mi",
                "rcb",
                "csk",
                "kkr",
                "srh",
                "rr",
                "dc",
                "pbks",
                "gt",
                "lsg"
            ]

            results = []

            for match in matches:

                match_name = match.get(
                    "name",
                    ""
                )

                match_name_lower = (
                    match_name.lower()
                )

                # IPL FILTER
                if not any(
                    keyword in match_name_lower
                    for keyword in ipl_keywords
                ):

                    continue

                status = match.get(
                    "status",
                    "No status available"
                )

                date = match.get(
                    "date",
                    "Unknown Date"
                )

                score = ""

                if match.get("score"):

                    for inning in match["score"]:

                        score += (

                            f"{inning.get('inning')}: "

                            f"{inning.get('r')}/"

                            f"{inning.get('w')} "

                            f"({inning.get('o')} ov)\n"
                        )

                results.append(

                    f"🏏 {match_name}\n\n"

                    f"📅 {date}\n\n"

                    f"{score}"

                    f"📊 {status}"
                )

            if not results:

                return (
                    "No IPL matches found."
                )

            return "\n\n".join(results[:5])

        except Exception as e:

            return (
                f"Sports Agent Error: {str(e)}"
            )