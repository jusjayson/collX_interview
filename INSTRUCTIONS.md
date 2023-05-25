# collX_interview
CollX Takehome Project
Background
One of the biggest challenges we have at CollX is reliably mapping pricing data from third-party sources like
eBay to canonical card records in our database.
Currently we’re able to map some percentage of sales using visual search. We run the photo from the eBay
listing through our visual search engine and try to find a match. This works reasonably well, but it requires that
we have an image for the card in the first place. In our database of about 14M cards we only have images for
about 3.5M. Visual search also leads to a large number of false positives because many cards have “parallels”
that are the same photo for different trim/frame.
Currently we map 10-20% of the sales we capture on eBay using visual search. We’d like to map a much
larger percentage of these sales by somehow mapping the text in the eBay listings to records in our database.
This can be achieved using some combination of rules-based logic and fuzzy text matching.
The purpose of this project is to explore some possible solutions to this problem.

The Data
Here’s a dump of the cards, teams, players, and sets tables from our MySQL database:
https://prop.to/rq7zeFps0A
The schema should be pretty self explanatory but let me know if you have any questions.
You can get the image for any card (if we have one) using the convention:
https://storage.googleapis.com/collx-media/{CARD_ID}-front.jpg
For example:

https://storage.googleapis.com/collx-media/421635-front.jpg
has_front_image in the cards table will be true when we have an image.
And this is a bunch of processed eBay sales data that’s already been run through our vision matching:

https://prop.to/qGwlHYDVOF
These are individual JSON files that correspond to a single scrape. Each scrape is for one particular sport.
If there’s a card_id it means we were able to map it to a card using vision. If card_id is null, there was no vision
match.
When there is a card_id, it does not necessarily mean it is correct. It could be a different version of the card, it
could be an image that has the card as part of a lot, or it could be a visually similar card from the same set.
Your Task
What we’d like you to do is figure out a way to reliably map the sales that we weren’t able to map already.
Based on the information scraped from the eBay listing your code should figure out the most likely set and card
for that listing. It won’t be possible to map all of them reliably, but the goal is to reliably map more than what we
are currently doing.
Deliverables & Submission Instructions
As a deliverable, please provide the following
1. Any and all code used to produce your results.
2. A summary document that describes
a. Your approach to matching.
b. Why you selected this approach, and if there were others that you considered.
c. The match rate your approach achieved. Please estimate the false positive rate you expect from
your results, and how that number was computed.
d. What your next steps would be if you were to continue working on this.
e. A high-level summary of the code (1).

We expect this project to take about 4 hours of focused effort. Please submit the deliverables (as a zipped file
saved as "collx_takehome_your_name.zip") within one week of being sent the project. If for whatever reason
you do not expect to finish on time, please communicate this as early as possible.
We look forward to reviewing your submission!