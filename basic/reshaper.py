import string
# import tkinter as tk


REVERSE = {'(': ')', ')': '('}


def is_both(char):
    return char == ' ' or '0' <= char <= '9' or char in string.punctuation


def is_hebrew(char):
    return 'א' <= char <= 'ת' or is_both(char)


def is_english(char):
    return 'a' <= char <= 'z' or 'A' <= char <= 'Z' or is_both(char)


def move_punctuations(s: str):
    """
    this function swipe punctuations from start to end
    for example: '!@#abc%$#' -> '#$%abc!@#'
    """
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
    new_start = ''.join([REVERSE[c] if c in REVERSE else c for c in end_spaces])
    new_end = ''.join([REVERSE[c] if c in REVERSE else c for c in start_spaces])
    return new_start + s.lstrip(start_spaces).rstrip(end_spaces) + new_end


def hebrew_reshaper(text: str):
    sub_texts = text.split('\n')
    new_strings = []
    for sub_text in sub_texts:
        if not sub_text:
            new_strings.append('')
            continue

        breaks = []
        is_current_hebrew = not is_english(sub_text[0])
        contain_hebrew = is_current_hebrew
        current_text = ''

        for char in sub_text:
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
                if part.endswith(')') and not is_heb:
                    part = '(' + part[:-1]
                part = move_punctuations(part)
                breaks[i] = (part, is_heb)
        new_string = ''.join([part for part, _ in breaks])
        new_strings.append(new_string)
    return '\n'.join(new_strings)


# def main():
#     """ this is some test code"""
#     root = tk.Tk()
#     text = "hello מה)) קורה? WITH YOU!%^ הכל טוב (נראלי)"
#     text = hebrew_reshaper(text)
#     label = tk.Label(root, text=text)
#     label.pack(fill=tk.BOTH)
#     root.mainloop()


# if __name__ == '__main__':
#     main()
