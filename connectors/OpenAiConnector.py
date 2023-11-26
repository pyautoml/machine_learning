import os
import sys
import json
import openai
import requests
from typing import Any
from dataclasses import dataclass, field


@dataclass
class OpenAiConnector:
    settings: str
    _api_key: str = None
    _organization: str = None
    _headers: dict = field(default_factory=lambda: {})

    def __post_init__(self) -> None:
        api_settings = self._setup()
        self._api_key = api_settings["api_key"]
        self._organization = api_settings["organization"]
        self._headers = {
            "Authorization": f"Bearer {self._api_key}",
            "OpenAI-Organization": f"{self._organization}",
        }
        self._client = openai.OpenAI(api_key=self._api_key)
        print("Successfull data setup.")

    def _setup(self) -> dict:
        obligatory_keys = ["api_key", "organization"]

        try:
            # verify file path
            if os.path.exists(self.settings):
                file = self.settings
            else:
                file = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), self.settings)
                )
                if not os.path.exists(file):
                    print(f"Invalid file path: {file}", flush=True)
                    sys.exit(1)

            # load settings data
            with open(file, "r") as f:
                loaded_data = json.load(f)

            for key in obligatory_keys:
                if key not in loaded_data.keys():
                    print(f"Missing {key} key in json settings file.", flush=True)
                    sys.exit(1)
            return loaded_data
        except Exception as e:
            print(f"Cannot find or load settings: {e}", flush=True)
            sys.exit(1)

    def _generate_embedding(
        self,
        message: str,
        api_version: str = "v1",
        metadata: bool = False,
        embeddings_endpoint: str = None,
        embedding_type: str = "text-embedding-ada-002",
    ) -> Any:
        if not message:
            print("Message cannot be empty.", flush=True)
            sys.exit(1)

        if not embeddings_endpoint:
            embeddings_endpoint = f"https://api.openai.com/{api_version}/embeddings"

        data = {"input": message, "model": embedding_type}

        try:
            response = requests.post(
                embeddings_endpoint, headers=self._headers, json=data
            )
            response = response.json()

            try:
                if metadata:
                    return response["data"]
                else:
                    return response["data"][0]["embedding"]
            except KeyError as e:
                print(f"Missing keys in response: {response.text}", flush=True)
                sys.exit(1)

        except Exception as e:
            print(f"Post error: {e}", flush=True)
            sys.exit(1)

    def _prompt(
        self, prompt: str, model="gpt-4", max_tokens=300, temperature=0.4
    ) -> str:
        try:
            response = self._client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error: prompt OpenAi {e}")
            sys.exit(1)

    def _vision_prompt(self, text: str, url: str, model: str = "gpt-4-vision-preview"):
        print("Url: ", url)
        print()

        response = self._client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": text,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": url,
                            },
                        },
                    ],
                }
            ],
            max_tokens=330,
        )

        return response.choices[0].message.content


# example usage
# def main() -> None:
#     open_ai = OpenAiConnector(settings="./openai_settings.json")
#     embedding = open_ai._generate_embedding(message="Cats are cool :)")
#     print(embedding)

# if __name__ == "__main__":
#     main()
