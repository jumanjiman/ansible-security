#!/usr/bin/env python

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from optparse import OptionParser
import json
import os
import re


playbook_whitelist = {
	     	      '-v': False,
		      '-i': True,
		      '-M': True,
		      '-e': True,
		      '-f': True,
		      '-k': False,
		      '-K': False,
		      '-U': True,
		      '-T': True,
		      '-s': False,
		      '-u': True,
		      '-c': True,
		      '-l': True
		     }
		     

class RequestHandler(BaseHTTPRequestHandler):
        
    def alphafy(self, a_string):
	pattern = "[^a-z0-9_]"
	return re.sub(pattern, "_", a_string, flags=re.IGNORECASE)

    def do_POST(self):
        
        request_path = self.path
	# handle the play endpoint
       	if request_path == '/play':
	    request_headers = self.headers
            content_length = request_headers.getheaders('content-length')
            length = int(content_length[0]) if content_length else 0
 	    post_data = json.loads(self.rfile.read(length))
	    print post_data
	    playbook = post_data['playbook']
	    if not playbook:
	    	self.send_response(400, 'playbook not sent')
		return
	    if not playbook.endswith('.yml'):
	    	self.send_response(400, 'bad playbook extension')
		return
	    flags = post_data['flags']
	    print flags
	    for flag in flags:
	    	print flag
	    for flag in flags:
	    	if flag['flag'] not in playbook_whitelist.keys():
		    self.send_response(400, "invalid flag")
		    return
		if playbook_whitelist[flag['flag']] and not flag['argument']:
		    self.send_response(400, "provided argument to non argument flag")
		    print flag['argument']
		    return
	    directory = post_data['git_handle'] + '/' + post_data['branch_name']
	    safe_dir = self.alphafy(directory)
	    print safe_dir
	    print playbook
	    command = "ansible-playbook"
	    if flags:
	    	for flag in flags:
		    command += " {0}".format(flag['flag'])
		    if flag['argument']:
		    	command += " {0}".format(flag['argument'])
	    base_dir = os.environ['base_dir']
            command += " {0}/{1}/{2}".format(base_dir, safe_dir, playbook)
	    print command
	    # Use this to set ANSIBLE_HOSTS environmet variable as base_dir, safe_dir
	    # root is hosts
            os.putenv('ANSIBLE_HOSTS', "{0}/{1}/hosts".format(base_dir, safe_dir)
	    os.system(command)
	    self.send_response(200)
	    return
		    
	elif request_path == '/run':
	    return # not implemented yet, TODO
	    
	    

def main():
    port = 8080
    print('Listening on localhost:%s' % port)
    server = HTTPServer(('', port), RequestHandler)
    server.serve_forever()

        
if __name__ == "__main__":
    parser = OptionParser()
    parser.usage = ("Creates an http-server that will echo out any GET or POST parameters\n"
                    "Run:\n\n"
                    "   reflect")
    (options, args) = parser.parse_args()
    
    main()
