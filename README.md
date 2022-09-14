# slack-downloader

`slack-downloader` is a tool to download/backup [Slack](https://slack.com) files on a local disk.

The program will download latest files uploaded on Slack, on a configured directory.
History of already downloaded files is mantained, in order to avoid duplicate downloads.

Files will be organized inside of a specified directory, with the following form:

```
<channel_name>/<date>-<filename>_by_<user/uploader>.<ext>
```

where `<date>` has the form `%Y%m%d_%H%M%S`.

This project is a fork of [marek/fslack](https://github.com/marek/fslack), used for a different purpose.

### Requirements

* `Slack API Token`: Get it from (https://api.slack.com/web)
* `Python`: The app is written in Python
* `python-requests`: web request library for Python


### Setting up API Access to your Slack Workspace

In order to get your token, you will have to create a new Slack App. You can follow [this tutorial](https://api.slack.com/tutorials/tracks/getting-a-token).

You can create a new app by going to https://api.slack.com/apps and clicking on the `"Create New App"` button.

When you click on the `"Create New App"` button, you will be given the following 2 options:

1. Create an app from scratch
2. Create an app from an app manifest

Select "Create an app from an app manifest" and then copy and paste the text in [slack-app-manifest.yaml](slack-app-manifest.yaml)

This will create an app with permission to read all data in your Slack workspace. It won't have any write permissions.

Once you have created the app, you have to install it in your workspace. 

Now - to get the token, go to the `OAuth & Permissions` section in the app settings. Then in the `OAuth Tokens for Your Workspace` section, copy the `Bot User OAuth Token`.

To access app `OAuth & Permissions` settings, you can navigate directly to `https://api.slack.com/apps/<app_id>/oauth?`

Finally, invite the App's bot into the channels from which you want to download the files.

To invite the bot, use `/invite @your-app-name` e.g. `/invite @Slack Data Downloader` as discussed in [this question](https://stackoverflow.com/a/61369364/8691571)


### Installation Instructions

1. Download the Python program:

   ```
   wget https://raw.githubusercontent.com/auino/slack-downloader/master/slack-downloader.py
   chmod +x slack-downloader.py
   ```

2. Open the `slack-downloader.py` script with a text editor and configure it using a [legacy token](https://api.slack.com/custom-integrations/legacy-tokens)
3. Optionally, you can add the program to your `crontab` to automatically check for new shared items on Slack:

   ```
   crontab -e
   ```

4. Now you have to append the following line (press `i` button to insert data):

   ```
   0 * * * * python /directory_path/slack-downloader.py
   ```

   where `/directory_path/` identifies the path of the directory containing the script, while `0 *` specifies the program has to be called every hour.
5. Hit `:q` to close, saving the file
6. Enjoy!

### Supporters ###

 * [kylevedder](https://github.com/kylevedder) for multiple fixes
 * [nalt](https://github.com/nalt) for the fix on file downloads
 * [paloha](https://github.com/paloha) for resolving API incompatibilities and other fixes

### Contacts ###

You can find me on Twitter as [@auino](https://twitter.com/auino).
