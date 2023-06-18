import typing
import time
import mouse
import keyboard

"""
Configuration Values. The characters width, rows and pages are taken from
- https://minecraft.fandom.com/wiki/Language#Font
- https://minecraft.fandom.com/wiki/Book_and_Quill
"""
FILE_NAME = "input.txt"     # Name of the file to use
MAX_WIDTH = 114             # Max width by pixels.
MAX_ROWS = 14               # Max number of lines
MAX_PAGES = 100             # Max number of pages
MAX_TITLE = 15              # Max characters the title has
BOTTOM_BAR = 9              # How many spaces the bottom bar has. Always been 9, but just in case it changes

char_width = 5              # Default width of characters.
characters = {              # Other characters with different width
    " ": 3, "!": 1, "\"": 3, "'": 1, "(": 3, ")": 3, "*": 3, ",": 1, ".": 1, ":": 1, ";": 1, "<": 4, ">": 4, "@": 6,
    "I": 3, "[": 3, "]": 3, "`": 2, "f": 4, "i": 1, "k": 4, "l": 2, "t": 3, "{": 3, "|": 1, "}": 3, "~": 6,
    "\n": 0
}
# Characters that require Shift to be pressed
shift_characters = ["{", "}", ":", "\"", "<", ">", "?", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "+", "~"]


def pause() -> None:
    """
    Wait for the user to press Enter. In theory, the user should have a book out.
    So, when they press enter, it'll backspace to remove the next line.

    :return: None
    """
    print("Press enter when ready.")
    keyboard.wait("ENTER")
    keyboard.press("BACKSPACE")


def wait() -> None:
    """
    Pause the program. This is mainly used between inputs. If it goes too fast, the inputs won't register.
    :return:
    """
    time.sleep(0.001)


def move_mouse(*args, **kwargs) -> None:
    """
    Calls mouse.move to move the mouse. This basically adds a delay before continuing.

    :param args:    args to give mouse.move
    :param kwargs:  kwargs to give mouse.move
    :return: None
    """
    mouse.move(*args, **kwargs)
    time.sleep(0.1)


def get_words() -> typing.Generator[str, None, None]:
    """
    Goes through the input file and yields all the words found.
    Mainly any words separated by space, empty string or next line.

    :return: typing.Generator[str, None, None]
    """
    with open(FILE_NAME, "r") as file:
        # Yield all of the words
        word = ""
        while True:
            # Grabbing the char and adding it to the word
            char = file.read(1)
            word += char

            # Checking if it's at the end of the file. If there is a word, then yield the word and loop.
            if word == "" and char == "":
                break

            # Checking if it's at the end of the word.
            elif char == "\n" or char == "" or char == " ":
                yield word
                word = ""


def get_width(word: str) -> int:
    """
    Grabs the length of the word in pixels.

    :param word:    str, word
    :return:        int, length
    """
    width = 0
    for i, c in enumerate(word):
        # If its a space, ignore it. It'll be calculated later
        if c == " ":
            continue

        # Checking if it's a special character. Then add it to total width
        if c not in characters:
            width += char_width
        else:
            width += characters[c]

        # I'll be honest, this if statement fixed a bug and I'm not sure how.
        if i != len(word) - 1:
            width += 1  # There is a space between characters
    return width


def type_word(word: str) -> None:
    """
    Types out the word by using the keyboard library

    :param word:    str, word to type out
    :return:        None
    """
    for c in word:
        wait()
        # If the character is upper case or needs shift to be pressed
        if c.isupper() or c in shift_characters:
            keyboard.press("SHIFT")

        # Press the character on the keyboard
        c = c.lower()
        keyboard.send(c)
        keyboard.release("SHIFT")


def next_page(pos_next_page: tuple) -> None:
    """
    Goes to the next page of the book. This uses pos_next_page to get the position of the next page button.

    :return: None
    """
    move_mouse(*pos_next_page)
    mouse.click("left")


