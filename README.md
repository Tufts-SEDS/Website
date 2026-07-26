
# Tufts SEDS Website

This repository contains the source code for the official Tufts SEDS website. Below are instructions to help you set up your local environment.

[Link to the original repository](https://github.com/bimmui/tufts-SEDS) (it is private but Claire and Will have access)

### Python Environment Setup
Before doing anything, install the following:
- [Git](https://git-scm.com/downloads)
- [Conda](https://docs.conda.io/en/latest/) or [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/)

```bash
# 1. Clone the Repository using either Github Desktop (recommended), via command line, or just by downloading the repo

# 2. Create Conda Environment
conda env create -f sedsite.yml -n sedsite

# 3. Activate the Conda Environment
conda activate sedsite

# 4. Verify Installation
conda list
```

### Running Django locally
Ensure that you're in the directory where the `manage.py` is located. From there, all you need to do is run `python manage.py runserver`

### Editing the Source Code
Assuming you've made another branch, you're pretty much free to do whatever you want on your local copy of the code! A few things to note however:
- There are two Postgres databases that we have up on our server. One is for production: which is used on what you see in [sedstufts.org](sedstufts.org). The other database is another Postgres db, but that is used primarily for testing. If you navigate to `tuftsseds\tuftsseds_core\settings.py`, you'll notice there are different settings based on the value of `DEBUG`. Whenever you're testing things out, ALWAY KEEP `DEBUG = True`. Otherwise, you'll switch to the production database and might mistakingly mess with things there. Luckily, there's a handful of checks and balances I implemented to prevent bad stuff from happening if you do happen to switch the settings, but I'd advise against messing with the settings for the most part.
- When it comes to working with the databases, the data to populate them comes from spreadsheets. Check out the Google Drive of tuftssedspics@gmail.com and you'll notice there are "Master Lists", each of which correspond with an app in `tuftsseds\siteapps`. These populate the database based on the models they emulate. Take a look inside the `models.py` for a couple of apps and you should be able to connect the dots from there. The specific way we go about getting this data in the database is by uploading the spreadsheet (as a csv) to the admin portal.
- Do not hesitate to consult Claire if need help with anything or you're deathly afraid of making some irreparable mistake!
