from goodreads_api import getUser, getPage, getBooks
from bookoutlet import queryBookOutlet, checkMatch
import csv

# put into functions, add main

print('starting test...')

member_ids = {'emma': '32879029', 'tara': '25083955', 'regan': '19645927',
              'miranda_readsmi': '71848701', 'julie': '5210022',
              'dianeS': '4159922'}

# sample book that I know is currently available on Bookoutlet
gr_book = ("The Thief (The Queen's Thief, #1)", "The Thief",
           "Megan Whalen Turner")


toRead_root = getPage(1, member_ids['emma'])
toRead_books = getBooks(toRead_root)


print('** testing queryBookOutlet function **')

bookoutlet_results = queryBookOutlet(gr_book)
print('bookoutlet result:', bookoutlet_results)


# filename = 'matches.csv'
# f = open(filename, "w")
#
# headers = ['Title', 'Author', 'Price', 'Edition', 'Scratch and Dent?']
#
# writer = csv.writer(f, dialect='excel')
# writer.writerow(headers)

# matches = [book for result in results for book in result]

# writer.writerows(bookoutlet_results)


# print('** testing checkMatch function **')
# is_match = checkMatch(bookoutlet_results, toRead_book)
# print(is_match)


print('** END OF TEST **')


def testCheckMatch(book1, book2):
    is_match = bookoutlet.checkMatch(bookoutlet_results, toRead_book)
    print("Testing', book1, 'and', book2 'for match...")
    print(is_match)