def sign(book_name: str, pos_sign: tuple, number=None, next_book=None) -> None:
    """
    Sign the book. This uses pos_sign to get the position of the sign button. Also uses book_name to get the name.

    If next_book is None, it won't go to the next empty book

    :param pos_sign:    tuple or list, position of
    :param number:      str, book number
    :param next_book:   str, next book's number. This is used to grab the next book in the bar on the bottom
    :return: None
    """
    time.sleep(0.2)

    # Grabbing the name. Also adding the number to the name
    title = book_name
    if number is not None:
        title += f" {number}"

    # Checking if the book's name is too large
    if len(title) > MAX_TITLE:
        temp = ".."
        if number is not None:
            temp += f" {number}"

        title = book_name[:MAX_TITLE - len(temp)] + temp

    # Signing the book
    move_mouse(*pos_sign)
    mouse.click("left")
    type_word(title)
    # Exiting the book
    move_mouse(*pos_sign)
    mouse.click("left")

    # Going to the next book
    if next_book is not None:
        wait()
        keyboard.press(next_book)
        mouse.click("right")

    time.sleep(0.2)


def write_book(book_name=None, pos_next_page=None, pos_sign=None, start_page=1, start_book=1,
               type_book=True, numbers=True) -> int:
    """
    Main function. This will start typing out words from the input file. It will keep track on when to go to
    the next page / book.

    :param start_page:  int, page to start at
    :param start_book:  int, book to start at
    :param type_book:   bool, type out the words or not. This is mainly used if you wanted to
                            see how many pages / books it will use before typing it out.
    :param numbers:     bool, If true, it'll add numbers to the title of the book. As in, which book it is
    :return:            How many books it took to write the input
    """

    def do_type() -> bool:
        return start_book <= book and start_page <= page and type_book

    row = 1  # Current row
    page = 1  # Current page
    book = 1  # Current book
    tool_book = 1  # Current book on the toolbar
    row_width = 0  # Current row's width in pixels

    for word in get_words():
        width = get_width(word)  # Grabbing how big the word is
        max_width = MAX_WIDTH - row_width  # Grabbing how much room the row has.
        row_width += width  # Adding it to the row's width

        if width > MAX_WIDTH:
            # Word is too big for the row. It may take one or multiple rows
            # TODO: Calculate how many rows the word will take
            row += 1
            row_width = width

        elif width > max_width:
            # Word won't fit on the row
            row += 1
            row_width = width

        if row > MAX_ROWS:
            # Reached the end of the page
            if do_type():
                next_page(pos_next_page)
            page += 1
            row = 1
            row_width = width

        if page > MAX_PAGES:
            # Reached the end of the book
            if do_type():
                print("End of book reached.")
                tool_book += 1

                # Used to give sign() the number of the book. If numbers is false, it'll give it None
                if numbers:
                    temp = str(book)
                else:
                    temp = None

                # Checking if we have enough books in the toolbar
                if tool_book > BOTTOM_BAR:
                    tool_book = 1
                    sign(book_name, pos_sign, number=temp)
                    print("Ran out of books in the toolbar. Grab more books.")
                    pause()
                else:
                    sign(book_name, pos_sign, number=temp, next_book=str(tool_book))
            book += 1
            page = 1

        if " " in word:
            # Adding in space
            row_width += characters[" "] + 1

        if "\n" in word:
            row += 1
            row_width = 0

        if do_type():
            type_word(word)
            print(f"B: {book}, PG {page} - [{row} / {MAX_ROWS}] - {row_width} / {MAX_WIDTH} - {word} ({width})")

    # Sign the book
    if do_type():
        if numbers:
            sign(book_name, pos_sign, number=str(book))
        else:
            sign(book_name, pos_sign)

    print(f"Books: {book}. Pages {page}")
    return book


def main():
    # Telling the user how many books / pages it'll take. Also grabbing the total books
    total = write_book(type_book=False)

    # If there is only 1 book. Tell write_book not to have numbers in the title.
    if total == 1:
        numbers = False
    else:
        numbers = True

    book_name = input(f"\nEnter the name of the book. Note, the max is {MAX_TITLE} characters. It can decrease if"
                      f" there are multiple books -> ")

    print("\nFocus minecraft and grab a book. If there are multiple books required, make sure its in first position in "
          "your toolbar")
    pause()

    print("\nPress the next page button, then back.")
    mouse.wait(target_types=["down"])
    pos_next_page = mouse.get_position()
    mouse.wait(target_types=["down"])
    print(pos_next_page)

    print("\nPress Sign then Cancel.")
    mouse.wait(target_types=["down"])
    pos_sign = mouse.get_position()
    mouse.wait(target_types=["down"])
    print(pos_sign)

    pause()
    write_book(book_name=book_name, pos_next_page=pos_next_page, pos_sign=pos_sign, numbers=numbers)


if __name__ == "__main__":
    main()
