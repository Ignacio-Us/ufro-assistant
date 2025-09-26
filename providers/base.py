from abc import ABC, abstractmethod
from typing import List, Dict

class Provider(ABC):
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Enviar mensajes al modelo y devolver la respuesta"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre del proveedor"""
        pass
