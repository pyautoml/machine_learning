#!/usr/bin/python3.11

__created__ = "27.01.2024"
__last_update__ = "27.01.2024"
__author__ = "https://github.com/pyautoml"
__version__ = "1.0.0"


"""
This file provides a variety of classes that offer connections for each specified service:
- OpenAi (api_key/token, organization_id)
- HuggingFace (api_key/token)

Create a connector instance and use `print(instance._help())` to get more information.
"""

import gc
import sys
from logger import logger
from typing import Optional, Self
from abc import ABC, abstractmethod
from settings import SettingsLoader
from dataclasses import dataclass, field


class AbstractConnector(ABC):
    @abstractmethod
    def _load_settings(self) -> None:
        pass


@dataclass
class OpenAIConnector(AbstractConnector):
    settings_path: str
    _api_key: str = None
    _instance: Self = None
    _initialized: bool = False
    _use_organization_id: bool = True
    _organization_id: Optional[str] = None
    _available_models: list = field(default_factory=list)

    def __setattr__(self, name, value):
        if self._initialized and name in self.__annotations__:
            raise AttributeError(
                f"Cannot modify attribute '{name}' after initialization."
            )
        super().__setattr__(name, value)

    def __post_init__(self):
        if not self._initialized:
            self._load_settings()
        self._initialized = True

    def _load_settings(self) -> None:
        try:
            settings = SettingsLoader(
                settings_path=self.settings_path
            ).load_credentials()
            settings = settings["connector"]["openai"]
            self._api_key = settings["api_key"]
            if self._use_organization_id:
                self._organization_id = settings["organization_id"]
            self._available_models = settings["model"]
            del settings
            gc.collect()
        except KeyError as e:
            logger.critical(f"Missing key in settings: {e}")
            sys.exit(1)
        except Exception as e:
            logger.critical(f"Cannot parse credentials file: {e}")
            sys.exit(1)

        if not self._initialized:
            try:
                if self._use_organization_id:
                    if not (self._api_key and self._use_organization_id):
                        logger.critical(
                            f"Missing _api_key or _organization_id. Cannot connect to OpenAI: {e}"
                        )
                        sys.exit(1)
                else:
                    if not self._api_key:
                        logger.critical(
                            f"Missing _api_key. Cannot connect to OpenAI: {e}"
                        )
                        sys.exit(1)
            except KeyError as e:
                logger.critical(f"Missing key in settings: {e}")
                sys.exit(1)
            except Exception as e:
                logger.critical(f"Exception error: {e}")
                sys.exit(1)

    def _help(self) -> str:
        return """
        1) Variables
            .. settings_path: str -> path to your local file containing credentials. By default you can find a predefined file in ./settings/credentials.json
            .. _api_key: str = None -> api key / token you need to create on OpenAI's website.
            .. _instance: Self = None -> this class instance; for the singleton class all new instances will share the same id.
            .. _initialized: bool = False -> once the non-singleton class is initialized, it's not possible to change values of the class' attributes. New attributes can be added. 
            .. _use_organization_id: bool -> specify if you want your class to utilize organization's id value.
            .. _organization_id: Optional[str] -> It is not always necessary to use organization's id. If you don't need it, state 'null' in the ./settings/credentials.json file and set _use_organization_id = False.
            .. _available_models: list -> you can specify in the ./settings/credentials.json OpenAI's models you'd like to use in this project. 
                
        2) API and usage
        To use OpenAI's API, you need to create an account: https://openai.com
        
        .. [budget treshold] Go to 'Settings' > 'Limits' and enter value for one or both:
            - 'Set a monthly budget'
            - 'Set an email notification threshold'
        
        .. [_api_key] a unique token you need to connec to to OpenAI:
            - Log in & go to click API.
            - Click 'API keys' to create new api key.
            - Go to 'settings' dir and paste your _organization_id into: connector": {"openai": {"api_key": " PASTE_HERE "}} 
        
        .. [_organization_id] (optional): not always, but also needed to use OpenAI's API.
            - Log in & go to click API.
            - Click 'Settings' to find your Organization ID.
            - Go to './settings' dir and paste your _organization_id into:connector": {"openai": {"organization_id": " PASTE_HERE  "}} 

        .. [path] 
            For Linux environments it is better to provide an absolute path to the file:
                os.path.abspath(os.path.join(os.path.dirname(__file__, "you_file_path")))

        .. [how to use]
            settings_path = "settings/credentials.json"
            
            > to create many singleton-pattern instances use:
                open_ai = OpenAIConnector(settings_path=settings_path)
        
            > to create standard instance use:
                open_ai = OpenAISingletonConnector(settings_path=settings_path)

            > to verify is instances are singletons or not, you can use the code below:
                path = "settings/credentials.json"
                open_ai0 = OpenAIConnector(path)
                open_ai1 = OpenAIConnector(path)
                open_ai2 = OpenAISingletonConnector(path)
                open_ai3 = OpenAISingletonConnector(path)

                print(id(open_ai0) == id(open_ai1)) # False
                print(id(open_ai1) == id(open_ai2)) # False
                print(id(open_ai2) == id(open_ai3)) # True

                del open_ai0
                del open_ai1
                del open_ai2
                del open_ai3
                gc.collect()
        """

    def __str__(self) -> str:
        return "OpenAI connector. Use print_help() to read more."

    def __repr__(self) -> str:
        return "OpenAI connector. Use print_help() to read more."


