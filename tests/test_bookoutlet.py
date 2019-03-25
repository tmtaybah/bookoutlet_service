import time
from bookoutlet_service.core import bookoutlet, goodreads_api


if __name__ == '__main__':

    # step 1. establish oauth session
    session = goodreads_api.establish_session()


    # step 2. get goodreads user
    user = goodreads_api.get_user(session)
    user_id = user[0]
    username = user[1]


    # step 3. get the user's bookshelf
    bookshelf = goodreads_api.get_bookshelf(user_id)


    # step 4. query bookoutlet for each book on bookshelf -- check db first
    start = time.time()

    for book in bookshelf:
        print('looking for: {}'.format(book))
        results = bookoutlet.query_bookoutlet(book)

        print('{} match[es] found'.format(len(results)))
        print(results)

    end = time.time()
    print('run-time {} s'.format(end-start))
