#!/usr/bin/python3.11

__created__ = "26.11.2023"
__last_update__ = "26.11.2023"
__author__ = "https://github.com/pyautoml"
__more_about_renderform__ = "https://renderform.io"

import os
import re
import sys
import json
import requests
import pandas as pd
from dataclasses import dataclass, field


@dataclass
class RenderForm:
    settings: str
    _headers: dict = field(default_factory=lambda: {})
    _img_headers: dict = field(default_factory=lambda: {})

    def __post_init__(self) -> None:
        self.settings = self._setup()
        self._img_headers = {"x-api-key": self.settings["x-api-key"], "output": "image"}
        self._headers = {
            "accept": "application/json",
            "x-api-key": self.settings["x-api-key"],
        }

    def _setup(self) -> dict:
        obligatory_keys = ["x-api-key"]

        try:
            if os.path.exists(self.settings):
                file = self.settings
            else:
                file = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), self.settings)
                )
                if not os.path.exists(file):
                    print(f"Invalid file path: {file}", flush=True)
                    sys.exit(1)

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

    def _get_template(self, template_id: str, version: str = "v2") -> dict:
        data = requests.get(
            url=f"https://api.renderform.io/api/{version}/my-templates/{template_id}",
            headers=self._headers,
        )
        return data.json()

    def _render_template(
        self,
        template_id: str,
        img_container_tag: str = None,
        text_container_tag: str = None,
        image_url: str = None,
        image_text: str = None,
        api_version: str = "v2",
        formatting: dict = {},
    ) -> None:
        """
        Formatting is customizable. Replace "mytext" to your text container tag. 'formatting' dict can be customized by adding new key-value pairs.s
        Example:
            {
                "outputExtension": ".jpg",
                "mytext.fontWeight": "400",
                "mytext.height": "30",
                "mytext.weight": "402",
                "mytext.fontFamily": "Lato"
                "mytext.y": "900",
                "mytext.x": "50",
                "mytext.rotation": "0",
                "mytext.opacity": "1",
                "mytext.color": "rgba(255, 255, 255, 1)"
            }
        """

        if image_url and img_container_tag:
            formatting[f"{img_container_tag}.src"] = image_url

        if image_text and text_container_tag:
            formatting[f"{img_container_tag}.text"] = f"{image_text}"

        response = requests.post(
            url=f"https://api.renderform.io/api/{api_version}/render",
            headers=self._img_headers,
            json={"template": template_id, "data": {formatting}},
        )
        response = response.json()
        return response["href"]


# example usage
# def main() -> None:
#     render_form = RenderForm(settings="./renderform_settings.json")
#     template_data = render_form._get_template(template_id="your_template_id")
#     print(template_data)


# if __name__ == "__main__":
#     main()
