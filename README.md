# collX_interview
CollX Takehome Project

# TLDR
I wrote a matching algorithm combining regex, fuzzy matching, and database queries as an alternative to the described computer vision approach. The main pro of the algorithm is its low false-positive rate. The cons include slowness and a low match rate. I include both low-hanging and longer term suggestions for improving this code, as well as numerous tests that can be used for replication, comprehension, and collaboration. Further, I utilized docker for system agnostic (as long as that system is some variant of Linux) installation of the code, and have included instuctions for installation with and w/out Docker below.

# Running code

## Running tests

### Using docker
After following the instructions in "Building the test environment" below, you can run all unit and integration tests from the root directory with 
```
make run-tests
```

This will create a docker container, install the collx package, and use pytest to run all unit tests.

### Outside of docker
From the project root directory (after following the instructions in the Installing Outside of Docker section), run
```
pytest
```

## Confirming accuracy of my solution
In order to assess the accuracy of my matching algorithm, I wrote code to match cards that already have a provided matching id in their ebay data.

### Using docker
After following the instructions in "Building the local environment, from the project root, run
```
make test-matching-accuracy
```

### Outside of docker
After following the instuctions in "Installing outside of docker", from the project root
```
python test.py test_accuracy
```

## Matching cards
### Using docker
After following the instructions in "Building the local environment, from the project root, run
```
make match-cards
```

### Outside of docker
After following the instuctions in "Installing outside of docker", from the project root

```
python test.py match_cards
```


# Design
## Approach
Given the choice to balance accuracy and speed, I prioritized accuracy. What I mean by this is that I had a pre-existing source of truth (the db) to test any inferences about the correctness of a player or set name in a listing's title. Prioritizing this source of truth meant executing at least one query whenever an assertion about the title needed validation, which is much slower than simply using regex to make more broad assertions about which parts of the title identified a player vs a set.

## Process

1. Parse titles using regex and the database

In order to figure out the card's year, player, and set from the title, I utilized regex to identify possible years, player names, and set names, queried the database for similar matches, and used thefuzz (package) to get the best match (if any).

2. Use parsed info to accurately find cards in db

After achieving some confidence (using the database) about the various parts of the title, I then queried the database for a card matching the already obtained set, player, and year.

## Constraints

### A match is considered valid only if there is some confidence in the set, player, and year.
Before writing any code, I mapped out the database, picking attributes I thought could best be used to confidently match a card. Noticing a player may have many cards in one year, I decided set, player, and year would serve as sufficient uniqueness-constraints when querying for a card match (at least for an MVP).


# Limitations
## Something is likely wrong with the code applying my algorithm.

There is a large disconnect between the match rate for ebay items containing a card_id and ebay items that do not. Given that I unit tested my code and am confident in the accuracy (%30) of the first case, I would (if given more time) investigate why the match rate for much ebay items not containing a card_id is dramatically lower.

## Order may yield an incorrect year
Given the limited range of card years (between the 1900s and 2023), I decided a good balance of efficiency and accuracy would be to match the first year-like string in the title, and use it if it was somewhere between 1900 and 3000. This may lead to false positives.

## Set accuracy is not guaranteed
While I use the database to validate what in the title is a set name, some sets have very similar names. While the listing title "2023 panini instant limited black refractions {player_number} {player name}" should confidently match the right set if it exists in the database, it may also match "2022 panini instant blue refractions", resulting in false positives.

# Alternative approaches
While I tried to keep false positives at a minimum by relying on the database and multiple unique constraints, this results in query heavy code with a low match rate. Upon reflection, I considered the following alternatives.

## More ML?
If I had the time and resources (to utilize a relevant package), I'd love to utilze an ML model capable of identifying sports players and sets as a better means of parsing this data from the given title.

## Omit set from constraints?
I have confidence (based on deciding to include the set name as a constraint) that removing the set name as a constraint would significantly increase both the match and false positive rate. This "close-enough" result is likely more preferabl if the core issue is needing more card-matches in general, and if there is a willingness to make a post-processing solution for correcting this "close-enough data".


# Performance

## Accuracy rate for items with card_ids (see test_results.txt)
I achieved an accuracy rate of about 35% on the selection of ebay items having card_ids (for the 4 files in which greater than 500 provided card ids were found in the provided database)

