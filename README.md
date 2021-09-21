# Spotlight On The Credits

The goal of this project is to give more credit to the artists behind songs. They are producers, songwriters, composers, topliners and many others. However, usually only the interpreters are credited. So, I decided to work on a way to contribute to give more recognition to **all the artists**.

## What is **Spotlight On The Credits** exactly?

At the moment, it is a series of playlists regrouping all the songs to which an artist has contributed to. So far, the playlist are only available on [Spotify](https://open.spotify.com/user/ik27dsazkx8qtbdp9o03227at/playlists). The playlists are generated, and updated every Friday, automatically using the [Genius API](https://genius.com/) and the [Spotify API](https://developer.spotify.com/documentation/web-api/). The information on the artists that worked on a song is taken from Genius databases. Genius is a collaborative website in which people can suggest meaning of lyrics and metadata on the songs. such as who contributed to a song. The information might be incorrect but it is possible to suggest a correction on the website and then this will be corrected in the API and thus, in my playlists.  

I also made a [Twitter bot](https://twitter.com/SpotCredits) which uses the [Twitter API](https://developer.twitter.com/en/docs) to look for Tweets requesting for a specific playlist.  

Finally, on my server side, I use Python scripts to handle all of this and a MongoDB database to store data on each playlist generated and to avoid making redundant requests.

## How to use the Twitter "user interface"?

* **When to use it ?** You can use it if you want to get a playlist that as not been made or if you're not sure if a playlist has been made.
* **How to use it ?** To use it you have to tweet at my bot (using **@SpotCredits**) and use the following synthax :  
![alt text](https://github.com/rpic84/spotcreds/blob/main/images/synthax.png "synthax.png")

For example, if you want to check if there is a playlist for the Belgian artist, [**Le Motif**](https://genius.com/artists/Le-motif), you can tweet one of the following :
* in English : "@SpotCredits Do you have a playlist with Le Motif please?"
* in French : "@SpotCredits Est-ce que tu as une playlist avec Le Motif stp?"

## Presentation of the code

* *[genius.py](genius.py)* : functions related to the Genius API. There are basic functions such as ones to search the Genius database or one to *get* items through the Genius API. There are also more complex ones parsing data at the *.json* format to get all the artists behind a song and their contribution.

* *[spotify.py](spotify.py)* : similarly, to what has been done for the Genius API in **genius.py**, this file is composed of a lot of functions to make requests to the Spotify API database. Moreover, there is a function that makes an image for which I have the rights for any playlist using [Pillow](https://pillow.readthedocs.io/en/stable/) and [opencv](https://docs.opencv.org/4.5.2/d6/d00/tutorial_py_root.html). The main element of this file is a class used to login to the Spotify account handling all the playlist and the access to the Spotify API, this was the most complex piece of code that I made for this project.

* *[twitter.py](twitter.py)* : functions to encapsulate code used to work with the Twitter API.

* *[logs.py](log.py)* : a function to create a new folder for logs if needed and a class to send an e-mail if an error occurs.

* *[custom_collections.py](custom_collections.py)* : classes to ensure the cojherence of the structure inside the *songs* and *artist_playlist* collections of the MongoDB database.

* *[check_tweets.py](check_tweets.py)* : the function that check if there are tweet requests and that create a playlist or links to an existing playlist depending on the request result.

* *[weekly_update.py](weekly_update.py)* : updating the database and the playlists. This update starts by looking for the songs that were not found on Spotify.After that it updates the popularity of each song in the database. The popularity is a score given through the Spotify API and it is used to sort the songs in each playlist by decreasing popularity. Then, this script updates the songs related to each artist already in the database by looking for new songs. Finally, the splaylists are updated on Spotify.  

The project uses a few configuration files that include access keys to the APIs and credentials for the other accounts used.


## Contributing

You can contribute to the project via GitHub directly if you want to code or contact me on Twitter [@SpotCredits](https://twitter.com/SpotCredits).

## Nota Bene

Spotify seems to be trying to develop more ressources for the artists behind songs. They started to able **songwriters** to create webpages for their work and to help producers and publishers through some kind of hub. Click [here](https://noteable.spotify.com/) for more information.

## Sources

* Spotify API : [CodingEntrepreneurs](https://www.youtube.com/watch?v=xdq6Gz33khQ) and [documentation](https://developer.spotify.com/documentation/web-api/reference/)
* Genius API : [official documentation](https://docs.genius.com/)
* Twitter API : [Code Wizard](https://www.youtube.com/watch?v=ewq-91-e2fw)
* Set up MongoDB on Linux server : [Code With Nate](https://www.youtube.com/watch?v=Ir68GVsNWB4)
* Logs : [Corey Schafer](https://www.youtube.com/watch?v=jxmzY9soFXg)
* For all the issues I encountered : [Stack Overflow](https://stackoverflow.com/)

## License & Copyright
© Romain Pic - 2021

Licensed under the [GNU GPLv3](LICENSE)
