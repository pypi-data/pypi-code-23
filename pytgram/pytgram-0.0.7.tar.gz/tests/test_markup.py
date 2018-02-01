from unittest import TestCase

from pytgram.markup import (
    ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton,
    KeyboardButton
)


class TestKeyboard(TestCase):

    def test_reply_keyboard_from_str(self):
        f_row = ['One', 'Two', 'Three']
        s_row = ['Four', 'Five', 'Six']
        kb_ = [f_row, s_row]
        kb = ReplyKeyboardMarkup(kb_)
        self.assertEqual(len(kb.keyboard), 2)
        for row in kb.keyboard:
            for button in row:
                self.assertIsInstance(button, KeyboardButton)

    def test_reply_keyboard_from_button(self):
        f_row = [KeyboardButton('One'), KeyboardButton('Two'),
                 KeyboardButton('Three')]
        s_row = [KeyboardButton('Four'), KeyboardButton('Five'),
                 KeyboardButton('Six')]
        kb_ = [f_row, s_row]
        kb = ReplyKeyboardMarkup(kb_)
        self.assertEqual(len(kb.keyboard), 2)

    def test_reply_keyboard_add_row_from_str(self):
        kb = ReplyKeyboardMarkup()
        kb.add_button_row('One', 'Two', 'Three')
        kb.add_button_row('Four', 'Five', 'Six')
        self.assertEqual(len(kb.keyboard), 2)
        for row in kb.keyboard:
            for button in row:
                self.assertIsInstance(button, KeyboardButton)

    def test_reply_keyboard_add_row_from_btn(self):
        kb = ReplyKeyboardMarkup()
        kb.add_button_row(KeyboardButton('One'), KeyboardButton('Two'),
                          KeyboardButton('Three'))
        kb.add_button_row(KeyboardButton('Four'), KeyboardButton('Five'),
                          KeyboardButton('Six'))
        self.assertEqual(len(kb.keyboard), 2)

    def test_reply_keyboard_to_dict(self):
        kb = ReplyKeyboardMarkup()
        kb.add_button_row('One', 'Two')
        kb.add_button_row('Three', 'Four')
        kb_dict = kb.to_dict()
        for row in kb_dict['keyboard']:
            for button in row:
                self.assertIsInstance(button, dict)

    def test_inline_keyboard_from_button(self):
        f_row = [InlineKeyboardButton('One'), InlineKeyboardButton('Two'),
                 InlineKeyboardButton('Three')]
        s_row = [InlineKeyboardButton('Four'), InlineKeyboardButton('Five'),
                 InlineKeyboardButton('Six')]
        th_row = [InlineKeyboardButton('Seven')]
        kb_ = [f_row, s_row, th_row]
        kb = InlineKeyboardMarkup(kb_)
        self.assertEqual(len(kb.keyboard), 3)

    def test_inline_keyboard_add_row_from_btn(self):
        kb = InlineKeyboardMarkup()
        kb.add_button_row(InlineKeyboardButton('One'),
                          InlineKeyboardButton('Two'),
                          InlineKeyboardButton('Three'))
        kb.add_button_row(InlineKeyboardButton('Four'),
                          InlineKeyboardButton('Five'),
                          InlineKeyboardButton('Six'))
        kb.add_button_row(InlineKeyboardButton('Seven'))
        self.assertEqual(len(kb.keyboard), 3)

    def test_inline_keyboard_to_dict(self):
        kb = InlineKeyboardMarkup()
        kb.add_button_row(InlineKeyboardButton('One'),
                          InlineKeyboardButton('Two'),
                          InlineKeyboardButton('Three'))
        kb.add_button_row(InlineKeyboardButton('Four'),
                          InlineKeyboardButton('Five'),
                          InlineKeyboardButton('Six'))
        kb.add_button_row(InlineKeyboardButton('Seven'))
        kb_dict = kb.to_dict()
        for row in kb_dict['inline_keyboard']:
            for button in row:
                self.assertIsInstance(button, dict)
