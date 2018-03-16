from testrail import *
from pprint import *
import sys
import codecs
import getopt
import xml.dom.minidom
import ssl
import os
import fnmatch
import datetime


def parse_uat_result(filename):
    cidstatus = {}
    xmldoc = xml.dom.minidom.parse(filename)
    testlist = xmldoc.getElementsByTagName('test')
    for test in testlist:
        tags = test.getElementsByTagName('tag')
        for tag in tags:
            cid_str = tag.firstChild.nodeValue
            if cid_str[:4] == "CID:":
                cid = cid_str[4:]
                status = test.getElementsByTagName('status')
                msg = test.getElementsByTagName(
                    'msg')[-1].firstChild.data.encode('utf-8')
                state = '1' if status[-1].attributes['status'].value == "PASS" else '5'
                start = datetime.datetime.strptime(
                    status[-1].attributes['starttime'].value, "%Y%m%d %H:%M:%S.%f")
                end = datetime.datetime.strptime(
                    status[-1].attributes['endtime'].value, "%Y%m%d %H:%M:%S.%f")
                duration = int((end - start).total_seconds())
                element = {'status': state, 'comment': msg if state ==
                           '5' else 'PASSED', 'time': str(duration)+'s'}
                cidstatus[cid] = element

    return cidstatus


def main():
    UTF8Writer = codecs.getwriter('utf8')
    sys.stdout = UTF8Writer(sys.stdout)
    ssl._create_default_https_context = ssl._create_unverified_context
    resultxml = "output.xml"
    projectid = 0
    user = "qateam@7peakssoftware.com"
    pwd = ""
    folder = "output"
    suite_id = 33
    run_name = "Automated test run"
    testrail_url = "https://7peakssoftware.testrail.com"
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", [
                                   "pid=", "suiteid=", "folder=", "user=", "pwd=", "testrail=", "run=", "resultxml="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)  # will print something like "option -a not recognized"
        sys.exit(2)
    for o, a in opts:
        if o == "--folder":
            folder = a
        elif o == "--pid":
            projectid = a
        elif o == "--suiteid":
            suite_id = a
        elif o == "--user":
            user = a
        elif o == "--pwd":
            pwd = a
        elif o == "--testrail":
            testrail_url = a
        elif o == "--resultxml":
            resultxml = a
        elif o == "--run":
            run_name = a
        else:
            assert False, "Unknown option" + o

    print "User:" + user
    print "Project ID:" + str(projectid)
    print "TestRail URL:" + testrail_url
    print "Suite ID:" + str(suite_id)
    print "Run:" + str(run_name)
    print "Folder:" + str(folder)
    print "Result file:" + str(resultxml)

    client = APIClient(testrail_url)
    client.user = user
    client.password = pwd

    run = client.send_post('add_run/' + str(projectid),
                           {"suite_id": suite_id, "name": run_name, "assignedto_id": 1, "include_all": "1", "description": "Automated test-run initiated by :"+run_name})

    for root, dirs, files in os.walk(folder):
        for file in files:
            if not fnmatch.fnmatch(file, '*'+resultxml):
                continue
            print(file)
            cidstatus = parse_uat_result(os.path.join(folder, file))
            for cid in iter(cidstatus):
                print "Updating test result for case:" + str(cid)
                resp = client.send_post('add_result_for_case/' + str(run['id']) + '/' + str(cid), {
                                        "status_id": cidstatus[cid]['status'], "comment": cidstatus[cid]['comment'], "elapsed": cidstatus[cid]['time'], "version": run_name})

        # pprint(resp)
    print "Done!"


main()
