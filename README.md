# robot-testrail
A python script for parsing robot test result and update the test result of TestRail

In robot-framework test case, you have to add CID:n in the Tags field where the n is the CID in testrail.

Example:
The max query count is 100
    [Documentation]    This test case is ....
    [Tags]    CID:1

# Requirement
https://github.com/gurock/testrail-api/tree/master/python/2.x

# Usage
python robot-testrail.py --folder=./UAT --pid=PROJECT_ID --user=USER --pwd=PWD --testrail=https://YOUR_IP/testrail
python robot-testrail.py --pid=16 --suiteid=33 --run="test run 1234"--user=USER --pwd=PWD --testrail=https://YOUR.testrail.com
