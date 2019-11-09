from requests import get
from bs4 import BeautifulSoup

from bookoutlet_service import db
from bookoutlet_service.models import BookoutletBook, GoodreadsBook


# bookoutlet specific urls
base_url = "https://bookoutlet.com"
search_url = "https://bookoutlet.com/Store/Search?qf=All&q="
top200_url = "https://bookoutlet.com/Store/Browse?N=isTopTwoHundred&Nq=0"


def get_bestsellers():
    """
    returns Bookoutlet's best sellers which will be used to prime the database
    """

    bestsellers = []

    # get page by creating repsponse object
    params = {"size": 200}
    response = get(top200_url, params=params)

    # create soup object so we can begin grabbing items off the page
    soup = BeautifulSoup(response.content, "html.parser")

    # grab book items
    book_items = soup.find_all(class_="grid-item")
    print(len(book_items), "books on page")

    # step 4 - now to create the book object for each book
    for book_item in book_items:

        book = get_book(book_item)
        bestsellers.append(book)

        # step 5 - check db for book. If it doesn't exist add to db
        found = False
        db_query = BookoutletBook.query.filter_by(title=book.title)
        for item in db_query:
            if book == item:
                found = True
                break
        if not found:
            print("adding {} to database".format(book))
            db.session.add(book)

    db.session.commit()

    return bestsellers


def get_title(book):
    print("in getTitle function")

    link = book.a["href"]
    print("link to visit --> {}".format(base_url + link))

    response = get(base_url + link)
    print("response {}".format(response))
    soup = BeautifulSoup(response.content, "html.parser")
    print("SOUP OBJECT")
    print(soup)

    # find & grab title
    title_container = soup.find("div", {"class": "col-md-8"})
    print(title_container)
    title = title_container.h4.text

    # clean title (remove series info)
    index = title.find("(")
    if index != -1:
        series = title[index:]
        title = title[:index]

    return title


def is_match(bookoutlet_book, goodreads_book):

    # title cleanup
    bookoutlet_title = bookoutlet_book.title.strip()
    goodreads_title = goodreads_book.title.strip()

    # author cleanup
    bookoutlet_author = prep_author(bookoutlet_book.author)
    goodreads_author = prep_author(goodreads_book.author)

    # bookoutlet has incomplete title and author so check if in only not if eq
    if bookoutlet_title in goodreads_title:
        if bookoutlet_author in goodreads_author:
            print("{} & {} are a match!".format(bookoutlet_book, goodreads_book))
            return True
        else:
            return False
    else:
        return False


# cleans up and unifies author name format
def prep_author(author):

    formatted_author = author.replace(",", "").replace(".", " ")
    formatted_author = formatted_author.strip()
    formatted_author = formatted_author.split()
    formatted_author = sorted(formatted_author)

    formatted_author = " ".join(formatted_author)

    return formatted_author


# queries Bookoutlet for goodread_book
def query_bookoutlet(goodreads_book):
    print("in query bookoutlet -- book is {}".format(goodreads_book))

    results = []

    # get search result page & create soup
    search_query = goodreads_book.title.replace(" ", "+")
    response = get(search_url + search_query)
    soup = BeautifulSoup(response.content, "html.parser")

    # grab all book results on page
    book_containers = soup.find_all(class_="grid-item")

    for book_item in book_containers:

        # create BookoutletBook object
        book = get_book(book_item)

        # check db for book -- move to next book if exists
        found = False
        db_query = BookoutletBook.query.filter_by(title=book.title)
        for item in db_query:
            print("comparing {} to {}".format(book, item))
            if book == item:
                print("result is true")
                found = True
                results += [book]
                break
        if not found:
            if is_match(book, goodreads_book):
                print("adding {} to database".format(book))
                db.session.add(book)
                results += [book]

    db.session.commit()
    return results


# returns a BookoutletBook object made of attributes extracted from webpage
def get_book(book_item):
    """
    extracts certain attributes off book_item and returns BookoutletBook object
    """

    title = book_item.p.find(class_="one-line").text
    index = title.find("(")  # clean up
    if index != -1:
        title = title[:index].strip()

    author = book_item.p.select(".one-line")[1].get_text()

    price = book_item.find(class_="price").get_text()

    format = book_item.p.find(class_="small").get_text().strip("()")

    if book_item.find(class_="price green"):
        scratch_n_dent = True  # a scratch & dent copy
    else:
        scratch_n_dent = False

    link = base_url + (book_item.find("a", href=True)["href"])

    # create BookoutletBook object to be added to db
    book = BookoutletBook(
        title=title,
        author=author,
        price=price,
        format=format,
        scratch_n_dent=scratch_n_dent,
        link=link,
    )

    return book


if __name__ == "__main__":

    count = BookoutletBook.query.count()
    print("start count = {} books in database".format(count))

    print("### testing get bestsellers function ###")
    bestsellers = get_bestsellers()

    print("rechecking count")
    count = BookoutletBook.query.count()
    print("{} books in database".format(count))

    print("\n ### testing query bookoutlet function ###")
    goodreads_book = GoodreadsBook(
        title="Shadowcaster",
        title_series="Shattered Realms",
        author="Cinda Williams Chima",
    )

    results = query_bookoutlet(goodreads_book)
    print("{} matches found".format(len(results)))
    print(results, "\n")
    print("checking if they were added to db >> ")
    allbooks = BookoutletBook.query.all()
    for result in results:
        print(result in allbooks)

    # cleanup db
    print("cleaning up db by deleting all items...")
    BookoutletBook.query.delete()
    db.session.commit()
    print("rechecking count")
    count = BookoutletBook.query.count()
    print("{} books in database".format(count))

    # print('\n ### testing eq func ###')
    # print('{} == {}?'.format(book1, book1))
    # print(book1 == book1)
