import string
import tkinter as tk


def is_both(char):
    return char == ' ' or '0' <= char <= '9' or char in string.punctuation


def is_hebrew(char):
    return 'א' <= char <= 'ת' or is_both(char)


def is_english(char):
    return 'a' <= char <= 'z' or 'A' <= char <= 'Z' or is_both(char)


def move_punctuations(s: str):
    if not s:
        return s
    start_spaces = ''
    end_spaces = ''
    for char in s:
        if char in string.punctuation + ' ':
            start_spaces += char
        else:
            break
    for char in s[::-1]:
        if char in string.punctuation + ' ':
            end_spaces += char
        else:
            break
    return end_spaces + s.lstrip(start_spaces).rstrip(end_spaces) + start_spaces


def hebrew_reshaper(text):
    sub_texts = text.split('\n')
    new_strings = []
    for text in sub_texts:
        if not text:
            new_strings.append('')
            continue

        breaks = []
        is_current_hebrew = not is_english(text[0])
        contain_hebrew = is_current_hebrew
        current_text = ''

        for char in text:
            if is_current_hebrew:
                if is_hebrew(char):
                    current_text += char
                else:
                    breaks.append((current_text, is_current_hebrew))
                    current_text = char
                    is_current_hebrew = False
            else:
                if is_english(char):
                    current_text += char
                else:
                    breaks.append((current_text, is_current_hebrew))
                    current_text = char
                    is_current_hebrew = True
                    contain_hebrew = True
        breaks.append((current_text, is_current_hebrew))
        breaks = breaks[::-1]

        if contain_hebrew:
            for i in range(len(breaks)):
                part, is_heb = breaks[i]
                part = move_punctuations(part)
                breaks[i] = (part, is_heb)
        new_strings.append(''.join([part for part, _ in breaks]))
    return '\n'.join(new_strings)


def main():
    root = tk.Tk()
    text = '-=-=asdf82this is full english!@#'
    text = hebrew_reshaper(text)
    label = tk.Label(root, text=text)
    label.pack(fill=tk.BOTH)
    root.mainloop()


if __name__ == '__main__':
    main()
