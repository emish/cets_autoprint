#!/usr/bin/python
# autoprint.py

"""Automatically manage and print pdfs in a source directory
to CETS for free printing while abiding by the printing policy.
"""

import os, time, subprocess, datetime
from pyPdf import PdfFileWriter, PdfFileReader

# Are we debugging
debug = True

# Adjust these globals for eniac
home = os.getenv('HOME')
path_to_watch = home + "/to_print"
print_cmd = "mkdir "
#print_cmd = "lpr -P169 -o Duplex=DuplexNoTumble "
logfile = file(path_to_watch + "/autoprint.log", 'w')

# The number of pages we're willing to let slide beyond the 5 page limit'
leeway_pages = 0
real_leeway = leeway_pages * 2

# Look for a new file every _ seconds
time_poll = 20
# Seconds in a half-hour
half_hour = 1800

# Program invariant globals
file_queue = []

def log(s):
    """Log the string s with pretty date prepended.
    """
    now = datetime.datetime.now()
    print >> logfile, now.strftime("%Y-%m-%d %H:%M:%S :: "),
    print >> logfile, s
    logfile.flush()

def logdebug(s):
    """Log a debug message.
    """
    if not debug: return
    now = datetime.datetime.now()
    print >> logfile, now.strftime("%Y-%m-%d %H:%M:%S :: DEBUG : "),
    print >> logfile, s
    logfile.flush()

def split_file(f, filename):
    """Split our file into 10-page sub-files and add those to the queue
    in order.
    """
    global file_queue
    curr_page = 0
    pages_left = f.getNumPages()
    log('Splitting file ' + filename + " with " + str(pages_left) + " pages.")
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
    filename = path_to_watch + "/" + f
    # Non-pdfs are not supported
    if (filename[-4:] != ".pdf"):
        log("Not a valid PDF file.")
        return
    try:
        fp = file(filename, 'rb')
        pdf_f = PdfFileReader(fp)
    except IOError as e:
        log("ERROR: Unable to process file "+filename)
        log(str(e))
        return
    except e:
        log("ERROR: Unable to read PDF File")
        log(str(e))
        return

    if pdf_f.getNumPages() > (10 + real_leeway):
        split_file(pdf_f, filename)
    else:
        file_queue.append(filename)
    fp.close()

def main():
    global file_queue
    jobs_printed = False

    log("Started autoprint. Watching "+path_to_watch+" directory.")

    while True:
        # Update our files list
        last_check = os.listdir(path_to_watch)
        for f in last_check:
            if f == 'autoprint.log': continue
            fname = path_to_watch + '/' + f
            if fname not in file_queue:
                log("Processing file: "+f)
                process_file(f)

        # Release a print job if any
        if file_queue:
            log("Files queued to print = " + str(len(file_queue)))
            file_to_print = file_queue.pop(0)
            tmp_cmd = print_cmd + file_to_print
            log("Releasing print job for file: " + file_to_print)
            try:
                subprocess.check_output(tmp_cmd,
                                        stderr=subprocess.STDOUT,
                                        shell=True)
            except subprocess.CalledProcessError as e:
                log("ERROR: Can't print file.")
                log(e.output)
            # Wait 30 mins after a processed job
            jobs_printed = True
            # Get rid of file
            try:
                os.remove(file_to_print)
            except OSError:
                log("ERROR: Can't remove file "+file_to_print)

        # If we just printed, we wait 30 mins.
        if jobs_printed:
            sleep_time = half_hour
            jobs_printed = False
            log("Sleeping for half-hour")
        # Don't sleep if job waiting and we are not waiting for printer'
        elif file_queue:
            sleep_time = 0
            log("Job forward to print.")
        # Sleep time-poll if no new updates
        else:
            sleep_time = time_poll

        # Sleep until we can print again.
        time.sleep(sleep_time)

if __name__ == '__main__':
    main()
