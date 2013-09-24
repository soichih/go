#!/usr/bin/python
import curses, os, traceback, copy

#load paths
pathfile = os.environ["GO_PATH_FILE"] 
paths = []
if os.path.exists(pathfile):
    f = open(pathfile, "r")
    for line in f:
        paths.append(line.strip())
    f.close()
else:
    #set to default (wherever..)
    paths = [ "/home", "/etc" ]


paths.sort()
paths_original = copy.deepcopy(paths)

def search(array, item):
    for i in range(0, len(array)):
        if array[i] == item:
            return i
    return -1

def redraw(stdsrc, scrollpos):
    stdscr.clear()
    #highlight current selection
    for i in range(scrollpos, len(paths)):
        #don't draw past the height
        if i >= stdscr.getmaxyx()[0] + scrollpos:
           break 
        path = paths[i]
        stdscr.addstr(i - scrollpos, 0, path)

def main(stdscr):
    scrollpos = 0

    # pick the last selected path (not the closeat match, because path maybe
    #aliased or linked
    last_path_env = "LAST_GO_PATH_INDEX"
    current = 0
    if os.environ.has_key(last_path_env):
        current = int(os.environ[last_path_env])
    if len(paths) <= current:
        current = len(paths)-1

    previous = -1
    redraw(stdscr, scrollpos)

    while 1:
        #update highlight
        if previous != -1 and previous - scrollpos < stdscr.getmaxyx()[0] and previous < len(paths):
            stdscr.addstr(previous - scrollpos, 0, paths[previous])
        #don't highlight past window size
        if current - scrollpos >= stdscr.getmaxyx()[0]:
            scrollpos = scrollpos + 1
            redraw(stdscr, scrollpos)
        if current - scrollpos < 0:
            scrollpos = scrollpos - 1
            redraw(stdscr, scrollpos)

        try:
            stdscr.addstr(current - scrollpos, 0, paths[current], curses.A_REVERSE)
            previous = current
        except:
            print "can't find ",current

        stdscr.refresh()
        
        c = stdscr.getch()
        if c == ord('q'):
            break
        elif c == curses.KEY_LEFT or c == ord('h'): 
            #shrink path
            sel = paths[current].split("/")
            if len(sel) > 1:
                newpath = "/".join(sel[0:-1])
            if newpath == "":
                newpath = "/";
	    paths[current] = newpath
            redraw(stdscr, scrollpos)
        elif c == curses.KEY_RIGHT or c == ord('l'): 
            #expand path
            added = False
            insertpos = current + 1
            for d in os.listdir(paths[current]):
                if paths[current] == "/":
                    newpath = "/" + d
		else: 
		    newpath = paths[current]+"/"+d
                if os.path.isdir(newpath):
                    if search(paths, newpath) == -1:
                        paths.insert(insertpos, newpath)
                        insertpos = insertpos + 1
                        added = True
            if added:
                paths.sort()
                current = current + 1
                redraw(stdscr, scrollpos)
            continue
        elif c == curses.KEY_UP or c == ord('k'): 
            if current > 0: 
                current = current - 1
        elif c == curses.KEY_DOWN or c == ord('j'): 
            if current < len(paths)-1: 
                current = current + 1
        elif c == curses.KEY_DC or c == ord('d'): 
            #remove it from original (if exists)
            s = search(paths_original, paths[current])
            if s != -1:
                paths_original.pop(s)

            #delete current path
            paths.pop(current)
            if current == len(paths):
                current = current - 1
            #if none exist, list root
            if len(paths) == 0:
                paths.append("/home")
            redraw(stdscr, scrollpos)
        elif c == curses.KEY_ENTER or c == 10: 
            sel = paths[current]
            #search for selected path in the original path
            if search(paths_original, sel) == -1:
                #if not found, add it to original path
                paths_original.append(sel)

            #store the location and exit
            path = os.environ["GO_SHELL_SCRIPT"] 
            f = open(path, "w")
            f.write("cd "+sel+"\nexport "+last_path_env+"="+str(current)+"\nrm -f " + path)
            f.close()
            break

    #store the original path
    f = open(pathfile, "w")
    for i in paths_original:
        f.write(i+"\n")
    f.close()
if __name__=='__main__':
    try:
    # Initialize curses
          stdscr=curses.initscr()
    # Turn off echoing of keys, and enter cbreak mode,
    # where no buffering is performed on keyboard input
          curses.noecho()
          curses.cbreak()
          curses.curs_set(0)
    # In keypad mode, escape sequences for special keys
    # (like the cursor keys) will be interpreted and
    # a special value like curses.KEY_LEFT will be returned
          stdscr.keypad(1)

          main(stdscr)# Enter the main loop
    # Set everything back to normal
          stdscr.keypad(0)
          curses.echo()
          curses.nocbreak()
          curses.curs_set(1)
          curses.endwin()# Terminate curses
    except:
    # In event of error, restore terminal to sane state.
          stdscr.keypad(0)
          curses.echo()
          curses.nocbreak()
          curses.endwin()
          traceback.print_exc()# Print the exception


