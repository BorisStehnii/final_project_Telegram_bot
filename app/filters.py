from telegram import Message
from telegram.ext import MessageFilter
import re


class PhoneFilter(MessageFilter):

    def filter(self, message: Message):
        return re.search(r'(\s*)?(\+)?([- _():=+]?\d[- _():=+]?){9,14}(\s*)?', message.text)


class AddressFilter(MessageFilter):

    def filter(self, message: Message):
        return type(message.text) == str
