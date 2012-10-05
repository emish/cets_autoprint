#!/opt/local/bin/python

import os, time, subprocess
from pyPdf import PdfFileWriter, PdfFileReader

d = True

# Adjust these globals for eniac
#path_to_watch = "/home1/e/emish/to_print"
#print_cmd = "lpr -P169 -o Duplex=DuplexNoTumble "
path_to_watch = "/Users/emish/Projects/autoprint/to_print"
print_cmd = "ls "

# The number of pages we're willing to let slide beyond the 5 page limit'
leeway_pages = 0
real_leeway = leeway_pages * 2
# Look for a new file every 10 seconds
time_poll = 10

# Program invariant globals
file_queue = []

def split_file(f, filename):
    """Split our file into 10-page sub-files and add those to the queue
    in order.
    Input is pdf obj
    Output is pdf obj 2-tuple
    """
    print 'splitting file ' + filename
    global file_queue
    curr_page = 0
    pages_left = f.getNumPages()
    while pages_left > 0:
        # Create the new file
        pages_processed = 0
        fname = filename[:-4] + '_' + str(curr_page) + '.pdf'
        output = PdfFileWriter()
        # Get 10 pages for it
        for i in range(curr_page, 10+curr_page):
            if pages_processed >= pages_left:
                break
            pages_processed += 1
            output.addPage(f.getPage(i))
        # Write and save file
        fout = file(fname, 'wb')
        output.write(fout)
        fout.flush()
        fout.close()
        file_queue.append(fname)
        curr_page += pages_processed
        pages_left -= pages_processed
    # Delete the file now that it's in pieces'
    os.remove(filename)

def process_file(f):
    """Splits the file into parts if necessary,
    then adds it to the global queue.
    """
    global file_queue
    print "Processing file: " + str(f)
    filename = path_to_watch + "/" + f
    # Non-pdfs are not supported
    if (filename[-4:] != ".pdf"):
        return
    fp = file(filename, 'rb')
    pdf_f = PdfFileReader(fp)
    if pdf_f.getNumPages() > (10 + real_leeway):
        split_file(pdf_f, filename)
    else:
        file_queue.append(filename)
    fp.close()

def main():
    global file_queue
    jobs_waiting = False
    first = True

    while True:
        # Release a print job if any
        print "Files to print = " + str(len(file_queue))
        print file_queue
        if file_queue:
            file_to_print = file_queue.pop(0)
            tmp_cmd = print_cmd + file_to_print
            print 'printing file ' + file_to_print
            subprocess.call(tmp_cmd, shell=True)
            # If more jobs, wait 30 minutes for sure.
            if file_queue:
                jobs_waiting = True
            # Get rid of file
            os.remove(file_to_print)
        else: jobs_waiting = False

        # Update our files list
        last_check = os.listdir(path_to_watch)
        for f in last_check:
            fname = path_to_watch + '/' + f
            if fname not in file_queue:
                process_file(f)

        # If we just printed, we wait 30 mins, otherwise keep
        # polling for new files
        sleep_time = 5 if jobs_waiting else time_poll

        # Sleep until we can print again.
        if not first:
            time.sleep(sleep_time)
        else:
            first = False

if __name__ == '__main__':
    main()
