#!/bin/sh
# Change these values to the ones used to create the App Service.
RESOURCE_GROUP_NAME='cloudcomputing'
APP_SERVICE_NAME='cloudcomputers'
ZIP_FILE_NAME='sitebuild.zip'

zip -r $ZIP_FILE_NAME . -x '.??*'


az webapp deploy \
    --name $APP_SERVICE_NAME \
    --resource-group $RESOURCE_GROUP_NAME \
    --src-path $ZIP_FILE_NAME
