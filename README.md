## cli-project
cli project to query couchbase db

### Platforms tested and verified as working
 - **MacOS 12**
 - **Ubuntu 20.1 LTS**

### Python SDK Installation pre-requisites
_please see https://docs.couchbase.com/python-sdk/current/hello-world/start-using-sdk.html for details_
 - **MacOS**
   - brew update
   - brew install openssl

 - **Ubuntu 20.1 LTS**
   - python3 -m pip install --upgrade pip setuptools wheel
   - sudo apt-get install git-all python3-dev python3-pip python3-setuptools cmake build-essential
   - sudo apt-get install libssl-dev

### Simple Query Tool App Installation alogn with dependencies
   - git clone https://github.com/rsavalagi/cli-project.git
   - cd cli-project
   - pip3 install virtualenv
   - virtualenv --python=python3.7 venv 
   - source venv/bin/activate
   - sudo -H python3 -m pip install couchbase (macOs) or python3 -m pip install couchbase (ubuntu)
   - pip3 install --editable .

## creating a distribution
 - cd cli-project
 - source venv/bin/activate
 - pip install pyinstaller
 - pyinstaller qtool.py

### Using App
**inline configuration**

_(venv) % qtool configure -a 127.0.0.1:8091 -u username -p Admin123$_

_(venv) % qtool execute -q "SELECT * FROM \`travel-sample\` LIMIT 10" -u Administrator -p Admin123$_

**interactive configuration**

default values are displayed, Press Enter Key to assume default values.

_(venv) rsavalagi@MacBook-Pro-16 cli-project % qtool configure_

_cluster address or ip  [127.0.0.1:8091]:_

_username  [Administrator]:_

_password : Admin123$_






