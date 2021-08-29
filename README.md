# Spotlight On The Credits

The goal of this project is to give more credit to the artists behind songs. They are producers, songwriters, composers, topliners and many others. However, usually only the interpreters are credited. So, I decided to work on a way to contribute to give more recognition to **all the artists**.

## What is **Spotlight On The Credits** exactly?

At the moment, it is a series of playlists regrouping all the songs to which an artist has contributed to. So far, the playlist are only available on [Spotify](https://open.spotify.com/user/ik27dsazkx8qtbdp9o03227at/playlists). The playlists are generated, and updated every Friday, automatically using the [Genius API](https://genius.com/) and the [Spotify API](https://developer.spotify.com/documentation/web-api/). The information on the artists that worked on a song is taken from Genius databases. Genius is a collaborative website in which people can suggest meaning of lyrics and metadata on the songs. such as who contributed to a song. The information might be incorrect but it is possible to suggest a correction on the website and then this will be corrected in the API and thus, in my playlists.  

I also made a [Twitter bot](https://twitter.com/SpotCredits) which uses the [Twitter API](https://developer.twitter.com/en/docs) to look for Tweets requesting for a specific playlist.  

Finally, on my server side, I use Python scripts to handle all of this and a MongoDB database to store data on each playlist generated and to avoid making redundant requests.

## How to use the Twitter "user interface"?

* **When to use it ?** You can use it if you want to get a playlist that as not been made or if you're not sure if a playlist has been made.
* **How to use it ?** To use it you have to tweet at my bot (using **@SpotCredits**) and use the following synthax :  
![alt text](https://github.com/rpic84/spotcreds/images/synthax.png "synthax.png")

For example, if you want to check if there is a playlist for the Belgian artist, [**Le Motif**](https://genius.com/artists/Le-motif), you can tweet one of the following :
* in English : "@SpotCredits Do you have a playlist with Le Motif please?"
* in French : "@SpotCredits Est-ce que tu as une playlist avec Le Motif stp?"

## Presentation of the code

* *genius.py* : 
* *spotify.py* : 
* *twitter.py* : 
* *logs.py* :
* *custom_collections.py* : 

* *check_tweets.py* : 
* *weekly_update.py* :


## Contributing

You can contribute to the project via GitHub directly if you want to code or contact me on Twitter [@SpotCredits](https://twitter.com/SpotCredits).

## Sources

* Spotify API : [CodingEntrepreneurs](https://www.youtube.com/watch?v=xdq6Gz33khQ) and [documentation](https://developer.spotify.com/documentation/web-api/reference/)
* Genius API : [official documentation](https://docs.genius.com/)
* Twitter API : [Code Wizard](https://www.youtube.com/watch?v=ewq-91-e2fw)
* Set up MongoDB on Linux server : [Code With Nate](https://www.youtube.com/watch?v=Ir68GVsNWB4)
* For all the issues I encountered : [Stack Overflow](https://stackoverflow.com/)
