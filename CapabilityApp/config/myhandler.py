### myhandler.py

# A global variable, cached between requests on this web server.
counter = 0

def main():
    global counter
    counter += 1
    print "Content-Type: text/plain"
    print ""
    print "My number: " + str(counter)

if __name__ == "__main__":
    main()
