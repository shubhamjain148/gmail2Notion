<div align="center">

## Port emails from gmail to Notion

</div>

Get your emails from gmail which have specific labels into notion and create a reading list out of your newsletters, subscriptions and other things.

## Before using

The project uses [simplegmail](https://github.com/jeremyephron/simplegmail) to connect to your gmail account.

Follow the [getting started](https://github.com/jeremyephron/simplegmail#getting-started) section of that repo to setup connection with gmail.

> **NOTE:** Make sure you create a Desktop Client for Google OAuth so you don't have to add
> a redirect URL

## Setting up Notion and Secret

[Follow these steps](https://developers.notion.com/docs) to get your database id and notion secret integration key

- Along with name column create another column named as `From` which is of select type and prepopulate it with some values which you want to store so that you know from whom the email is like `x`, `y` and `z`
- Add your databaseId in place of `defaultDatabaseId` in `addToNotion.py`
- Add your secret integration key in place of `integrationKey` in `addToNotion.py`

## How to use the script

1. To get started, first create a filter for the emails which you want to move and add specific labels to emails in those filters

2. Update `labelMappings.json` file to reflect your labels list as keys to that object and the value of the key will be with what name you want to store this into gmail.

```json
{
  "label1": "x",
  "label2": "y"
}
```

So if your `labelMappings.json` file looks like this so the script will read all you emails marked with `label1` and `label2` and store it in notion database by populating From table value as `x` and `y` respective.

> **NOTES:** `x` and `y` are should be some prepopulated values in `From` select column as mentioned in [How to setup Notion section](#Setting-up-Notion-and-Secret)

3.  run the script and your emails are in Notion
