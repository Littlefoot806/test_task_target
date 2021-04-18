# test_task_target

## Install and activate virtual environment
```sh
# Create virtual environment
virtualenv venv
# Activate virtualenv
source venv/bin/activate
```

Change working folder and install dependencies
```sh
cd test_task
pip install -r requirements.txt
```

## Run

Run spider by explicitly specifying url to product (`ex: https://www.target.com/p/standish-3pc-patio-bar-height-dining-set-charcoal-project-62-8482/-/A-53957008#lnk=sametab`)
```sh
scrapy crawl target -a url="<url>"
```