### Caveat: Prioritizing pre-existing data
Of significant note, my algorithm makes use of provided data in an ebay item (i.e., player name, set name, year) over parsing the title. If this optimization were removed, results may vary.

## False positive estimate: 10%
As described above, companies with very similarly named sets are likely be mismatched if one exists in the database and the other does not. Assuming this is not the case, and that some sets simply mismatch due to mispelling in the listing, I make a still conservative estimate that 10 out of 100 cards will have mispelled set names and be mismatched as a result.

## Actual match rate  (see test results.txt)
As described above, I have an unexpectedly low match rate of 2%. Given that my match rate is 30% for cards that have a card_id, and that I am not utilizing a different flow of code, and that such items may also include the same identifiers (set, name, year) I prioritize over title parsing, I'm assuming there's something wrong with the declarative logic in the main function running the full match. The data, at a glance, doesn't seem different enough between the two categories (matched vs un-matched) to justify such a huge difference.

# If given more time
If given more time to work on this, I'd immediately do the following.

## Collaborate
This is an early solution, and actually more than what I'd usually do before showing other people my thoughts. I default to test-driven development, and wrote unit tests (after modeling my ideas) before writing any of the code in src/collx. I'd prefer to share these tests with the other developers on my team before writing too much clean code in order to consider alternatives and optimizations before spending multiple hours writing making something "good".

## Improve speeds
Keeping my current solution, it would make sense to check items concurrently and distribute the database to account for the large number of queries we're doing. Financially, this could be done initially in bursts, and then scaled down with the expectation that new sales of trading cards will not occur quickly enough to require extensive database distribution.

## Why the inaccuracy
Identify why the results are so much more accuracte when we have match_ids vs when we don't, given the similarity of the data.

## Cache known sets and players for parsing
Conducting so many db queries to validate set and player in the title is expensive. It took over an hour to run my code on a single core of a 12th gen i5 processor, and I've included a test_results.txt file to spare my reviewers the pain of needing to execute all of this themselves. Given the limited number of sports sets and reasonable number of players, preloading a cache would be a much faster first option for validating parts of the title.

### Cache previous results
Given the limited amount of players and sets, caching previous results is a low hanging fruit for avoid many db hits.

# Instructions for deployment
## Installing the code
For flexibility and to avoid package conflicts, I built this code for containerization via docker. I've already written a package called Python-Docker for building Python based containers with Poetry (package manager), and included that in order to generate environments for writing/testing the code and easily accessing the webserver. Given its usage of docker buildkit, this deployment flow is intended to be built on linux. If this is problematic, please skip to the sections concerning running the code outside of docker.

## Building the base image
In order to build the image (test) used for running tests, confirming accuracy of my solution, and matching unmatching cards, we first build a base Python image with the Poetry package manager. To do so, from the root directory, run
```
make build-base-image
```

## Building the testing environment
After building the base image, from the project root, run
```
make build-test-project && make load-db
```
NOTE: Before running, make sure to populate a data directory in the project root as follows:
{root}/data/ebay_sales
{root}/data/collx_card_data.sql

This sets up the "collx" project and accompanying mysql-db, configures logging, mounts the relevant code, and binds the correct entrypoint script.

## Installing outside of docker
While I recommend running the project in docker to ensure you have the most similar environment as the one I spent most of my time in, this is not required. In order to do so, one must install the following:
- Python 3.8+ (https://www.python.org), given the use of the walrus operator in the code base. On a modern Ubuntu distrubution:
```
sudo apt install python3.10 python3.10-venv
```

- Poetry Poetry (https://python-poetry.org): This is most easily installed using
```
pip install poetry
```
Note: If installing outside of docker, I recommend install poetry within a virtual environment. To do so on a modern Ubuntu distribution,
```
mkdir -p ~/.virtualenvs;
python3.10 -m venv ~/.virtualenvs/taxer;
source ~/.virtualenvs/taxer/bin/activate
```

After installing the above requirements, from the project root directory, run
```
poetry install
```

A populated mysql database is also required. Instructions for settings one up are available via (https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/).

Once configured, create a new database, load the necessary sql dump, and record the database name, user, host, port, and password. This information must be substituted into the get_engine command of
```src/collx/db.py```.

#### Tearing down containers
In order to teardown any lingering containers, simply run (from the project root)
```
make teardown-test-project
```