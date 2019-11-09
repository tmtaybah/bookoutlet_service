import os
import time
import configparser
from math import ceil

from requests import get
import xml.etree.ElementTree as ET

from bookoutlet_service.models import GoodreadsBook
from bookoutlet_service.core.goodreads_oauth import establish_session


base_url = "https://www.goodreads.com/"

# read developer key
config = configparser.ConfigParser()
config.read("goodreads.env")
developer_key = config["goodreads"]["key"]
# developer_key = os.environ.get('GR_KEY')


# returns user(id, name) tuple from goodreads' get user api call
# takes in oauth session object as param
def get_user(session):

    response = session.get(base_url + "api/auth_user", header_auth=True)

    if response.status_code != 200:
        raise Exception(
            "Could not get user ID -- Error {}".format(response.status_code)
        )
    else:
        response_str = response.content.decode("utf-8")

    # get XML tree root
    root = ET.fromstring(response_str)

    # extract user info (id, name)
    user_node = root.find("./user")
    id = user_node.get("id")
    name = user_node.find("name").text
    user = (id, name)
    print("user details: {}".format(user))

    return user


# returns a dictionary of shelf names and number of books on each shelf
def get_user_shelves(user_id):

    # extracts only the first page
    params = {"key": developer_key, "user_id": user_id}

    response = get("https://www.goodreads.com/shelf/list.xml", params=params)
    response_str = response.content.decode("utf-8")

    # get XML tree root
    root = ET.fromstring(response_str)

    shelves = {}

    shelf_nodes = root.findall("./shelves/user_shelf")
    print("{} shelves extracted".format(len(shelf_nodes)))

    for shelf in shelf_nodes:
        shelf_name = shelf.find("name").text
        book_count = shelf.find("book_count").text

        shelves[shelf_name] = book_count

    return shelves


# makes api call to get books on member's shelf and returns an ET root
# shelf is hardcoded right now
def get_page(page_num, member_id, shelf):

    # request to-read page with aprop params and get response in str format
    params = {
        "id": member_id,
        "shelf": shelf,
        "key": developer_key,
        "per_page": 200,
        "page": page_num,
    }

    response = get(base_url + "/review/list?v=2", params=params)
    response_str = response.content.decode("utf-8")

    # pass str response to xml parser
    toRead_root = ET.fromstring(response_str)

    return toRead_root


# takes an ET root and returns a list of books on the page
def get_books(root):

    books = []
    book_nodes = root.findall("./reviews/review/book")

    # grab feilds we're interested in
    for book in book_nodes:
        title_series = book.find("title").text
        title = book.find("title_without_series").text
        author = book.find("authors/author/name").text

        book = GoodreadsBook(title=title, title_series=title_series, author=author)
        books += [book]

    return books


# returns total number of xml pages to loop over in member's to-read shelf
def find_total_pages(root):
    max_per_page = 200

    total_books = int(root.find("./reviews").attrib["total"])
    total_pages = ceil(total_books / max_per_page)

    return total_pages


# returns a given member's to-read shelf
def get_bookshelf(member_id, shelf="to-read"):

    print("get_bookshelf called with member id {}".format(member_id))
    # a list of tuples with book attributes
    toRead_books = []

    page_num = 1
    root = get_page(page_num, member_id, shelf)
    total_pages = find_total_pages(root)

    # add books from first result page
    toRead_books += get_books(root)

    for page in range(2, total_pages + 1):
        root = get_page(page, member_id, shelf)
        toRead_books += get_books(root)

    print("{} books on to-read shelf".format(len(toRead_books)))
    print(toRead_books)

    return toRead_books


if __name__ == "__main__":

    print("##### testing get_user() #####")
    session = establish_session()
    user = get_user(session)
    print("user is; {}".format(user))
    user_id = user[0]
    user_name = user[1]

    print("##### testing get_user_shelves() #####")
    shelves = get_user_shelves(user_id)
    print("{}'s shelves: \n{}".format(user_name, shelves))

    print("##### testing get_bookshelf() #####")
    start = time.time()

    print("getting {46476449}'s to-read shelf")
    bookshelf = get_bookshelf(46476449)
    print(bookshelf)

    end = time.time()

    print("run-time {} s".format(end - start))

    print("##### testing get_bookshelf() with read shelf arg #####")
    start = time.time()

    print("getting {}'s to-read shelf".format(user_name))
    bookshelf = get_bookshelf(user_id, "read")
    print(bookshelf)

    end = time.time()

    print("run-time {} s".format(end - start))
