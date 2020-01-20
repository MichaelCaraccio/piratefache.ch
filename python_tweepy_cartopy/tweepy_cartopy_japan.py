__author__ = 'michaelcaraccio'

import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import matplotlib.pyplot as plt
import tweepy

from authentication import authentication  # Consumer and access token/key


class TwitterStreamListener(tweepy.StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """

    def __init__(self):
        super().__init__()
        self.tweet_counter = 0
        self.text_position = self.get_axis_limits(ax)
        self.tweet_counter_text = ax.text(self.text_position[0],                    # x position
                                          self.text_position[1],                    # y position
                                          "Tweets : " + str(self.tweet_counter),    # text
                                          fontsize=9,                               # fontsize
                                          ha="center", va="center",                 # position of text in the box
                                          color=(0.30, 0.34, 0.42),                 # textcolor
                                          bbox=dict(                                # fancybox
                                              boxstyle="square,pad=0.3",            # square with padding
                                              ec=(0.85, 0.87, 0.91),                # inner color
                                              fc=(0.93, 0.94, 0.96)                 # border color
                                          ))

    def on_status(self, status):
        if status.coordinates is not None:  # we only care about tweets with coordinates
            self.tweet_counter += 1
            self.tweet_counter_text.set_text("Tweets : " + str(self.tweet_counter))
            self.get_tweet(status)

    def on_error(self, status_code):
        if status_code == 403:
            print("The request is understood, but it has been refused or access is not allowed. Limit is maybe reached")
            return False

    @staticmethod
    def get_tweet(tweet):
        print(tweet)
        x, y = tweet.coordinates['coordinates']  # get coordinates from the tweet
        plt.plot(x, y, 'ro', markersize=2)  # plot the red dot on the map
        plt.pause(0.01)  # little trick to update the map

    @staticmethod
    def get_axis_limits(axes, scale_x=1.02, scale_y=1.03):
        return axes.get_xlim()[0] * scale_x, (axes.get_ylim()[0] * scale_y)


if __name__ == '__main__':

    # ------------------------------------------------------------------
    # MAP
    # ------------------------------------------------------------------

    # Japan coordinates
    japan_extent = [122.372118838, 150.0007330301, 29.9785169793, 42.4539733251]

    # Create a Stamen terrain background instance.
    stamen_terrain = cimgt.Stamen('watercolor')

    # Define map size and dpi
    fig = plt.figure(figsize=(9, 5), dpi=150)

    # Create a GeoAxes in the tile's projection.
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Limit the extent of the map to a small longitude/latitude range.
    ax.set_extent(japan_extent, crs=ccrs.PlateCarree())

    # Add the Stamen data at zoom level 6.
    ax.add_image(stamen_terrain, 6)

    # ------------------------------------------------------------------
    # TWEEPY
    # ------------------------------------------------------------------

    # Get access and key from another class
    auth = authentication()

    consumer_key = auth.getconsumer_key()
    consumer_secret = auth.getconsumer_secret()

    access_token = auth.getaccess_token()
    access_token_secret = auth.getaccess_token_secret()

    # Authentication
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.secure = True
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth,
                     wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True,
                     retry_count=10,
                     retry_delay=5,
                     retry_errors={401, 404, 500, 503}
                     )

    streamListener = TwitterStreamListener()

    myStream = tweepy.Stream(auth=api.auth,
                             listener=streamListener
                             )

    japan_location_coord = [122.372118838, 29.9785169793, 150.0007330301, 42.4539733251]

    myStream.filter(locations=japan_location_coord)
