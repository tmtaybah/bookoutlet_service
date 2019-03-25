import time
import csv
from multiprocessing import Pool

# custom modules?
import goodreads
import bookoutlet
from flask import app


# create csv file and write book data into it
def writeCSV(member_id, data):

    # path = '/Users/tara/Developer/projects/goodreads_bookoutlet/matches'
    filename = 'matches/matches_member' + member_id + '.csv'
    print('file created: ', filename)
    # file = os.path.join(path+filename)
    f = open(filename, 'w')
    writer = csv.writer(f, dialect='excel')

    headers = ['Title', 'Author', 'Price', 'Edition', 'Scratch and Dent?']
    writer.writerow(headers)

    writer.writerows(data)

    f.close()


def main():

    # create worker pool to speed up querying
    num_workers = 30
    pool = Pool(num_workers)

    # get member from user input
    member_input = input('which member? ').strip().lower()

    member_ids = {'emma': '32879029', 'tara': '25083955', 'regan': '19645927',
                  'miranda_readsmi': '71848701', 'julie': '5210022',
                  'dianeS': '4159922', 'hannah': '38077205',
                  'emilymay': '4622890', 'ghada': '15349216'}

    if member_input in member_ids:
        member_id = member_ids[member_input]
    else:
        print('Error: member not found ')
        exit()

    # get a member's to-read shelf
    toReads = goodreads.getToReadShelf(member_id)

    start = time.time()
    results = pool.map(bookoutlet.queryBookOutlet, toReads)
    end = time.time()
    print('run-time {} s'.format(end-start))

    # prepare data into form that can be written into csv file
    matches = [book for result in results for book in result]
    writeCSV(member_id, matches)


if __name__ == '__main__':
