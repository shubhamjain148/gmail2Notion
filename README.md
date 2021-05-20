<div align="center">

## Port emails from gmail to Notion

</div>

Get your emails from gmail which have specific labels into notion and create a reading list out of your newsletter, subscriptions and other things.

## How to use

- To get started, first create a filter for the emails which you want to move and add specific labels to emails in those filters

- Update lableMappings in `readEmail.py` to reflect your labels list as keys to that object and the value of the key will be with what name you want to store this into gmail

- run the script and your emails are in Notion

## Setting up Notion and Secret

[Follow these steps](https://developers.notion.com/docs) to get your database id and notion secret integration key

Along with name column have another select column names as `from` where the value from labelMappings will be stored

- Add your databaseId in place of `defaultDatabaseId` in `addToNotion.py`
- Add your secret integration key in place of `integrationKey` in `addToNotion.py`
