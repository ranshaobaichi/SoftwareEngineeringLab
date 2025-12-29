"""
PocketLedger - Personal Accounting Software
"""

__version__ = "1.0.0"
__author__ = "Claude 4.5"

from .app_logic import AppLogic
from .ui_interface import IUserInterface, ConsoleUI, GUIInterface

__all__ = ['AppLogic', 'IUserInterface', 'ConsoleUI', 'GUIInterface']