class OpenAISingletonConnector(OpenAIConnector):
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(OpenAIConnector, cls).__new__(cls)
        return cls._instance

    def __setattr__(self, name, value):
        if name in self.__annotations__.keys():
            super().__setattr__(name, value)

    def __post_init__(self):
        if not self._initialized:
            self._load_settings()


@dataclass
class HuggingFaceConnector:
    settings_path: str
    _api_key: str = None
    _instance: Self = None
    _initialized: bool = False

    def __setattr__(self, name, value):
        if self._initialized and name in self.__annotations__:
            raise AttributeError(
                f"Cannot modify attribute '{name}' after initialization."
            )
        super().__setattr__(name, value)

    def __post_init__(self):
        if not self._initialized:
            self._load_settings()
            self._initialized = True

    def _load_settings(self) -> None:
        settings = SettingsLoader(settings_path=self.settings_path).load_credentials()
        settings = settings["connector"]["huggingface"]
        self._api_key = settings["api_key"]
        del settings
        gc.collect()

    def _help(self) -> str:
        return """
        1) Variables
            .. settings_path: str -> path to your local file containing credentials. By default you can find a predefined file in ./settings/credentials.json
            .. _api_key: str = None -> api key / token you need to create on Huggingface website.
            .. _instance: Self = None -> this class instance; for the singleton class all new instances will share the same id.
            .. _initialized: bool = False -> once the non-singleton class is initialized, it's not possible to change values of the class' attributes. New attributes can be added. 
        
        2) API and usage
        To use Huggingcafe's API, you need to create an account: https://huggingface.co
        
        .. [_api_key] a unique token you need to connec to to OpenAI:
            - Click 'Settings' > 'Access Token'.
            - Go to './settings' dir and paste your token into: connector": {"huggingface": {"api_key": " PASTE_HERE "}} 
        
        .. [path] 
            For Linux environments it is better to provide an absolute path to the file:
                os.path.abspath(os.path.join(os.path.dirname(__file__, "you_file_path")))

        .. [how to use]
            settings_path = "settings/credentials.json"
            
            > to create many singleton-pattern instances use:
                open_ai = OpenAIConnector(settings_path=settings_path)
        
            > to create standard instance use:
                open_ai = OpenAISingletonConnector(settings_path=settings_path)

            > to verify is instances are singletons or not, you can use the code below:
                path = "settings/credentials.json"
                hugging_face0 = HuggingFaceConnector(path)
                hugging_face1 = HuggingFaceConnector(path)
                hugging_face2 = HuggingFaceSingletonConnector(path)
                hugging_face3 = HuggingFaceSingletonConnector(path)

                print(id(hugging_face0) == id(hugging_face1)) # False
                print(id(hugging_face1) == id(hugging_face2)) # False
                print(id(hugging_face2) == id(hugging_face3)) # True

                del hugging_face0
                del hugging_face1
                del hugging_face2
                del hugging_face3
                gc.collect()
        """

    def __str__(self) -> str:
        return "Connected to HuggingFace Service"

    def __repr__(self) -> str:
        return "Connected to HuggingFace Service"


class HuggingFaceSingletonConnector(HuggingFaceConnector):
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(HuggingFaceConnector, cls).__new__(cls)
        return cls._instance

    def __setattr__(self, name, value):
        if name in self.__annotations__.keys():
            super().__setattr__(name, value)

    def __post_init__(self):
        if not self._initialized:
            self._load_settings()
