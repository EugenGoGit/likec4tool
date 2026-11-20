#!/usr/bin/env python3
with open('diagrams/instagram-service.c4', 'rb') as f:
    content = f.read()
    # Find the first occurrence of unescaped triple quotes
    idx = content.find(b"'''")
    if idx >= 0:
        print('Found unescaped triple quote at:', idx)
        print(repr(content[idx-20:idx+20]))
    else:
        print('No unescaped triple quotes found')
        # Check for escaped
        idx2 = content.find(b"\\'\\'\\'")
        if idx2 >= 0:
            print('Found escaped triple quote at:', idx2)
            print(repr(content[idx2-20:idx2+20]))
